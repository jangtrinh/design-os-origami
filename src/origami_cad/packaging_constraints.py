"""Shared manufacturing-seam constraints for parametric carton blanks."""
import math


def validate_glue_flap(flap_width, receiving_span, name='glue_flap_width'):
    """Reject a requested seam flap that cannot fit its closing receiving panel."""
    for label, value in ((name, flap_width), ('receiving panel span', receiving_span)):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
            raise ValueError(f'{label} must be a finite positive length')
    if flap_width > receiving_span:
        raise ValueError(f'{name} ({flap_width:g} mm) must not exceed the receiving panel '
                         f'({receiving_span:g} mm); reduce the flap or enlarge the receiving panel')
