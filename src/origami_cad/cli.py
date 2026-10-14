"""Command Line Interface for origami-cad."""

import argparse
from pathlib import Path
import sys

from origami_cad.packaging import generate_miura_ori_sleeve
from origami_cad.product_registry import product_blanks
from origami_cad.figurative import generate_deer_bird_base
from origami_cad.dieline_export import export_svg, export_dxf
from origami_cad.viewer_html import generate_viewer_html


def create_parser():
    parser = argparse.ArgumentParser(description="DESIGN:OS Origami CAD & Packaging Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: generate
    gen_p = subparsers.add_parser("generate", help="Generate packaging dieline and 3D folding viewer")
    gen_p.add_argument("--type", choices=["tuck-box", "miura-ori", "hex-petal", "diamond-box", "zero-glue-tray", "gable-box", "pillow-box", "crash-lock-box", "fefco-0201", "fefco-0427", "sleeve-tray", "food-box", "deer-base"], default="tuck-box", help="Pattern type")
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

    return parser


def generate_blanks(args):
    """One reusable dispatch boundary; preserves the original CLI defaults."""
    if args.type == "deer-base":
        return (generate_deer_bird_base(size=args.width if args.width is not None else 200.0),)
    if args.type == "miura-ori":
        return (generate_miura_ori_sleeve(),)
    return product_blanks(args.type, width=50.0 if args.type == "diamond-box" and args.width is None else args.width,
                          depth=args.depth, height=args.height, radius=args.radius, thickness=args.thickness)


def main():
    parser = create_parser()
    args = parser.parse_args()

    try:
        blanks = generate_blanks(args)
    except ValueError as error:
        parser.error(str(error))
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for cp in blanks:
        _export_blank(cp, args, out_dir, parser)


def _export_blank(cp, args, out_dir, parser):
    """Export each physical blank independently; a two-piece product never overlaps nets."""

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
