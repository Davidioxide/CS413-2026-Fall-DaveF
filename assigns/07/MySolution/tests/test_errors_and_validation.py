import unittest
from unittest import mock

from MySolution import lambda_service, server


class ErrorAndValidationTests(unittest.TestCase):
    def dispatch(self, method, params, request_id="error"):
        return server.dispatch({"jsonrpc": "2.0", "method": method, "params": params, "id": request_id})[0]

    def test_syntax_and_type_errors_are_distinct(self):
        syntax = self.dispatch("lambda.typecheck", {"source": "if then"})
        type_error = self.dispatch("lambda.typecheck", {"source": "1 + true"})
        self.assertEqual(syntax["error"]["code"], -32010)
        self.assertEqual(type_error["error"]["code"], -32011)
        self.assertNotIn("traceback", str(syntax).lower())

    def test_unbound_variable_is_rejected(self):
        body = self.dispatch("lambda.typecheck", {"source": "not_declared"})
        self.assertEqual(body["error"]["code"], -32011)
        self.assertEqual(body["error"]["data"]["kind"], "type")

    def test_blank_missing_wrong_type_and_oversized_source(self):
        cases = ({}, {"source": "   "}, {"source": 12}, {"source": "x" * (lambda_service.MAX_SOURCE_BYTES + 1)})
        for params in cases:
            with self.subTest(params_type=type(params.get("source")).__name__):
                self.assertEqual(self.dispatch("lambda.interpret", params)["error"]["code"], -32602)

    def test_compile_target_and_params_are_validated(self):
        self.assertEqual(self.dispatch("lambda.compile", {"source": "1 + 2", "target": "ruby"})["error"]["code"], -32602)
        missing = server.dispatch({"jsonrpc": "2.0", "method": "lambda.typecheck", "id": 1})[0]
        wrong = server.dispatch({"jsonrpc": "2.0", "method": "lambda.typecheck", "params": [], "id": 2})[0]
        self.assertEqual(missing["error"]["code"], -32602)
        self.assertEqual(wrong["error"]["code"], -32600)

    def test_unknown_method_and_invalid_envelope(self):
        self.assertEqual(self.dispatch("missing.method", {})["error"]["code"], -32601)
        invalid, valid = server.dispatch({"jsonrpc": "1.0", "method": "service.health", "id": 3})
        self.assertFalse(valid)
        self.assertEqual(invalid["error"]["code"], -32600)
        self.assertIsNone(invalid["id"])

    def test_unexpected_backend_failure_is_sanitized(self):
        with mock.patch.object(server.service, "typecheck", side_effect=RuntimeError("secret traceback path")):
            body = self.dispatch("lambda.typecheck", {"source": "1 + 2"}, request_id=8)
        self.assertEqual(body["error"]["code"], -32603)
        self.assertNotIn("traceback", str(body).lower())
        self.assertNotIn("secret", str(body))

    def test_interpret_timeout_has_explicit_error(self):
        with mock.patch.object(server.service, "INTERPRET_TIMEOUT_SECONDS", 0.0):
            body = self.dispatch("lambda.interpret", {"source": "1 + 2"}, request_id=9)
        self.assertEqual(body["error"]["code"], -32012)
        self.assertEqual(body["error"]["data"], {"kind": "timeout"})


if __name__ == "__main__":
    unittest.main()
