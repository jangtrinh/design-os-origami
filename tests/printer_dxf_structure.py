"""Independent stdlib checks for the printer's minimal R2000 database."""
import math

TABLE_SUBCLASSES = {
    'LTYPE': 'AcDbLinetypeTableRecord', 'LAYER': 'AcDbLayerTableRecord',
    'STYLE': 'AcDbTextStyleTableRecord', 'APPID': 'AcDbRegAppTableRecord',
    'DIMSTYLE': 'AcDbDimStyleTableRecord', 'BLOCK_RECORD': 'AcDbBlockTableRecord',
}
TABLE_NAMES = ['VPORT', 'LTYPE', 'LAYER', 'STYLE', 'VIEW', 'UCS', 'APPID',
               'DIMSTYLE', 'BLOCK_RECORD']


def tags(text):
    lines = text.splitlines()
    assert len(lines) % 2 == 0, 'Unpaired DXF tag'
    return [(int(c), v) for c, v in zip(lines[::2], lines[1::2])]


def dump(pairs):
    return ''.join(f'{c}\n{v}\n' for c, v in pairs)


def values(record, code):
    return [v for c, v in record if c == code]


def one(record, code):
    found = values(record, code)
    assert len(found) == 1, f'Expected one group {code}'
    return found[0]


def records(pairs):
    result = []
    for pair in pairs:
        if pair[0] == 0:
            result.append([])
        assert result, 'Missing record marker'
        result[-1].append(pair)
    return result


