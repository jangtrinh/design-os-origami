"""Offline source-bound browser capture; dependencies are caller-provisioned."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import time

from origami_cad.preview_model import build_preview_model
from origami_cad.product_registry import product_blanks


class LookError(ValueError):
    """Code 1 is invalid evidence; code 2 is unavailable capture runtime."""
    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


def _json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'),
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (OSError, ValueError) as error:
        raise LookError(f'artifact: cannot read valid JSON: {error}') from error


def _file(root, name):
    if not isinstance(name, str) or '\\' in name:
        raise LookError('artifact path: expected a relative filename')
    relative = PurePosixPath(name)
    if relative.is_absolute() or not relative.parts or any(p in {'.', '..'} for p in relative.parts):
        raise LookError('artifact path: traversal is forbidden')
    target = root.joinpath(*relative.parts)
    if any(p.is_symlink() for p in [target, *target.parents] if p != root.parent):
        raise LookError('artifact path: symlink is forbidden')
    if not target.is_file() or not target.resolve().is_relative_to(root):
        raise LookError(f'artifact file: missing or outside run: {name}')
    return target


def _source_blanks(spec):
    # Use the shared dispatcher when integrated; the pre-core capture worktree
    # retains the same existing generators while its dependency is being built.
    try:
        from origami_cad.artifact_workflow import blanks_for_spec
    except ModuleNotFoundError as error:
        if error.name != 'origami_cad.artifact_workflow':
            raise
    else:
        return blanks_for_spec(spec)
    parameters = spec.get('parameters', {})
    kind = spec['type']
    if kind == 'miura-ori':
        from origami_cad.packaging import generate_miura_ori_sleeve
        return (generate_miura_ori_sleeve(),)
    if kind == 'deer-base':
        from origami_cad.figurative import generate_deer_bird_base
        return (generate_deer_bird_base(size=parameters.get('width', 200.0)),)
    return product_blanks(kind, **parameters)


def prepare_job(repo_root, output_dir, sheet):
    """Validate bytes and source geometry before exposing artifacts to Chromium."""
    root, output = Path(repo_root).resolve(), Path(output_dir).resolve()
    sheet = Path(sheet).absolute()
    if sheet.suffix.lower() != '.png' or sheet.exists() or sheet.is_symlink():
        raise LookError('sheet: PNG destination exists or is invalid; choose a fresh path')
    sheet = sheet.resolve()
    receipt = sheet.with_suffix('.json')
    if receipt.exists() or receipt.is_symlink():
        raise LookError('receipt: destination exists; choose a fresh path')
    manifest = _json(_file(output, 'artifact.json'))
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1:
        raise LookError('artifact: unsupported schema_version')
    for key in ('source_hash', 'contract_hash'):
        if not re.fullmatch('[a-f0-9]{64}', str(manifest.get(key, ''))):
            raise LookError(f'artifact: invalid {key}')
    files = manifest.get('files')
    if not isinstance(files, dict) or not files:
        raise LookError('artifact: missing files mapping')
    for name, expected in files.items():
        path = _file(output, name)
        if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise LookError(f'artifact hash: changed file {name}')
    spec, rows = manifest.get('spec'), manifest.get('blanks')
    if not isinstance(spec, dict) or not isinstance(rows, list) or not rows:
        raise LookError('artifact: missing normalized spec or blanks')
    try:
        blanks = _source_blanks(spec)
    except (TypeError, KeyError, ValueError) as error:
        raise LookError(f'artifact spec: {error}') from error
    if [row.get('name') for row in rows] != [cp.name for cp in blanks]:
        raise LookError('L7: source blank names do not match receipt')
    job = dict(schema_version=1, sheet=str(sheet), receipt=str(receipt),
               source_hash=manifest['source_hash'], contract_hash=manifest['contract_hash'],
               artifact_hash=hashlib.sha256((output / 'artifact.json').read_bytes()).hexdigest(),
               spec=spec, blanks=[])
    for cp, row in zip(blanks, rows):
        model = build_preview_model(cp)
        preview = row.get('preview', {})
        if not isinstance(preview, dict) or preview.get('available') != model['available']:
            raise LookError('L7: preview availability differs from source')
        from origami_cad.preview_recording import preview_records_match
        if not preview_records_match(preview, model, cp):
            raise LookError('L7: preview receipt differs from source')
        if spec.get('preview_requirement') == 'available' and not model['available']:
            raise LookError('L7: input requires an available preview')
        svg_name, viewer_name = cp.name + '.svg', cp.name + '_viewer.html'
        if svg_name not in files or viewer_name not in files:
            raise LookError('artifact file: SVG and viewer must be manifest-listed')
        svg, viewer = _file(output, svg_name), _file(output, viewer_name)
        text = viewer.read_text(encoding='utf-8')
        match = re.search(r'<script id="fold-model" type="application/json">(.*?)</script>', text, re.S)
        try:
            embedded = json.loads(match.group(1)) if match else None
        except ValueError as error:
            raise LookError('L7: invalid embedded fold model') from error
        if not preview_records_match(embedded, model, cp):
            raise LookError('L7: embedded model differs from regenerated source')
        job['blanks'].append(dict(name=cp.name, svg=str(svg), viewer=str(viewer),
                                 # Python checked source equivalence above; the
                                 # browser must check the exact saved JSON bytes.
                                 model=embedded, viewer_hash=files[viewer_name], svg_hash=files[svg_name]))
    return job


def run_look(repo_root, output_dir, browser_cache, sheet, cancel=None):
    """Return machine evidence; never install dependencies or fetch a URL."""
    try:
        from origami_cad.artifact_validation import validate
    except ModuleNotFoundError as error:
        if error.name != 'origami_cad.artifact_validation':
            raise
        raise LookError('LOOK: NOT RUN — artifact validation runtime unavailable', 2) from error
    else:
        failures = validate(repo_root, output_dir)
        if failures:
            raise LookError('artifact validation: ' + '; '.join(failures))
    job = prepare_job(repo_root, output_dir, sheet)
    cache = Path(browser_cache).resolve()
    node = shutil.which('node')
    if not node or not (cache / 'node_modules/playwright').is_dir():
        raise LookError('LOOK: NOT RUN — Node or cached Playwright unavailable', 2)
    job['browser_cache'] = str(cache)
    script = Path(repo_root).resolve() / 'scripts/capture-viewer.cjs'
    if not script.is_file():
        raise LookError('LOOK: NOT RUN — capture runtime unavailable', 2)
    process = None
    try:
        process = subprocess.Popen([node, str(script)], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        deadline, pending_input = time.monotonic() + 180, json.dumps(job, allow_nan=False)
        while True:
            if cancel is not None and cancel.is_set():
                process.terminate()
                try:
                    process.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                # Destinations were required to be new; remove only this request's evidence.
                for target in (Path(sheet), Path(sheet).with_suffix('.json')):
                    if target.is_file() and not target.is_symlink():
                        target.unlink()
                raise LookError('look: operation cancelled; no evidence published')
            if time.monotonic() >= deadline:
                process.terminate()
                try:
                    process.communicate(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.communicate()
                raise LookError('LOOK: NOT RUN — capture runtime timed out', 2)
            try:
                stdout, stderr = process.communicate(input=pending_input, timeout=0.1)
                break
            except subprocess.TimeoutExpired:
                pending_input = None
        result = subprocess.CompletedProcess([node, str(script)], process.returncode, stdout, stderr)
    except (OSError, subprocess.TimeoutExpired) as error:
        raise LookError(f'LOOK: NOT RUN — capture runtime failed: {error}', 2) from error
    finally:
        if process is not None:
            if process.poll() is None:
                process.kill()
                process.wait()
            for stream in (process.stdin, process.stdout, process.stderr):
                stream.close()
    if result.returncode:
        raise LookError(result.stderr.strip() or 'look: browser capture failed',
                        2 if result.returncode == 2 else 1)
    try:
        evidence = json.loads(result.stdout)
    except ValueError as error:
        raise LookError('look: invalid capture process response') from error
    sheet_path = Path(sheet)
    if not evidence.get('ok') or not sheet_path.is_file() or sheet_path.read_bytes()[:8] != b'\x89PNG\r\n\x1a\n':
        raise LookError('look: capture did not produce a valid PNG')
    return evidence


def capture_look(repo, output, browser_cache, sheet, cancel=None):
    """Shared MCP boundary; capture errors retain their machine/dependency code."""
    return run_look(repo, output, browser_cache, sheet, cancel=cancel)


def main(argv=None):
    parser = argparse.ArgumentParser(description='Capture source-bound offline fold evidence')
    for name in ('repo-root', 'output-dir', 'browser-cache', 'sheet'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args(argv)
    try:
        result = run_look(args.repo_root, args.output_dir, args.browser_cache, args.sheet)
    except (LookError, OSError, TypeError) as error:
        print(str(error), file=sys.stderr)
        return error.code if isinstance(error, LookError) else 1
    print(json.dumps(result, allow_nan=False))
    return 0
