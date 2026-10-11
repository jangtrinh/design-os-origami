"""Minimal R2000 database for connected printer paths; caller owns file I/O."""

KINDS = ('cut', 'crease', 'perforation', 'bleed', 'glue')
TABLES = ('VPORT', 'LTYPE', 'LAYER', 'STYLE', 'VIEW', 'UCS', 'APPID',
          'DIMSTYLE', 'BLOCK_RECORD')


def r2000_document(paths, names):
    """Serialize validated source-mm paths in y-up coordinates without changing them.

    Database objects follow Autodesk's DXF symbol-table reference and ezdxf's
    minimal-content/layout-management contracts. Handles share one namespace.
    """
    rows, next_handle = [], 1

    def allocate():
        nonlocal next_handle
        value = f'{next_handle:X}'
        next_handle += 1
        return value

    def emit(*pairs):
        for code, value in pairs:
            rows.extend((str(code), str(value)))

    def section(name):
        emit((0, 'SECTION'), (2, name))

    def obj(kind, owner, subclasses, handle=None, handle_code=5):
        handle = allocate() if handle is None else handle
        emit((0, kind), (handle_code, handle), (330, owner))
        for subclass in subclasses:
            emit((100, subclass))
        return handle

    table_handles = {name: allocate() for name in TABLES}
    block_handles = {name: allocate() for name in ('*Model_Space', '*Paper_Space')}
    root, group, layout_dict = allocate(), allocate(), allocate()
    layout_handles = {name: allocate() for name in ('Model', 'Layout1')}
    section('HEADER')
    emit((9, '$ACADVER'), (1, 'AC1015'), (9, '$HANDSEED'))
    seed_index = len(rows)+1
    emit((5, ''), (9, '$INSUNITS'), (70, 4), (9, '$MEASUREMENT'), (70, 1),
         (0, 'ENDSEC'))
    section('CLASSES')
    emit((0, 'CLASS'), (1, 'LAYOUT'), (2, 'AcDbLayout'), (3, 'ObjectDBX Classes'),
         (90, 0), (280, 0), (281, 0), (0, 'ENDSEC'))
    section('TABLES')
    counts = {'LTYPE': 3, 'LAYER': 6, 'STYLE': 1, 'APPID': 1,
              'DIMSTYLE': 1, 'BLOCK_RECORD': 2}
    style_handle = None
    for table in TABLES:
        owner = table_handles[table]
        emit((0, 'TABLE'), (2, table), (5, owner), (330, '0'),
             (100, 'AcDbSymbolTable'), (70, counts.get(table, 0)))
        if table == 'DIMSTYLE':
            emit((100, 'AcDbDimStyleTable'), (71, 1))

        def record(name, subclass, handle=None, handle_code=5):
            value = obj(table, owner, ['AcDbSymbolTableRecord', subclass],
                        handle, handle_code)
            emit((2, name), (70, 0))
            return value

        if table == 'LTYPE':
            for name in ('BYBLOCK', 'BYLAYER', 'CONTINUOUS'):
                record(name, 'AcDbLinetypeTableRecord')
                emit((3, 'Solid line' if name == 'CONTINUOUS' else ''),
                     (72, 65), (73, 0), (40, 0))
        elif table == 'LAYER':
            for name, color in [('0', 7)] + [(names[k], c) for k, c in zip(KINDS, (1, 3, 5, 2, 6))]:
                record(name, 'AcDbLayerTableRecord')
                emit((62, color), (6, 'CONTINUOUS'))
        elif table == 'STYLE':
            style_handle = record('STANDARD', 'AcDbTextStyleTableRecord')
            emit((40, 0), (41, 1), (50, 0), (71, 0), (42, 1), (3, 'txt'), (4, ''))
        elif table == 'APPID':
            record('ACAD', 'AcDbRegAppTableRecord')
        elif table == 'DIMSTYLE':
            record('STANDARD', 'AcDbDimStyleTableRecord', handle_code=105)
            emit((40, 1), (41, 2.5), (140, 2.5), (340, style_handle))
        elif table == 'BLOCK_RECORD':
            for block, layout in zip(block_handles, layout_handles):
                # Units/explodability/scalability tags 70/280/281 are R2007+.
                obj('BLOCK_RECORD', owner, ['AcDbSymbolTableRecord', 'AcDbBlockTableRecord'],
                    block_handles[block])
                emit((2, block), (340, layout_handles[layout]))
        emit((0, 'ENDTAB'))
    emit((0, 'ENDSEC'))
    section('BLOCKS')
    for name, owner in block_handles.items():
        obj('BLOCK', owner, ['AcDbEntity'])
        emit((8, '0'), (100, 'AcDbBlockBegin'), (2, name), (70, 0),
             (10, 0), (20, 0), (30, 0), (3, name), (1, ''))
        obj('ENDBLK', owner, ['AcDbEntity'])
        emit((8, '0'), (100, 'AcDbBlockEnd'))
    emit((0, 'ENDSEC'))
    section('ENTITIES')
    for kind in KINDS:
        for points, closed in paths[kind]:
            obj('LWPOLYLINE', block_handles['*Model_Space'], ['AcDbEntity'])
            emit((8, names[kind]), (100, 'AcDbPolyline'),
                 (90, len(points)), (70, int(closed)))
            for point in points:
                emit((10, f'{point.x:.8f}'), (20, f'{-point.y:.8f}'))
    emit((0, 'ENDSEC'))
    section('OBJECTS')
    obj('DICTIONARY', '0', ['AcDbDictionary'], root)
    emit((281, 1), (3, 'ACAD_GROUP'), (350, group), (3, 'ACAD_LAYOUT'), (350, layout_dict))
    obj('DICTIONARY', root, ['AcDbDictionary'], group)
    emit((281, 1))
    obj('DICTIONARY', root, ['AcDbDictionary'], layout_dict)
    emit((281, 1))
    for name, handle in layout_handles.items():
        emit((3, name), (350, handle))
    points = [p for kind in KINDS for pts, _ in paths[kind] for p in pts]
    minimum = (min((p.x for p in points), default=0), min((-p.y for p in points), default=0))
    maximum = (max((p.x for p in points), default=0), max((-p.y for p in points), default=0))
    for index, (name, block) in enumerate(zip(layout_handles, block_handles)):
        obj('LAYOUT', layout_dict, [], layout_handles[name])
        emit((102, '{ACAD_REACTORS'), (330, layout_dict), (102, '}'),
             (100, 'AcDbPlotSettings'), (1, ''), (4, ''), (6, ''))
        emit(*[(c, 0) for c in range(40, 44)],
             (44, maximum[0]-minimum[0]), (45, maximum[1]-minimum[1]),
             *[(c, 0) for c in (46, 47, 48, 49, 140, 141)], (142, 1), (143, 1),
             (70, 1712 if index == 0 else 688), (72, 1), (73, 0), (74, 1),
             (7, ''), (75, 16), (147, 1), (148, 0), (149, 0),
             (100, 'AcDbLayout'), (1, name), (70, 1), (71, index),
             (10, minimum[0]), (20, minimum[1]), (11, maximum[0]), (21, maximum[1]))
        for xcode, xyz in [(12, (0, 0, 0)), (14, (*minimum, 0)), (15, (*maximum, 0)),
                           (13, (0, 0, 0)), (16, (1, 0, 0)), (17, (0, 1, 0))]:
            emit(*[(xcode+offset, v) for offset, v in zip((0, 10, 20), xyz)])
        emit((146, 0), (76, 0), (330, block_handles[block]))
    emit((0, 'ENDSEC'), (0, 'EOF'))
    rows[seed_index] = f'{next_handle:X}'
    return '\n'.join(rows)+'\n'