def validate(text, names):
    pairs = tags(text)
    assert pairs[-1:] == [(0, 'EOF')], 'Missing EOF'
    sections, i = {}, 0
    while i < len(pairs)-1:
        assert pairs[i] == (0, 'SECTION'), 'Missing SECTION'
        assert pairs[i+1][0] == 2, 'Missing section name'
        name = pairs[i+1][1]
        assert name not in sections, 'Duplicate section'
        end = pairs.index((0, 'ENDSEC'), i+2)
        assert (0, 'SECTION') not in pairs[i+2:end], 'Unbalanced section'
        sections[name] = pairs[i+2:end]
        i = end+1
    assert list(sections) == ['HEADER', 'CLASSES', 'TABLES', 'BLOCKS',
                              'ENTITIES', 'OBJECTS'], 'Required sections'
    header = sections['HEADER']
    for variable, value in [('$ACADVER', (1, 'AC1015')), ('$INSUNITS', (70, '4')),
                            ('$MEASUREMENT', (70, '1'))]:
        assert header[header.index((9, variable))+1] == value, variable
    seed_code, seed = header[header.index((9, '$HANDSEED'))+1]
    assert seed_code == 5, 'HANDSEED group'
    objects = []
    tables, table = {}, None
    for record in records(sections['TABLES']):
        kind = one(record, 0)
        if kind == 'TABLE':
            assert table is None, 'Nested table'
            table = one(record, 2)
            assert table not in tables, 'Duplicate table'
            tables[table] = [record]
            assert one(record, 330) == '0', 'Table owner'
            assert values(record, 100)[:1] == ['AcDbSymbolTable'], 'Table subclass'
            assert record.index((2, table)) < record.index((100, 'AcDbSymbolTable')), 'Table tag order'
            if table == 'DIMSTYLE':
                assert 'AcDbDimStyleTable' in values(record, 100), 'DIMSTYLE table subclass'
            objects.append(record)
        elif kind == 'ENDTAB':
            assert table is not None, 'Unbalanced ENDTAB'
            assert int(one(tables[table][0], 70)) >= len(tables[table])-1, 'Table count'
            table = None
        else:
            assert table == kind, 'Record outside its table'
            assert values(record, 100) == ['AcDbSymbolTableRecord', TABLE_SUBCLASSES[kind]], 'Record subclasses'
            assert one(record, 330) == one(tables[table][0], 5), 'Record table owner'
            tables[table].append(record)
            objects.append(record)
    assert table is None, 'Missing ENDTAB'
    assert list(tables) == TABLE_NAMES, 'Required tables/order'
    required = {'LTYPE': {'BYBLOCK', 'BYLAYER', 'CONTINUOUS'},
                'LAYER': {'0', *names.values()}, 'STYLE': {'STANDARD'},
                'APPID': {'ACAD'}, 'DIMSTYLE': {'STANDARD'},
                'BLOCK_RECORD': {'*Model_Space', '*Paper_Space'}}
    for kind, expected in required.items():
        actual = [one(r, 2) for r in tables[kind][1:]]
        assert len(actual) == len(set(actual)), 'Duplicate table record'
        assert set(actual) == expected, f'Required {kind} records'
    blocks = {one(r, 2): r for r in tables['BLOCK_RECORD'][1:]}
    block_entities = records(sections['BLOCKS'])
    assert [one(r, 0) for r in block_entities] == ['BLOCK', 'ENDBLK']*2, 'Block pairs'
    for offset, name in enumerate(['*Model_Space', '*Paper_Space']):
        begin, end = block_entities[offset*2:offset*2+2]
        assert one(begin, 2) == one(begin, 3) == name, 'Block name'
        for record, subclass in [(begin, 'AcDbBlockBegin'), (end, 'AcDbBlockEnd')]:
            assert values(record, 100) == ['AcDbEntity', subclass], 'Block subclass'
            assert one(record, 330) == one(blocks[name], 5), 'Block owner'
    entities = records(sections['ENTITIES'])
    for record in entities:
        assert one(record, 0) == 'LWPOLYLINE', 'Unexpected geometry'
        assert values(record, 100) == ['AcDbEntity', 'AcDbPolyline'], 'Polyline subclass'
        assert one(record, 330) == one(blocks['*Model_Space'], 5), 'Polyline owner'
        assert one(record, 8) in names.values(), 'Unknown spot layer'
        assert int(one(record, 90)) == len(values(record, 10)) == len(values(record, 20)), 'Vertex count'
        assert one(record, 70) in ['0', '1'], 'Closure flag'
        assert all(math.isfinite(float(v)) for c, v in record if c in [10, 20]), 'Coordinates'
        if one(record, 70) == '1':
            assert int(one(record, 90)) >= 3, 'Closed contour vertex count'
    assert any(one(e, 8) == names['cut'] and one(e, 70) == '1'
               for e in entities), 'Missing closed CUT contour'
    database = records(sections['OBJECTS'])
    root = database[0]
    assert one(root, 0) == 'DICTIONARY' and one(root, 330) == '0', 'Root dictionary'
    entries = dict(zip(values(root, 3), values(root, 350)))
    assert set(entries) == {'ACAD_GROUP', 'ACAD_LAYOUT'}, 'Root dictionary entries'
    objects += block_entities + entities + database
    handles = [one(r, 105 if one(r, 0) == 'DIMSTYLE' else 5) for r in objects]
    numeric = [int(h, 16) for h in handles]
    assert min(numeric) > 0 and len(set(numeric)) == len(numeric), 'Duplicate/zero handles'
    assert int(seed, 16) > max(numeric), 'Low HANDSEED'
    by_handle = dict(zip(handles, objects))
    for record in objects:
        assert values(record, 330), 'Missing owner'
        for c, handle in record:
            if (330 <= c <= 369 or c in [390, 480, 481, 1005]) and handle != '0':
                assert handle in by_handle, 'Dangling handle reference'
        if one(record, 0) == 'DICTIONARY':
            assert values(record, 100) == ['AcDbDictionary'], 'Dictionary subclass'
    group, layout_dict = [by_handle[entries[k]] for k in ['ACAD_GROUP', 'ACAD_LAYOUT']]
    for dictionary in [group, layout_dict]:
        assert one(dictionary, 0) == 'DICTIONARY', 'Dictionary target'
        assert one(dictionary, 330) == one(root, 5), 'Dictionary owner'
    layouts = dict(zip(values(layout_dict, 3), values(layout_dict, 350)))
    assert set(layouts) == {'Model', 'Layout1'}, 'Required layouts'
    for dimstyle in tables['DIMSTYLE'][1:]:
        assert one(by_handle[one(dimstyle, 340)], 0) == 'STYLE', 'DIMSTYLE text style'
    for name, block_name in [('Model', '*Model_Space'), ('Layout1', '*Paper_Space')]:
        layout = by_handle[layouts[name]]
        assert one(layout, 0) == 'LAYOUT', 'Layout target'
        assert values(layout, 100) == ['AcDbPlotSettings', 'AcDbLayout'], 'Layout subclasses'
        assert values(layout, 1)[-1] == name, 'Layout name'
        assert values(layout, 330) == [one(layout_dict, 5), one(layout_dict, 5),
                                      one(blocks[block_name], 5)], 'Layout references'
        assert one(blocks[block_name], 340) == one(layout, 5), 'Reciprocal layout pointer'
    return sections, tables, entities
