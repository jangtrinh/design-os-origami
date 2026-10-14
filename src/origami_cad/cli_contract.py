"""Generated contract from the parser, generator signatures and product source."""
import hashlib
import inspect
import json
from pathlib import Path

from origami_cad.cli import create_parser
from origami_cad.product_registry import PRODUCTS
from origami_cad import packaging
from origami_cad.printer_profile_export import DEFAULT_SPOTS

SKILL = Path('skills/es-origami-cad')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def source_hash(repo):
    """Bind every runtime module, including validation/protocol, by relative name."""
    tree = Path(repo) / 'src/origami_cad'
    return digest(b''.join(p.relative_to(repo).as_posix().encode() + b'\0' + p.read_bytes()
                           for p in sorted(tree.rglob('*.py'))))


def model_parameters():
    out = {}
    for slug, _, function in PRODUCTS:
        defaults = {k: p.default for k, p in inspect.signature(getattr(packaging, function)).parameters.items()
                    if k in {'width', 'depth', 'height', 'wall_height', 'radius', 'thickness'}}
        if 'wall_height' in defaults:
            defaults['height'] = defaults.pop('wall_height')
        defaults['thickness'] = 0.5  # CLI default overrides generator caliper.
        if slug == 'diamond-box':
            defaults['width'] = 50.0  # Historical CLI override, unlike registry default.
        out[slug] = defaults
    out['deer-base'] = {'width': 200.0}
    out['miura-ori'] = {}
    return out


def contract_data(repo):
    parser = create_parser()
    generate = next(a for a in parser._actions if a.dest == 'command').choices['generate']
    arguments = [{'flags': a.option_strings, 'type': getattr(a.type, '__name__', 'str'),
                  'choices': a.choices, 'default': a.default} for a in generate._actions if a.dest != 'help']
    return dict(schema_version=1, source_hash=source_hash(repo), arguments=arguments,
                parameters=model_parameters(), profiles=['presentation', 'printer'],
                workflow_profile_limits={'miura-ori': ['presentation'], 'deer-base': ['presentation']},
                output_names={'presentation': ['{name}.svg', '{name}.dxf', '{name}_viewer.html'],
                              'printer': ['{name}_printer.pdf', '{name}_printer.dxf']},
                spots=DEFAULT_SPOTS, bleed_mm=3.0,
                limits=['Sampled source-derived continuity is not continuous-time or physical fit proof.',
                        'Printer PDF: five spots, 1 pt; DXF: mm/y-up. Recipient import unverified.',
                        'Allowance heuristic at 90 degrees is 0.45*t; mandated formula unresolved.'])


def render_contract(repo):
    payload = json.dumps(contract_data(repo), sort_keys=True, indent=2, allow_nan=False)
    return ('<!-- sha256: ' + digest(payload.encode()) + ' -->\n'
            '# Generated executable contract\n\nDo not edit. Run `python3 scripts/skill_contract.py`.\n\n'
            '```json\n' + payload + '\n```\n').encode()


def contract_current(repo):
    path = Path(repo) / SKILL / 'contract.md'
    return (source_hash(repo) == LOADED_SOURCE_HASH and path.is_file() and
            not path.is_symlink() and path.read_bytes() == render_contract(repo))


# Long-lived MCP processes must not attest newly edited source while executing
# already-imported Python code. Restart after any runtime source mutation.
LOADED_SOURCE_HASH = source_hash(Path(__file__).resolve().parents[2])
