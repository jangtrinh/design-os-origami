"""Command Line Interface for origami-cad."""

import argparse
from pathlib import Path
import sys

from origami_cad.packaging import (
    generate_tuck_box,
    generate_miura_ori_sleeve,
    generate_hexagonal_petal_box,
    generate_diamond_faceted_box,
    generate_zero_glue_tray,
    generate_gable_handle_box,
    generate_pillow_box,
    generate_crash_lock_box,
)
from origami_cad.figurative import generate_deer_bird_base
from origami_cad.dieline_export import export_svg, export_dxf
from origami_cad.viewer_html import generate_viewer_html


def main():
    parser = argparse.ArgumentParser(description="DESIGN:OS Origami CAD & Packaging Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: generate
    gen_p = subparsers.add_parser("generate", help="Generate packaging dieline and 3D folding viewer")
    gen_p.add_argument("--type", choices=["tuck-box", "miura-ori", "hex-petal", "diamond-box", "zero-glue-tray", "gable-box", "pillow-box", "crash-lock-box", "deer-base"], default="tuck-box", help="Pattern type")
    gen_p.add_argument("--width", type=float, default=None, help="Width in mm (default depends on model)")
    gen_p.add_argument("--depth", type=float, default=None, help="Depth in mm (default depends on model)")
    gen_p.add_argument("--height", type=float, default=None, help="Height in mm; tray wall height (default depends on model)")
    gen_p.add_argument("--radius", type=float, default=40.0, help="Base radius in mm (for hex-petal)")
    gen_p.add_argument("--thickness", type=float, default=0.5, help="Paperboard caliper/thickness in mm")
    gen_p.add_argument("--output-dir", type=str, default="./output", help="Output directory")

    gen_p.add_argument("--profile", choices=["presentation", "printer"], default="presentation")
    gen_p.add_argument("--bleed-mm", type=float, default=3.0, help="Printer bleed outside CUT, in mm")
    for kind in ("cut", "crease", "perforation", "bleed", "glue"):
        gen_p.add_argument("--spot-" + kind, help="Printer spot/layer name override")

    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.type == "tuck-box":
        cp = generate_tuck_box(
            width=args.width if args.width is not None else 80.0,
            depth=args.depth if args.depth is not None else 50.0,
            height=args.height if args.height is not None else 120.0,
            thickness=args.thickness
        )
    elif args.type == "hex-petal":
        cp = generate_hexagonal_petal_box(
            radius=args.radius,
            height=args.height if args.height is not None else 55.0,
            thickness=args.thickness
        )
    elif args.type == "diamond-box":
        cp = generate_diamond_faceted_box(
            width=args.width if args.width is not None else 50.0,
            height=args.height if args.height is not None else 80.0,
            thickness=args.thickness
        )
    elif args.type == "zero-glue-tray":
        cp = generate_zero_glue_tray(
            width=args.width if args.width is not None else 100.0,
            depth=args.depth if args.depth is not None else 70.0,
            wall_height=args.height if args.height is not None else 30.0,
            thickness=args.thickness
        )
    elif args.type == "gable-box":
        cp = generate_gable_handle_box(
            width=args.width if args.width is not None else 160.0,
            depth=args.depth if args.depth is not None else 110.0,
            height=args.height if args.height is not None else 110.0,
            thickness=args.thickness
        )
    elif args.type == "pillow-box":
        cp = generate_pillow_box(
            width=args.width if args.width is not None else 90.0,
            depth=args.depth if args.depth is not None else 40.0,
            height=args.height if args.height is not None else 110.0,
            thickness=args.thickness
        )
    elif args.type == "crash-lock-box":
        cp = generate_crash_lock_box(
            width=args.width if args.width is not None else 80.0,
            depth=args.depth if args.depth is not None else 60.0,
            height=args.height if args.height is not None else 100.0,
            thickness=args.thickness
        )
    elif args.type == "deer-base":
        cp = generate_deer_bird_base(size=args.width if args.width is not None else 200.0)
    else:
        cp = generate_miura_ori_sleeve()

    if args.profile == "printer":
        from origami_cad.printer_profile_export import export_printer_pdf, export_printer_dxf
        names = {kind: getattr(args, "spot_"+kind) for kind in
                 ("cut", "crease", "perforation", "bleed", "glue") if getattr(args, "spot_"+kind) is not None}
        pdf = out_dir / f"{cp.name}_printer.pdf"
        dxf = out_dir / f"{cp.name}_printer.dxf"
        try:
            export_printer_pdf(cp, pdf, args.bleed_mm, names)
            export_printer_dxf(cp, dxf, args.bleed_mm, names)
        except ValueError as error:
            parser.error(str(error))
        print(f"[✓] Printer profile: {pdf}\n    - DXF mm/y-up: {dxf}")
        return

    svg_file = out_dir / f"{cp.name}.svg"
    dxf_file = out_dir / f"{cp.name}.dxf"
    html_file = out_dir / f"{cp.name}_viewer.html"

    export_svg(cp, str(svg_file))
    export_dxf(cp, str(dxf_file))
    generate_viewer_html(cp, str(html_file))

    print(f"[✓] Generated Origami CAD Model: {cp.name}")
    print(f"    - SVG 2D Dieline:  {svg_file}")
    print(f"    - DXF 2D CAD:      {dxf_file}")
    print(f"    - 3D Fold Viewer:  {html_file}")


if __name__ == "__main__":
    main()
