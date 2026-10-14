"""FEFCO 0427 roll-end tray with locking cover (e-commerce "roll end tuck front" mailer).

Style source: FEFCO/ESBO International Fibreboard Case Code, style 0427 (folder-type
box, one piece, manual erection): the blank columns are front wall H, base B, back wall
H, cover B and a rounded tuck front; each end of the base carries an outer end wall,
a double score and an inner wall ending in a locking tab that drops into a slot in the
base next to the end score; front and back walls carry dust flaps, the cover carries
side flaps. The FEFCO sketch draws the slot on the score; here it sits one roll strip
inboard, where the rigid inner wall actually lands once caliper is accounted for.
Fibre Box Association "Box Styles Basics" (2014): formed from a single piece on a die
cutter, unbroken bottom, several layers in the end panels and a locking cover. Internal
dimensions L x B x H; no adhesive is used. Dimensions and clearances are parametric.
"""
from origami_cad.fold_graph import EPS as GEOMETRY_EPS
from origami_cad.geometry import CreaseType, OrigamiCreasePattern, Point2D
from origami_cad.packaging_fefco_helpers import assemble_blank, mirror_y, rect, validate_box_inputs


def generate_fefco_0427(
    width: float = 200.0,
    depth: float = 150.0,
    height: float = 60.0,
    thickness: float = 0.5,
    roll_clearance: float = 1.0,
    lock_tab_depth: float = 12.0,
) -> OrigamiCreasePattern:
    """
    Parametric FEFCO 0427 blank. width = L runs along the walls (vertical in the blank as
    in the FEFCO layout), depth = B is the base/cover column width, height = H. The roll
    strip between the two end scores is 2 x caliper + roll_clearance so the inner wall
    rolls over the dust flaps; the lock slot is a hole in the base centred one roll strip
    inboard of the end score with the same depth, so the tab lands in it. Dust flaps reach B/2 minus clearance so the two meet at the end centre; cover
    side flaps and the tuck front are H minus the roll strip. Walls carry the formula
    score allowance. No GLUE geometry is emitted: the style locks mechanically.
    """
    validate_box_inputs(width, depth, height, thickness)
    if not roll_clearance > 0 or not lock_tab_depth > 0:
        raise ValueError("roll clearance and lock tab depth must be positive")
    cp = OrigamiCreasePattern(name=f"FEFCO0427_{int(width)}x{int(depth)}x{int(height)}",
                              thickness_mm=thickness)
    allowance = cp.calculate_score_allowance(90.0)
    length, breadth, h = width + allowance, depth + allowance, float(height)
    strip = 2.0 * thickness + roll_clearance
    if h <= strip:
        raise ValueError("height must exceed the roll strip (2 x caliper + clearance)")
    # Intersection parameters use relative precision along each slot edge.
    gap_precision = GEOMETRY_EPS * max(1.0, strip)
    if length <= 3.0 * strip + gap_precision:
        raise ValueError("width plus score allowance must exceed 3 x roll strip to leave a positive lock slot gap")
    dust = breadth / 2.0 - roll_clearance
    tab_width = 0.3 * breadth
    slot_width = tab_width + 2.0 * roll_clearance
    if dust <= 0 or slot_width >= breadth:
        raise ValueError("depth must leave room for dust flaps and the lock slot")
    tuck = h - strip
    lid_flap = h - strip
    lid_chamfer = min(lid_flap / 2.0, 0.1 * breadth)
    tuck_chamfer = min(tuck / 2.0, 0.1 * length)

    x_base = h
    x_back = x_base + breadth
    x_lid = x_back + h
    x_tuck = x_lid + breadth
    x_end = x_tuck + tuck
    s0 = x_base + (breadth - slot_width) / 2.0
    s1 = s0 + slot_width
    t0 = x_base + (breadth - tab_width) / 2.0
    t1 = t0 + tab_width
    y_roll = -h
    y_inner = y_roll - strip
    y_tab = y_inner - h

    base = rect(x_base, 0.0, x_back, length)
    outer_end = rect(x_base, y_roll, x_back, 0.0)
    roll_strip = rect(x_base, y_inner, x_back, y_roll)
    inner_end = [(x_base, y_inner), (x_back, y_inner), (x_back, y_tab), (t1, y_tab),
                 (t1, y_tab - lock_tab_depth), (t0, y_tab - lock_tab_depth), (t0, y_tab), (x_base, y_tab)]
    front_dust = rect(0.0, -dust, x_base, 0.0)
    back_dust = rect(x_back, -dust, x_lid, 0.0)
    lid_side = [(x_lid, 0.0), (x_tuck, 0.0), (x_tuck, -(lid_flap - lid_chamfer)),
                (x_tuck - lid_chamfer, -lid_flap), (x_lid + lid_chamfer, -lid_flap),
                (x_lid, -(lid_flap - lid_chamfer))]
    tuck_front = [(x_tuck, 0.0), (x_tuck, length), (x_end - tuck_chamfer, length),
                  (x_end, length - tuck_chamfer), (x_end, tuck_chamfer), (x_end - tuck_chamfer, 0.0)]

    pieces = {"Base": base, "FrontWall": rect(0.0, 0.0, x_base, length),
              "BackWall": rect(x_back, 0.0, x_lid, length), "Lid": rect(x_lid, 0.0, x_tuck, length),
              "TuckFront": tuck_front}
    hinges = [("FrontWall_Hinge", (x_base, 0.0), (x_base, length)),
              ("BackWall_Hinge", (x_back, 0.0), (x_back, length)),
              ("Lid_Hinge", (x_lid, 0.0), (x_lid, length)),
              ("TuckFront_Hinge", (x_tuck, 0.0), (x_tuck, length))]
    ends = {"FrontDust": front_dust, "OuterEnd": outer_end, "RollStrip": roll_strip,
            "InnerEnd": inner_end, "BackDust": back_dust, "LidSide": lid_side}
    end_hinges = [("FrontDust_Hinge", (0.0, 0.0), (x_base, 0.0)),
                  ("OuterEnd_Hinge", (x_base, 0.0), (x_back, 0.0)),
                  ("Roll_Hinge", (x_base, y_roll), (x_back, y_roll)),
                  ("InnerEnd_Hinge", (x_base, y_inner), (x_back, y_inner)),
                  ("BackDust_Hinge", (x_back, 0.0), (x_lid, 0.0)),
                  ("LidSide_Hinge", (x_lid, 0.0), (x_tuck, 0.0))]
    for side, flip in (("Top", False), ("Bottom", True)):
        for name, polygon in ends.items():
            pieces[f"{name}{side}"] = mirror_y(polygon, length) if flip else list(polygon)
        for label, p, q in end_hinges:
            if flip:
                p, q = (p[0], length - p[1]), (q[0], length - q[1])
            hinges.append((f"{side}_{label}", p, q))
    assemble_blank(cp, pieces, hinges,
                   "Knife line separating a flap from the neighbouring end column; "
                   "both run from the body score to the blank edge.")
    # Lock slots: closed holes in the base where each rolled inner wall's tab lands.
    for side, y_centre in (("Top", strip), ("Bottom", length - strip)):
        slot = rect(s0, y_centre - strip / 2.0, s1, y_centre + strip / 2.0)
        for a, b in zip(slot, slot[1:] + slot[:1]):
            cp.add_crease(Point2D(*a), Point2D(*b), CreaseType.CUT, 0.0, f"LockSlot_{side}")
    cp.fefco_style = "0427"
    cp.roll_clearance = float(roll_clearance)
    cp.roll_strip_width = strip
    cp.lock_slot_height = strip
    cp.lock_tab_depth = float(lock_tab_depth)
    cp.tuck_depth = tuck
    cp.dust_flap_depth = dust
    return cp
