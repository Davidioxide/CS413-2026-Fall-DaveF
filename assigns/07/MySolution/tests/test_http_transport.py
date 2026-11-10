import unittest
from unittest import mock

from fastapi.testclient import TestClient

from MySolution import lambda_service
from MySolution import server
from MySolution.server import app


class HttpTransportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def post(self, payload, **kwargs):
        return self.client.post("/rpc", json=payload, **kwargs)

    def test_success_has_http_and_json_rpc_contract(self):
        result = self.post({
            "jsonrpc": "2.0",
            "method": "service.health",
            "params": {},
            "id": "health",
        })
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.headers["content-type"].split(";", 1)[0], "application/json")
        self.assertEqual(result.json()["result"], {"status": "ok", "version": "1.0"})

    def test_malformed_json_is_rpc_parse_error(self):
        result = self.client.post(
            "/rpc",
            content=b'{"jsonrpc":',
            headers={"content-type": "application/json"},
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["error"]["code"], -32700)

    def test_unsupported_media_type_is_transport_error(self):
        result = self.client.post("/rpc", content=b"{}", headers={"content-type": "text/plain"})
        self.assertEqual(result.status_code, 415)

    def test_notification_has_no_response_body(self):
        result = self.post({"jsonrpc": "2.0", "method": "service.health", "params": {}})
        self.assertEqual(result.status_code, 204)
        self.assertEqual(result.content, b"")

    def test_batch_includes_invalid_member_and_omits_notification(self):
        result = self.post([
            {"jsonrpc": "2.0", "method": "service.health", "params": {}, "id": "ok"},
            "not-a-request",
            {"jsonrpc": "2.0", "method": "service.health", "params": {}},
        ])
        self.assertEqual(result.status_code, 200)
        bodies = result.json()
        self.assertEqual(len(bodies), 2)
        self.assertEqual({body["id"] for body in bodies}, {"ok", None})
        self.assertEqual(next(body for body in bodies if body["id"] is None)["error"]["code"], -32600)

    def test_backend_failure_is_sanitized_over_http(self):
        with mock.patch.object(server.service, "typecheck", side_effect=RuntimeError("secret /Users/private/trace")):
            result = self.post({
                "jsonrpc": "2.0",
                "method": "lambda.typecheck",
                "params": {"source": "1 + 2"},
                "id": "failure",
            })
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["error"]["code"], -32603)
        self.assertNotIn("secret", result.text)
        self.assertNotIn("/Users/private", result.text)

    def test_timeout_is_explicit_over_http(self):
        with mock.patch.object(lambda_service, "INTERPRET_TIMEOUT_SECONDS", 0.0):
            result = self.post({
                "jsonrpc": "2.0",
                "method": "lambda.interpret",
                "params": {"source": "1 + 2"},
                "id": "timeout",
            })
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()["error"]["code"], -32012)
        self.assertEqual(result.json()["id"], "timeout")


if __name__ == "__main__":
    unittest.main()
