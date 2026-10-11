"""Additive printer profile: vector spot PDF and millimetre/y-up DXF."""
import math
import re
from pathlib import Path
from origami_cad.printer_paths import with_bleed

PT_PER_MM = 72/25.4
DEFAULT_SPOTS = {'cut': 'CutContour', 'crease': 'CreaseLine', 'perforation': 'Perforation',
                 'bleed': 'Bleed', 'glue': 'GlueArea'}
RESERVED_COLORANTS = {'none', 'all', 'cyan', 'magenta', 'yellow', 'black'}
COLORS = {'cut': (0, 1, 1, 0), 'crease': (1, 0, 1, 0), 'perforation': (1, 1, 0, 0),
          'bleed': (0, 0, 1, 0), 'glue': (0, 1, 0, 0)}


def resolve_spots(overrides=None):
    names = DEFAULT_SPOTS | (overrides or {})
    if set(names) != set(DEFAULT_SPOTS):
        raise ValueError('Unknown spot line type')
    if any(not isinstance(n, str) or not re.fullmatch(r'[A-Za-z][A-Za-z0-9 _.\-]{0,63}', n) for n in names.values()):
        raise ValueError('Spot names: 1-64 ASCII letters, digits, spaces, underscores, dots or hyphens; letter first')
    if any(n.strip().casefold() in RESERVED_COLORANTS for n in names.values()):
        raise ValueError('Spot colorant name is reserved: None, All, Cyan, Magenta, Yellow or Black')
    if len({n.casefold() for n in names.values()}) != 5:
        raise ValueError('Each line type requires a unique spot name')
    return names


def pdf_name(name):
    return ''.join(c if c.isalnum() or c in '_.-' else f'#{ord(c):02X}' for c in name)


def pdf_document(objects):
    """Write uncompressed PDF objects with byte-exact xref and stream lengths."""
    data, offsets = bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'), [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(data))
        data.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
    start = len(data)
    data.extend(f'xref\n0 {len(offsets)}\n0000000000 65535 f \n'.encode())
    for offset in offsets[1:]:
        data.extend(f'{offset:010d} 00000 n \n'.encode())
    data.extend(f'trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode())
    return bytes(data)


def export_printer_pdf(cp, output_path, bleed_mm=3.0, spot_names=None):
    names = resolve_spots(spot_names)
    paths = with_bleed(cp, bleed_mm)
    all_points = [p for rows in paths.values() for pts, _ in rows for p in pts]
    min_x, min_y = min(p.x for p in all_points), min(p.y for p in all_points)
    max_x, max_y = max(p.x for p in all_points), max(p.y for p in all_points)
    margin, legend = 5.0, 24.0
    width = max(max_x-min_x+2*margin, 20+max(map(len,names.values()))*8*0.6/PT_PER_MM)
    height = max_y-min_y+2*margin+legend
    x_shift, y_shift = (margin-min_x)*PT_PER_MM, (margin+legend+max_y)*PT_PER_MM
    if not all(math.isfinite(v) for v in (width*PT_PER_MM,height*PT_PER_MM,x_shift,y_shift)):
        raise ValueError('PDF page arithmetic overflow')
    # Coordinates in points preserve a unit PDF CTM and an exact1pt stroke.
    content = ['1 w']
    for i, kind in enumerate(DEFAULT_SPOTS):
        content.append(f'/S{i} CS 1 SCN')
        for points, closed in paths[kind]:
            for j, p in enumerate(points):
                content.append(f'{p.x*PT_PER_MM+x_shift:.8f} {-p.y*PT_PER_MM+y_shift:.8f} '+('m' if j==0 else 'l'))
            if closed: content.append('h')
            content.append('S')
    # Legend is below the bleed-inclusive die; all five resources are used even when a type has no path.
    for i, (kind, name) in enumerate(names.items()):
        y = (5+i*4)*PT_PER_MM
        content.extend([f'/S{i} CS 1 SCN', f'{5*PT_PER_MM:.8f} {y:.8f} m {12*PT_PER_MM:.8f} {y:.8f} l S',
                        f'BT /F1 8 Tf 1 0 0 1 {15*PT_PER_MM:.8f} {y-2:.8f} Tm ({name}) Tj ET'])
    stream = ('\n'.join(content)+'\n').encode('ascii')
    resources = ' '.join(f'/S{i} {6+i} 0 R' for i in range(5))
    objects = [b'<< /Type /Catalog /Pages 2 0 R >>', b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',
               (f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width*PT_PER_MM:.8f} {height*PT_PER_MM:.8f}] '
                f'/Resources << /ColorSpace << {resources} >> /Font << /F1 5 0 R >> >> /Contents 4 0 R >>').encode(),
               f'<< /Length {len(stream)} >>\nstream\n'.encode()+stream+b'endstream',
               b'<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>']
    for kind, name in names.items():
        cmyk = ' '.join(map(str,COLORS[kind]))
        objects.append((f'[/Separation /{pdf_name(name)} /DeviceCMYK << /FunctionType 2 /Domain [0 1] '
                        f'/C0 [0 0 0 0] /C1 [{cmyk}] /N 1 >>]').encode())
    data = pdf_document(objects)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_bytes(data)
    return data


def export_printer_dxf(cp, output_path, bleed_mm=3.0, spot_names=None):
    names = resolve_spots(spot_names)
    paths = with_bleed(cp, bleed_mm)
    from origami_cad.printer_r2000 import r2000_document
    text = r2000_document(paths, names)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(text, encoding='ascii')
    return text
