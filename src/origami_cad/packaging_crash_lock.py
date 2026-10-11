"""Scored bottom tube geometry with explicitly named flap slits."""
from origami_cad.geometry import OrigamiCreasePattern, Point2D, CreaseType


def generate_crash_lock_box(
    width: float = 80.0,
    depth: float = 60.0,
    height: float = 100.0,
    thickness: float = 0.5,
    glue_flap_width: float = 15.0,
) -> OrigamiCreasePattern:
    """
    Generates a 1-2-3 Crash-Lock (auto) Bottom Box (FEFCO 0215 style): the bottom flaps
    carry diagonal 45° creases that snap into a self-locking base when the tube is erected;
    the top is a plain tuck closure.
    """
    cp = OrigamiCreasePattern(name=f"CrashLockBox_{int(width)}x{int(depth)}x{int(height)}", thickness_mm=thickness)
    c_allow = cp.calculate_score_allowance(90.0)
    w, d, h = width + c_allow, depth + c_allow, height

    # Panels along X: Glue -> Left (D) -> Front (W) -> Right (D) -> Back (W)
    xs = [0.0, glue_flap_width]
    for span in (d, w, d, w):
        xs.append(xs[-1] + span)
    y_top, y_body_top, y_body_bot, y_bot = -d * 0.6, 0.0, h, h + d

    # Body hinges and top/bottom fold lines
    for i, x in enumerate(xs[1:-1]):
        cp.add_crease(Point2D(x, y_body_top), Point2D(x, y_body_bot), CreaseType.CREASE, 90.0, f"Hinge_{i}")
    cp.add_crease(Point2D(xs[1], y_body_top), Point2D(xs[-1], y_body_top), CreaseType.CREASE, 90.0, "TopFold")
    cp.add_crease(Point2D(xs[1], y_body_bot), Point2D(xs[-1], y_body_bot), CreaseType.CREASE, 90.0, "BottomFold")

    # Only the three internal boundaries at each end are flap-separation slits.
    cp.cut_slits = {f"{end}Slit_{i}": "Separates adjacent closure flaps from body hinge to flap edge."
                    for end in ("Top", "Bottom") for i in range(2, 5)}

    # Crash-lock bottom flaps: 45° gusset creases from each lower hinge corner
    for i in range(1, 5):
        x_a, x_b = xs[i], xs[i + 1]
        span = x_b - x_a
        rise = min(span / 2.0, y_bot - y_body_bot)
        cp.add_crease(Point2D(x_a, y_body_bot), Point2D(x_a + rise, y_body_bot + rise), CreaseType.VALLEY, -90.0, "LockDiag")
        cp.add_crease(Point2D(x_b, y_body_bot), Point2D(x_b - rise, y_body_bot + rise), CreaseType.MOUNTAIN, 90.0, "LockDiag")
        cp.add_crease(Point2D(x_a, y_bot), Point2D(x_b, y_bot), CreaseType.CUT, 0.0, "FlapEdge")
        cp.add_crease(Point2D(x_a, y_body_bot), Point2D(x_a, y_bot), CreaseType.CUT, 0.0, f"BottomSlit_{i}" if i > 1 else "FlapSide")
        # Top tuck panel edge
        cp.add_crease(Point2D(x_a, y_body_top), Point2D(x_a, y_top), CreaseType.CUT, 0.0, f"TopSlit_{i}" if i > 1 else "TopSide")
        cp.add_crease(Point2D(x_a, y_top), Point2D(x_b, y_top), CreaseType.CUT, 0.0, "TopEdge")
    cp.add_crease(Point2D(xs[-1], y_body_top), Point2D(xs[-1], y_bot), CreaseType.CUT, 0.0)
    cp.add_crease(Point2D(xs[-1], y_top), Point2D(xs[-1], y_body_top), CreaseType.CUT, 0.0, "TopRightEdge")
    cp.add_crease(Point2D(xs[0], y_body_top), Point2D(xs[0], y_body_bot), CreaseType.CUT, 0.0, "GlueOuterCut")
    cp.add_crease(Point2D(xs[0], y_body_top), Point2D(xs[0], y_body_bot), CreaseType.GLUE, 0.0, "GlueEdge")
    # Glue flap outline: close the top/bottom cut edges of the flap
    cp.add_crease(Point2D(xs[0], y_body_top), Point2D(xs[1], y_body_top), CreaseType.CUT, 0.0, "GlueFlapTop")
    cp.add_crease(Point2D(xs[0], y_body_bot), Point2D(xs[1], y_body_bot), CreaseType.CUT, 0.0, "GlueFlapBottom")

    cp.add_facet("CrashLockFront", [Point2D(xs[2], 0), Point2D(xs[3], 0), Point2D(xs[3], h), Point2D(xs[2], h)])
    return cp
