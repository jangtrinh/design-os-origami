# Origami mathematics: local conditions and limits

These mathematical ideas guide construction; they do not establish physical
assembly, global flat-foldability, collision avoidance or rigid-carton closure.
Source attribution and provenance limits are in [ATTRIBUTION.md](../ATTRIBUTION.md).

## Single-crease construction

| Axiom | Construction |
| --- | --- |
| O1 | Fold through two distinct points |
| O2 | Fold one point onto another |
| O3 | Fold one line onto another |
| O4 | Fold perpendicular to a line through a point |
| O5 | Fold through one point placing another onto a line |
| O6 | Place two points onto two respective lines with one fold |
| O7 | Place a point onto a line with a fold perpendicular to another line |

Construction existence depends on geometric preconditions; a named axiom does
not authorize an arbitrary crease or a fabricated solution. These operations
are distinct from the product's packaging-family parameter schema.

## Interior single-vertex checks

For an interior vertex of even degree 2n, consecutive sectors must sum to 360°.
Kawasaki's alternating sectors sum to 180° each for local flat-foldability under
its idealized assumptions. A assigned flat fold must also satisfy Maekawa's
`abs(M - V) == 2`. Generic CREASE is not a mountain/valley assignment.

Right: sectors `[60, 110, 120, 70]` have alternating sums 180° and 180°.
Wrong: sectors `[90, 90, 85, 95]` have alternating sums 175° and 185°;
a four-valent label alone does not establish Kawasaki's condition.

```python
# Right: local numerical condition, with its scope explicit.
def alternating_sectors_ok(sectors, tolerance=0.5):
    return (len(sectors) >= 4 and len(sectors) % 2 == 0
            and all(angle > 0 for angle in sectors)
            and abs(sum(sectors) - 360) <= tolerance
            and abs(sum(sectors[::2]) - 180) <= tolerance
            and abs(sum(sectors[1::2]) - 180) <= tolerance)

# Wrong: global_foldable = alternating_sectors_ok(sectors)
```

## Decision guidance

| Target | Use | Trade-off / when NOT to use |
| --- | --- | --- |
| Ideal interior flat-folding vertex | Local sector and M/V checks | Not a boundary vertex or volumetric carton theorem |
| Generated carton | Product topology + sampled source-derived continuity | Not proof of physical fit or all-time closure |
| Research tessellation | Explicit construction and qualification limits | Not an implemented packaging generator by analogy |
| Manufacturing release | Recipient import and physical sample | Mathematical labels alone are insufficient |

## Common pitfalls and diagnostics

| Failure | Observable evidence | Mechanical home |
| --- | --- | --- |
| Odd assigned interior degree | M/V counts cannot differ by 2 | Mathematical review; do not invent a runtime error |
| Wrong M/V export | SVG differs from source segment assignment | `fold-metadata` |
| Broken blank connectivity | Product topology check reports invalid material/contour | `topology` |
| Missing global test | Only local vertex equations were checked | Report NOT VERIFIED; no theorem-to-product upgrade |

Diagnostics are check identifiers from [rules.md](../rules.md), not invented
mathematical exception strings. Local success does not decide layer ordering.
