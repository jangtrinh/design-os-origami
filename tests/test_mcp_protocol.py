"""Lifecycle, malformed messages, cancellation/EOF and protocol-only stdout."""
import io
import json
import select
import subprocess
import sys
import threading
import unittest
from unittest.mock import patch

from origami_cad.mcp_protocol import Protocol, MAX_MESSAGE, VERSIONS
from origami_cad.mcp_tools import ToolService
from origami_cad.cli_contract import SKILL
from skill_fixture import SkillFixture, ROOT, TUCK


class McpProtocol(SkillFixture):
    def setUp(self):
        super().setUp()
        (self.repo / SKILL / 'SKILL.md').write_text('Concept → Build → Check → Hand over → Adjust')
        self.service = ToolService(self.repo, self.base / 'workspace')
        self.output = io.StringIO()
        self.protocol = Protocol(self.service, self.output)
        self.addCleanup(self.protocol.pool.shutdown, wait=True)

    def request(self, method, params=None, ident=1):
        request = {'jsonrpc': '2.0', 'method': method, 'params': params or {}}
        if ident is not None:
            request['id'] = ident
        self.protocol.handle(json.dumps(request).encode())
        self.protocol.pool.submit(lambda: None).result(timeout=10)
        return [json.loads(line) for line in self.output.getvalue().splitlines()]

    def initialize(self, version=VERSIONS[0]):
        self.request('initialize', {'protocolVersion': version, 'capabilities': {}, 'clientInfo': {'name': 'test', 'version': '1'}})
        self.request('notifications/initialized', ident=None)

    def test_versions_initialization_prompt_and_discovery(self):
        self.initialize()
        self.assertEqual(self.request('tools/list')[-1]['result']['tools'][0]['name'], 'origami_describe')
        self.assertEqual(len(self.request('tools/list')[-1]['result']['tools']), 5)
        self.assertEqual(self.request('prompts/list')[-1]['result']['prompts'][0]['name'], 'origami-workflow')
        self.assertIn('Concept', self.request('prompts/get', {'name': 'origami-workflow'})[-1]['result']['messages'][0]['content']['text'])
        self.assertNotIn('resources', self.request('initialize')[-1].get('result', {}).get('capabilities', {}))

    def test_before_initialized_and_duplicate_initialize_rejected(self):
        self.assertEqual(self.request('tools/list')[-1]['error']['code'], -32000)
        self.initialize()
        self.assertEqual(self.request('initialize')[-1]['error']['code'], -32600)

    def test_invalid_initialize_and_version_negotiation(self):
        self.assertEqual(self.request('initialize', {'protocolVersion': 123})[-1]['error']['code'], -32602)
        self.initialize('unsupported')
        initialized = [r for r in self.request('ping') if 'result' in r and 'protocolVersion' in r['result']][0]
        self.assertEqual(initialized['result']['protocolVersion'], VERSIONS[0])

    def test_malformed_nonfinite_duplicate_keys_batches_and_boolean_ids(self):
        for raw, code in [(b'{', -32700), (b'{"jsonrpc":"2.0","jsonrpc":"2.0"}', -32700),
                          (b'{"value":NaN}', -32700), (b'[]', -32600),
                          (b'{"jsonrpc":"2.0","method":"ping","id":true}', -32600)]:
            with self.subTest(raw=raw):
                self.protocol.handle(raw)
                self.assertEqual(json.loads(self.output.getvalue().splitlines()[-1])['error']['code'], code)

    def test_deep_json_is_rejected_and_following_ping_survives(self):
        raw = b'{"jsonrpc":"2.0","id":1,"method":"ping","params":{"value":' + b'[' * 1500 + b'0' + b']' * 1500 + b'}}'
        self.protocol.handle(raw)
        self.assertEqual(json.loads(self.output.getvalue().splitlines()[-1])['error']['code'], -32700)
        self.assertEqual(self.request('ping')[-1]['result'], {})

    def test_json_number_overflow_rejected(self):
        self.protocol.handle(b'{"jsonrpc":"2.0","id":1,"method":"ping","params":{"value":1e999}}')
        self.assertEqual(json.loads(self.output.getvalue().splitlines()[-1])['error']['code'], -32700)

    def test_unknown_method_tool_and_prompt_are_protocol_errors(self):
        self.initialize()
        for method, params, code in [('missing', {}, -32601), ('tools/call', {'name': 'shell'}, -32602),
                                     ('prompts/get', {'name': 'missing'}, -32602),
                                     ('tools/call', {'name': 'origami_validate', 'arguments': {'run_id': '../x'}}, -32602)]:
            self.assertEqual(self.request(method, params)[-1]['error']['code'], code)

    def test_engine_error_is_tool_result_not_protocol_error(self):
        self.initialize()
        result = self.request('tools/call', {'name': 'origami_build', 'arguments': {'run_id': 'bad', 'spec': TUCK | {'parameters': {'width': 0}}}})[-1]
        self.assertTrue(result['result']['isError'])
        self.assertNotIn('error', result)

    def test_cli_stdout_is_captured(self):
        self.initialize()
        def noisy(*args):
            print('This must not enter protocol stdout')
            return {'ok': True}
        with patch.object(self.service, 'call', side_effect=noisy):
            result = self.request('tools/call', {'name': 'origami_describe'})[-1]
        self.assertFalse(result['result']['isError'])
        self.assertNotIn('This must', self.output.getvalue())

    def test_cancellation_notification_and_unhashable_request_id_are_safe(self):
        self.initialize()
        event = threading.Event()
        self.protocol.pending['active'] = event
        before = self.output.getvalue()
        self.request('notifications/cancelled', {'requestId': 'active'}, ident=None)
        self.assertTrue(event.is_set())
        self.request('notifications/cancelled', {'requestId': {}}, ident=None)
        self.assertEqual(self.output.getvalue(), before)
        self.protocol.pending.clear()

    def test_eof_and_oversized_message_drain(self):
        raw = b'x' * (MAX_MESSAGE + 40) + b'\n' + b'{"jsonrpc":"2.0","id":1,"method":"ping"}\n'
        self.protocol.serve(io.BytesIO(raw))
        rows = [json.loads(line) for line in self.output.getvalue().splitlines()]
        self.assertEqual(rows[0]['error']['code'], -32600)
        self.assertEqual(rows[1]['result'], {})
        self.assertTrue(self.protocol.closed)

    def test_real_stdio_client_build_validate_and_read(self):
        # Actual subprocess transport; waits for response before EOF.
        process = subprocess.Popen([sys.executable, '-B', str(ROOT / 'scripts/run_mcp.py'), '--workspace', str(self.base / 'wire')], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        self.addCleanup(process.stderr.close)
        self.addCleanup(process.stdout.close)
        self.addCleanup(lambda: process.stdin.close() if not process.stdin.closed else None)
        def call(message):
            process.stdin.write(json.dumps(message).encode() + b'\n')
            process.stdin.flush()
            self.assertTrue(select.select([process.stdout], [], [], 15)[0], 'MCP response timed out')
            return json.loads(process.stdout.readline())
        for version in [VERSIONS[0]]:
            response = call({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': {'protocolVersion': version, 'capabilities': {}, 'clientInfo': {'name': 'wire-test', 'version': '1'}}})
            self.assertEqual(response['result']['protocolVersion'], version)
        process.stdin.write(b'{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        process.stdin.flush()
        discovery = call({'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list'})
        self.assertEqual(len(discovery['result']['tools']), 5)
        built = call({'jsonrpc': '2.0', 'id': 3, 'method': 'tools/call', 'params': {'name': 'origami_build', 'arguments': {'run_id': 'real', 'spec': TUCK}}})
        self.assertFalse(built['result']['isError'], built)
        checked = call({'jsonrpc': '2.0', 'id': 4, 'method': 'tools/call', 'params': {'name': 'origami_validate', 'arguments': {'run_id': 'real'}}})
        self.assertTrue(checked['result']['structuredContent']['ok'])
        read = call({'jsonrpc': '2.0', 'id': 5, 'method': 'tools/call', 'params': {'name': 'origami_read_artifact', 'arguments': {'run_id': 'real', 'filename': 'artifact.json'}}})
        self.assertEqual(json.loads(read['result']['structuredContent']['data'])['spec']['type'], 'tuck-box')
        process.stdin.close()
        self.assertEqual(process.wait(timeout=10), 0)
        self.assertEqual(process.stdout.read(), b'')
        self.assertEqual(process.stderr.read(), b'')
