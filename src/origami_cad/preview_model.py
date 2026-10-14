"""Public preview selection preserves the baseline gate, then tries dense coordinated motion."""
from origami_cad.fold_faces import build_fold_model
from origami_cad.fold_coordinated import build_coordinated_fold_model


def build_preview_model(cp):
    """Select actual qualified motion without guessing from a product name."""
    baseline = build_fold_model(cp)
    if baseline['available']:
        return baseline
    candidate = build_coordinated_fold_model(cp)
    if candidate['available'] or candidate.get('coordination', {}).get('candidates'):
        return candidate
    return baseline
