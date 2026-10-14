"""Five bounded local workflow tools; no shell, URLs or general file browsing."""
import base64
import json
import mimetypes
from pathlib import Path
import re

from origami_cad.artifact_workflow import build, strict_json, MAX_INPUT
from origami_cad.artifact_validation import validate, safe_file
from origami_cad.cli_contract import SKILL, contract_data, digest, contract_current

RUN_SCHEMA = {'type': 'string', 'pattern': '^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$'}


def schema(properties, required):
    return {'type': 'object', 'properties': properties, 'required': required, 'additionalProperties': False}


TOOLS = [
    dict(name='origami_describe', description='Read executable contract, canonical workflow and verification limits.', inputSchema=schema({}, [])),
    dict(name='origami_build', description='Build one new declared run; never overwrite or retry the same run ID.', inputSchema=schema({'run_id': RUN_SCHEMA, 'spec': {'type': 'object'}}, ['run_id', 'spec'])),
    dict(name='origami_validate', description='Offline source-bound validation of one generated run.', inputSchema=schema({'run_id': RUN_SCHEMA}, ['run_id'])),
    dict(name='origami_look', description='Offline fixed look sheet using explicitly provisioned browser cache.', inputSchema=schema({'run_id': RUN_SCHEMA}, ['run_id'])),
    dict(name='origami_read_artifact', description='Read a manifest-listed artifact, hash verified, at most1MiB.', inputSchema=schema({'run_id': RUN_SCHEMA, 'filename': {'type': 'string', 'maxLength': 200}}, ['run_id', 'filename'])),
]


class ToolService:
    def __init__(self, repo, workspace, browser_cache=None):
        self.repo = Path(repo).resolve()
        workspace = Path(workspace).absolute()
        if workspace.is_symlink():
            raise ValueError('Workspace must not be symlinked')
        workspace.mkdir(parents=True, exist_ok=True)
        self.workspace = workspace.resolve()
        self.browser_cache = Path(browser_cache).resolve() if browser_cache else None

    def run_path(self, name):
        if not isinstance(name, str) or not re.fullmatch(RUN_SCHEMA['pattern'], name):
            raise ValueError('Run ID must be 1-64 letters/digits/underscores/hyphens, alphanumeric first')
        path = self.workspace / name
        if path.is_symlink() or path.resolve().parent != self.workspace:
            raise ValueError('Run escapes workspace')
        return path

    def arguments(self, name, args):
        description = next((t for t in TOOLS if t['name'] == name), None)
        if description is None:
            raise ValueError('Unknown tool')
        shape = description['inputSchema']
        if not isinstance(args, dict) or set(args) - set(shape['properties']) or set(shape['required']) - set(args):
            raise ValueError('Invalid tool arguments')
        if len(json.dumps(args, allow_nan=False).encode()) > MAX_INPUT:
            raise ValueError('Tool arguments exceed64KiB')
        if 'run_id' in args:
            self.run_path(args['run_id'])
        if 'spec' in args and not isinstance(args['spec'], dict):
            raise ValueError('spec must be an object')
        if 'filename' in args and (not isinstance(args['filename'], str) or len(args['filename']) > 200):
            raise ValueError('filename must be a bounded string')

    def call(self, name, args, cancel=None):
        self.arguments(name, args)
        if not contract_current(self.repo):
            raise ValueError('Runtime source or contract changed; restart MCP server and regenerate contract')
        if name == 'origami_describe':
            return {'contract': contract_data(self.repo), 'workflow': (self.repo / SKILL / 'SKILL.md').read_text(),
                    'limits': ['PHYSICAL_FOLD_FIT: NOT VERIFIED.', 'RECIPIENT_IMPORT: NOT VERIFIED.']}
        path = self.run_path(args['run_id'])
        if name == 'origami_build':
            receipt = build(self.repo, args['spec'], path, cancel)
            return {'output_dir': str(path), 'receipt': receipt, 'artifacts': self.artifacts(path, receipt)}
        # Every read/change requires a valid declared receipt first.
        receipt = strict_json(safe_file(path, 'artifact.json').read_bytes())
        if name == 'origami_validate':
            failures = validate(self.repo, path)
            return {'ok': not failures, 'diagnostics': failures, 'output_dir': str(path)}
        if name == 'origami_look':
            failures = validate(self.repo, path)
            if failures:
                raise ValueError('\n'.join(failures))
            if self.browser_cache is None:
                raise ValueError('LOOK: NOT RUN — configure a provisioned browser cache.')
            from origami_cad.look_harness import capture_look
            sheet = path / 'evidence/look-sheet.png'
            if not sheet.resolve().is_relative_to(path.resolve()) or any(p.is_symlink() for p in [sheet, *sheet.parents] if p == path or path in p.parents):
                raise ValueError('Evidence destination escapes run or is symlinked')
            index_file = path / 'evidence/artifact-index.json'
            if index_file.exists() or index_file.is_symlink():
                raise ValueError('Evidence index must be new')
            result = capture_look(self.repo, path, self.browser_cache, sheet, cancel=cancel)
            index = {name: digest(safe_file(path, name).read_bytes()) for name in
                     ('evidence/look-sheet.png', 'evidence/look-sheet.json')}
            with index_file.open('x') as stream:
                stream.write(json.dumps(index, sort_keys=True) + '\n')
            return {'sheet': str(sheet), 'look': result, 'evidence': self.artifacts(path, {'files': index})}
        if name == 'origami_read_artifact':
            filename = args['filename']
            listed = dict(receipt.get('files', {}))
            index_file = path / 'evidence/artifact-index.json'
            if index_file.exists():
                index = strict_json(safe_file(path, 'evidence/artifact-index.json').read_bytes())
                if not isinstance(index, dict) or set(index) != {'evidence/look-sheet.png', 'evidence/look-sheet.json'}:
                    raise ValueError('Invalid evidence index')
                listed.update(index)
            if filename != 'artifact.json' and filename not in listed:
                raise ValueError('Artifact is not manifest-listed')
            target = safe_file(path, filename)
            if target.stat().st_size > 1024 * 1024:
                raise ValueError('Artifact read exceeds1MiB')
            data = target.read_bytes()
            sha = digest(data)
            if filename in listed and listed[filename] != sha:
                raise ValueError('Artifact hash mismatch')
            mime = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
            encoding = 'base64' if mime.startswith('image/') or mime == 'application/pdf' else 'utf-8'
            content = base64.b64encode(data).decode() if encoding == 'base64' else data.decode('utf-8')
            return {'filename': filename, 'mime_type': mime, 'sha256': sha, 'encoding': encoding, 'data': content}
        raise ValueError('Unknown tool')

    @staticmethod
    def artifacts(path, receipt):
        return [dict(filename=name, path=str(path / name), sha256=sha,
                     mime_type=mimetypes.guess_type(name)[0] or 'application/octet-stream')
                for name, sha in receipt['files'].items()]
