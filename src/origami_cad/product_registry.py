"""Product-to-blank contract: one independently exported CP per physical blank."""
from origami_cad import packaging

# A two-piece product has one CLI choice and two independently named blanks.
PRODUCTS = (
    ('tuck-box', 'Tuck box', 'generate_tuck_box'),
    ('hex-petal', 'Hexagonal petal box', 'generate_hexagonal_petal_box'),
    ('diamond-box', 'Diamond faceted box', 'generate_diamond_faceted_box'),
    ('zero-glue-tray', 'Zero-glue tray', 'generate_zero_glue_tray'),
    ('gable-box', 'Gable handle box', 'generate_gable_handle_box'),
    ('pillow-box', 'Pillow box', 'generate_pillow_box'),
    ('crash-lock-box', 'Crash-lock box', 'generate_crash_lock_box'),
    ('fefco-0201', 'FEFCO 0201 RSC', 'generate_fefco_0201'),
    ('fefco-0427', 'FEFCO 0427 mailer', 'generate_fefco_0427'),
    ('sleeve-tray', 'Sleeve + tray', 'generate_sleeve_tray'),
    ('food-box', 'Hinged food box', 'generate_food_box'),
)


def product_blanks(slug, **dimensions):
    """Return distinct source blanks, preserving each generator's own defaults."""
    names = {key: function for key, _, function in PRODUCTS}
    if slug not in names:
        raise ValueError('Unknown carton product')
    arguments = {name: value for name, value in dimensions.items() if value is not None}
    if slug == 'zero-glue-tray' and 'height' in arguments:
        arguments['wall_height'] = arguments.pop('height')
    if slug == 'hex-petal':
        arguments.pop('width', None)
        arguments.pop('depth', None)
    else:
        arguments.pop('radius', None)
    if slug in {'diamond-box'}:
        arguments.pop('depth', None)
    result = getattr(packaging, names[slug])(**arguments)
    blanks = tuple(result) if isinstance(result, (tuple, list)) else (result,)
    if not blanks or len({cp.name for cp in blanks}) != len(blanks):
        raise ValueError('Products must have distinct named blanks')
    return blanks


def catalog_blanks():
    """Flatten products for per-blank assets, topology checks and model selection."""
    entries = []
    for slug, label, _ in PRODUCTS:
        blanks = product_blanks(slug)
        for index, cp in enumerate(blanks):
            part = ('sleeve', 'tray')[index] if slug == 'sleeve-tray' else None
            entries.append(dict(slug=slug+'-'+part if part else slug,
                                label=label+' · '+part if part else label,
                                product=slug, part=part, cp=cp))
    return entries
