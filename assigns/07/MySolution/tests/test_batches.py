import unittest

from MySolution import server


class BatchAndEnvelopeTests(unittest.TestCase):
    def test_batch_preserves_ids_and_omits_notification(self):
        requests = [
            {"jsonrpc": "2.0", "method": "lambda.interpret", "params": {"source": "6 * 7"}, "id": "answer"},
            {"jsonrpc": "2.0", "method": "service.health", "params": {}},
        ]
        responses = [server.dispatch(item)[0] for item in requests]
        returned = [item for item in responses if item is not None]
        self.assertEqual(len(returned), 1)
        self.assertEqual(returned[0]["id"], "answer")
        self.assertEqual(returned[0]["result"]["value"], "42")

    def test_notification_only_batch_has_no_responses(self):
        requests = [
            {"jsonrpc": "2.0", "method": "service.health", "params": {}},
            {"jsonrpc": "2.0", "method": "lambda.typecheck", "params": {"source": "1 + 2"}},
        ]
        self.assertEqual([server.dispatch(item)[0] for item in requests], [None, None])

    def test_malformed_batch_member_gets_null_id_error(self):
        good, _ = server.dispatch({"jsonrpc": "2.0", "method": "service.health", "params": {}, "id": "ok"})
        bad, _ = server.dispatch("not-a-request-object")
        self.assertEqual(good["id"], "ok")
        self.assertIsNone(bad["id"])
        self.assertEqual(bad["error"]["code"], -32600)

    def test_empty_batch_is_invalid_request(self):
        body, valid = server.dispatch([])
        self.assertFalse(valid)
        self.assertIsNone(body["id"])
        self.assertEqual(body["error"]["code"], -32600)

    def test_response_never_contains_result_and_error(self):
        for request in (
            {"jsonrpc": "2.0", "method": "service.health", "params": {}, "id": 1},
            {"jsonrpc": "2.0", "method": "missing", "params": {}, "id": 2},
        ):
            body, _ = server.dispatch(request)
            self.assertFalse("result" in body and "error" in body)


if __name__ == "__main__":
    unittest.main()
