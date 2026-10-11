"""Experimental packaging dieline SVG and DXF interchange exporters."""

from pathlib import Path
from typing import Dict
from origami_cad.geometry import OrigamiCreasePattern, CreaseType


def export_svg(cp: OrigamiCreasePattern, output_path: str, margin_mm: float = 15.0) -> str:
    """
    Exports a presentation SVG using local CUT/CREASE/PERFORATE/GLUE groups.
    Mountain/valley folds retain direction in data-fold attributes on CREASE lines.
    Display styling is not a recipient-approved prepress or machine profile.
    """
    min_x, min_y, max_x, max_y = cp.bounding_box()
    width = (max_x - min_x) + 2 * margin_mm
    height = (max_y - min_y) + 2 * margin_mm

    offset_x = margin_mm - min_x
    offset_y = margin_mm - min_y

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} {height:.2f}" width="{width:.2f}mm" height="{height:.2f}mm" style="background:#FFFFFF;">',
        f'  <defs>',
        f'    <style>',
        f'      .cut {{ stroke: #FF0000; stroke-width: 1.2; fill: none; stroke-linecap: round; }}',
        f'      .crease {{ stroke: #00FF00; stroke-width: 1.0; stroke-dasharray: 4, 3; fill: none; }}',
        f'      .perf {{ stroke: #0000FF; stroke-width: 1.0; stroke-dasharray: 2, 2; fill: none; }}',
        f'      .glue {{ stroke: #FF00FF; stroke-width: 1.2; stroke-dasharray: 1, 2; fill: none; }}',
        f'    </style>',
        f'  </defs>',
        f'  <g id="DIELINE_LAYER">',
    ]

    # Group creases by type
    by_type: Dict[CreaseType, list] = {t: [] for t in CreaseType}
    for c in cp.creases:
        by_type[c.crease_type].append(c)

    # 1. Crease group
    svg_lines.append('    <g id="CREASE" class="crease">')
    for c in by_type[CreaseType.CREASE] + by_type[CreaseType.MOUNTAIN] + by_type[CreaseType.VALLEY]:
        x1 = c.p1.x + offset_x
        y1 = c.p1.y + offset_y
        x2 = c.p2.x + offset_x
        y2 = c.p2.y + offset_y
        fold_attr = (f' data-fold="{c.crease_type.value.lower()}"'
                     if c.crease_type in (CreaseType.MOUNTAIN, CreaseType.VALLEY) else "")
        svg_lines.append(f'      <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"{fold_attr}/>')
    svg_lines.append('    </g>')

    # 2. Glue group
    svg_lines.append('    <g id="GLUE" class="glue">')
    for c in by_type[CreaseType.GLUE]:
        x1 = c.p1.x + offset_x
        y1 = c.p1.y + offset_y
        x2 = c.p2.x + offset_x
        y2 = c.p2.y + offset_y
        svg_lines.append(f'      <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    svg_lines.append('    </g>')

    # 3. Cut group
    svg_lines.append('    <g id="CUT" class="cut">')
    for c in by_type[CreaseType.CUT]:
        x1 = c.p1.x + offset_x
        y1 = c.p1.y + offset_y
        x2 = c.p2.x + offset_x
        y2 = c.p2.y + offset_y
        svg_lines.append(f'      <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    svg_lines.append('    </g>')

    # 4. Perforation group
    svg_lines.append('    <g id="PERFORATE" class="perf">')
    for c in by_type[CreaseType.PERFORATE]:
        x1 = c.p1.x + offset_x
        y1 = c.p1.y + offset_y
        x2 = c.p2.x + offset_x
        y2 = c.p2.y + offset_y
        svg_lines.append(f'      <line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}"/>')
    svg_lines.append('    </g>')

    svg_lines.append('  </g>')
    svg_lines.append('</svg>')

    content = "\n".join(svg_lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(content, encoding="utf-8")
    return content


def export_dxf(cp: OrigamiCreasePattern, output_path: str) -> str:
    """
    Exports an AutoCAD R12 ASCII DXF file with local packaging layers:
    - Layer CUT: Color 1 (Red)
    - Layer CREASE: Color 3 (Green)
    - Layer PERFORATE: Color 5 (Blue)
    - Layer GLUE: Color 6 (Magenta)
    Mountain/valley direction is lost in CREASE; units and orientation require
    a recipient agreement. SVG retains direction metadata when it is needed.
    """
    layer_map = {
        CreaseType.CUT: ("CUT", 1),
        CreaseType.CREASE: ("CREASE", 3),
        CreaseType.MOUNTAIN: ("CREASE", 3),
        CreaseType.VALLEY: ("CREASE", 3),
        CreaseType.PERFORATE: ("PERFORATE", 5),
        CreaseType.GLUE: ("GLUE", 6),
    }

    dxf_lines = [
        "0", "SECTION",
        "2", "HEADER",
        "9", "$ACADVER",
        "1", "AC1009",  # AutoCAD R12 DXF
        "0", "ENDSEC",
        "0", "SECTION",
        "2", "TABLES",
        "0", "TABLE",
        "2", "LAYER",
        "70", "4",
    ]

    # Declare layers
    declared = set()
    for layer_name, color_idx in layer_map.values():
        if layer_name not in declared:
            declared.add(layer_name)
            dxf_lines.extend([
                "0", "LAYER",
                "2", layer_name,
                "70", "0",
                "62", str(color_idx),
                "6", "CONTINUOUS",
            ])

    dxf_lines.extend([
        "0", "ENDTAB",
        "0", "ENDSEC",
        "0", "SECTION",
        "2", "ENTITIES",
    ])

    for c in cp.creases:
        layer_name, _ = layer_map.get(c.crease_type, ("CUT", 1))
        dxf_lines.extend([
            "0", "LINE",
            "8", layer_name,
            "10", f"{c.p1.x:.4f}",
            "20", f"{c.p1.y:.4f}",
            "30", "0.0",
            "11", f"{c.p2.x:.4f}",
            "21", f"{c.p2.y:.4f}",
            "31", "0.0",
        ])

    dxf_lines.extend([
        "0", "ENDSEC",
        "0", "EOF",
    ])

    content = "\n".join(dxf_lines)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text(content, encoding="utf-8")
    return content
