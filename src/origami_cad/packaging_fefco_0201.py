"""FEFCO 0201 regular slotted container: four walls, eight half-breadth flaps, joint flap.

Style source: FEFCO/ESBO International Fibreboard Case Code, style 0201 (slotted-type
box, one piece, glued/stitched/taped manufacturer's joint, top and bottom flaps; the
layout is drawn as joint flap, L, B, L, B with flaps of 1/2 B on every panel; internal
dimensions L x B x H). Fibre Box Association "Box Styles Basics" (2014): all flaps have
the same length and the outer flaps are one-half the container's width so they meet at
the centre. The code describes the style; dimensions, slot and joint sizes are parametric.
"""
from origami_cad.packaging_constraints import validate_glue_flap
from origami_cad.geometry import CreaseType, OrigamiCreasePattern, Point2D
from origami_cad.packaging_fefco_helpers import assemble_blank, rect, validate_box_inputs


def generate_fefco_0201(
    width: float = 200.0,
    depth: float = 150.0,
    height: float = 120.0,
    thickness: float = 0.5,
    joint_flap_width: float = 30.0,
    slot_width=None,
) -> OrigamiCreasePattern:
    """
    Parametric FEFCO 0201 blank. width = L (longer side at the opening), depth = B,
    height = H, all internal. Panel order L, B, L, B with the manufacturer's joint flap
    extending the first L panel. Flaps are B/2 deep on every panel; slots of slot_width
    (default 2 x caliper + 1 mm clearance, a converter choice rather than a FEFCO figure)
    are centred on the wall scores, with half slots at the glued corner. Wall panels carry
    the formula score allowance; the blank is viewed from the printed outside.
    """
    validate_box_inputs(width, depth, height, thickness)
    if width < depth:
        raise ValueError("FEFCO 0201 takes width as L, the longer side at the opening: width >= depth")
    cp = OrigamiCreasePattern(name=f"FEFCO0201_{int(width)}x{int(depth)}x{int(height)}",
                              thickness_mm=thickness)
    allowance = cp.calculate_score_allowance(90.0)
    length, breadth, h = width + allowance, depth + allowance, float(height)
    slot = 2.0 * thickness + 1.0 if slot_width is None else float(slot_width)
    if not 0 < slot < min(length, breadth):
        raise ValueError("slot width must be positive and narrower than every panel")
    validate_glue_flap(joint_flap_width, breadth, name="joint_flap_width")
    flap = breadth / 2.0
    chamfer = min(joint_flap_width / 2.0, h / 4.0)

    xs = [joint_flap_width]
    for span in (length, breadth, length, breadth):
        xs.append(xs[-1] + span)
    panel_names = ("WallL1", "WallB1", "WallL2", "WallB2")
    pieces = {"JointFlap": [(xs[0], 0.0), (0.0, chamfer), (0.0, h - chamfer), (xs[0], h)]}
    hinges = [("Joint_Hinge", (xs[0], 0.0), (xs[0], h))]
    for i, name in enumerate(panel_names):
        pieces[name] = rect(xs[i], 0.0, xs[i + 1], h)
        if i:
            hinges.append((f"Wall_Hinge_{i}", (xs[i], 0.0), (xs[i], h)))
        a, b = xs[i] + slot / 2.0, xs[i + 1] - slot / 2.0
        pieces[f"TopFlap{i + 1}"] = rect(a, -flap, b, 0.0)
        pieces[f"BottomFlap{i + 1}"] = rect(a, h, b, h + flap)
        hinges.append((f"TopFlap_Hinge_{i + 1}", (a, 0.0), (b, 0.0)))
        hinges.append((f"BottomFlap_Hinge_{i + 1}", (a, h), (b, h)))
    assemble_blank(cp, pieces, hinges, "Slot between adjacent closing flaps.")
    cp.add_crease(Point2D(joint_flap_width / 2.0, chamfer + 2.0),
                  Point2D(joint_flap_width / 2.0, h - chamfer - 2.0),
                  CreaseType.GLUE, 0.0, "ManufacturersJoint_Glue")
    cp.fefco_style = "0201"
    cp.joint_flap_width = float(joint_flap_width)
    cp.slot_width = slot
    cp.flap_depth = flap
    return cp
