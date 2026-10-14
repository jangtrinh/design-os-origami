"""Bounded newline JSON-RPC/MCP lifecycle, cancellation and protocol-only stdout."""
import contextlib
import io
import json
import threading
from concurrent.futures import ThreadPoolExecutor

from origami_cad.artifact_workflow import strict_json
from origami_cad.cli_contract import SKILL
from origami_cad.mcp_tools import TOOLS

VERSIONS = ('2025-11-25', '2025-06-18', '2024-11-05')
MAX_MESSAGE = 128 * 1024


class Protocol:
    def __init__(self, service, output):
        self.service, self.output = service, output
        self.phase = 'new'
        self.lock = threading.Lock()
        self.pending = {}
        self.closed = False
        self.pool = ThreadPoolExecutor(max_workers=1)

    def send(self, payload):
        with self.lock:
            if not self.closed:
                self.output.write(json.dumps(payload, separators=(',', ':'), allow_nan=False) + '\n')
                self.output.flush()

    def error(self, ident, code, message):
        self.send({'jsonrpc': '2.0', 'id': ident, 'error': {'code': code, 'message': message}})

    def result(self, ident, result):
        self.send({'jsonrpc': '2.0', 'id': ident, 'result': result})

    def handle(self, raw):
        try:
            request = strict_json(raw)
        except (ValueError, UnicodeError):
            self.error(None, -32700, 'Parse error')
            return
        if (not isinstance(request, dict) or request.get('jsonrpc') != '2.0' or
                not isinstance(request.get('method'), str) or
                ('id' in request and (isinstance(request['id'], bool) or not isinstance(request['id'], (str, int))))):
            self.error(None, -32600, 'Invalid request')
            return
        ident, method = request.get('id'), request['method']
        params = request.get('params', {})
        if not isinstance(params, dict):
            if 'id' in request:
                self.error(ident, -32602, 'Params must be an object')
            return
        if 'id' not in request:
            if method == 'notifications/initialized' and self.phase == 'initialized':
                self.phase = 'ready'
            elif method == 'notifications/cancelled':
                request_id = params.get('requestId')
                event = self.pending.get(request_id) if isinstance(request_id, (str, int)) and not isinstance(request_id, bool) else None
                if event is not None:
                    event.set()
            return
        if ident in self.pending:
            self.error(ident, -32600, 'Request ID already active')
            return
        if method == 'ping':
            self.result(ident, {})
        elif method == 'initialize':
            if self.phase != 'new':
                self.error(ident, -32600, 'Already initialized')
            elif not isinstance(params.get('protocolVersion'), str) or not isinstance(params.get('capabilities'), dict) or not isinstance(params.get('clientInfo'), dict):
                self.error(ident, -32602, 'Invalid initialize parameters')
            else:
                self.phase = 'initialized'
                version = params['protocolVersion'] if params['protocolVersion'] in VERSIONS else VERSIONS[0]
                self.result(ident, {'protocolVersion': version, 'capabilities': {'tools': {}, 'prompts': {}},
                                    'serverInfo': {'name': 'origami-cad', 'version': '0.1.0'},
                                    'instructions': 'Local source-bound workflow; physical fit and recipient import are not verified.'})
        elif self.phase != 'ready':
            self.error(ident, -32000, 'Initialize and send notifications/initialized first')
        elif method == 'tools/list':
            self.result(ident, {'tools': TOOLS})
        elif method == 'prompts/list':
            self.result(ident, {'prompts': [{'name': 'origami-workflow', 'description': 'Canonical local CAD workflow'}]})
        elif method == 'prompts/get':
            if params.get('name') != 'origami-workflow' or params.get('arguments', {}):
                self.error(ident, -32602, 'Unknown prompt or arguments')
            else:
                text = (self.service.repo / SKILL / 'SKILL.md').read_text()
                self.result(ident, {'messages': [{'role': 'user', 'content': {'type': 'text', 'text': text}}]})
        elif method == 'tools/call':
            try:
                self.service.arguments(params.get('name'), params.get('arguments', {}))
            except (ValueError, TypeError, OverflowError):
                self.error(ident, -32602, 'Invalid tool name or arguments')
                return
            event = threading.Event()
            self.pending[ident] = event
            self.pool.submit(self.execute, ident, params['name'], params.get('arguments', {}), event)
        else:
            self.error(ident, -32601, 'Method not found')

    def execute(self, ident, name, args, event):
        try:
            # Product stdout never reaches protocol transport.
            with contextlib.redirect_stdout(io.StringIO()):
                if event.is_set():
                    raise ValueError('Operation cancelled')
                value = self.service.call(name, args, event)
            is_error = name == 'origami_validate' and not value['ok']
            content = [{'type': 'text', 'text': json.dumps(value, allow_nan=False)}]
            if name == 'origami_read_artifact' and value.get('mime_type') == 'image/png':
                content = [{'type': 'image', 'data': value['data'], 'mimeType': 'image/png'},
                           {'type': 'text', 'text': json.dumps({k: v for k, v in value.items() if k != 'data'})}]
            self.result(ident, {'content': content,
                                'structuredContent': value, 'isError': is_error})
        except Exception as error:
            self.result(ident, {'content': [{'type': 'text', 'text': str(error)}], 'isError': True})
        finally:
            self.pending.pop(ident, None)

    def serve(self, input_stream):
        try:
            while True:
                line = input_stream.readline(MAX_MESSAGE + 1)
                if not line:
                    break
                if len(line) > MAX_MESSAGE:
                    while line and not line.endswith(b'\n'):
                        line = input_stream.readline(MAX_MESSAGE + 1)
                    self.error(None, -32600, 'Message exceeds128KiB')
                    continue
                self.handle(line)
        finally:
            for event in list(self.pending.values()):
                event.set()
            self.pool.shutdown(wait=True, cancel_futures=True)
            self.closed = True
