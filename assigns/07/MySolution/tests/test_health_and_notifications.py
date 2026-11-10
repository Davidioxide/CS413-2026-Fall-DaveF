import unittest

from MySolution import server


class HealthAndNotificationTests(unittest.TestCase):
    def request(self, params=None, request_id="id-1"):
        request = {"jsonrpc": "2.0", "method": "service.health", "params": params or {}}
        if request_id != "__notification__":
            request["id"] = request_id
        return server.dispatch(request)

    def test_health_result_and_id_are_preserved(self):
        body, valid = self.request(request_id="health-42")
        self.assertTrue(valid)
        self.assertEqual(body["jsonrpc"], "2.0")
        self.assertEqual(body["id"], "health-42")
        self.assertEqual(body["result"], {"status": "ok", "version": "1.0"})
        self.assertNotIn("error", body)

    def test_health_accepts_numeric_and_null_ids(self):
        for request_id in (7, 3.5, None):
            with self.subTest(request_id=request_id):
                self.assertEqual(self.request(request_id=request_id)[0]["id"], request_id)

    def test_health_rejects_nonempty_params(self):
        self.assertEqual(self.request(params={"unexpected": True})[0]["error"]["code"], -32602)

    def test_single_notification_has_no_response(self):
        body, valid = self.request(request_id="__notification__")
        self.assertTrue(valid)
        self.assertIsNone(body)


if __name__ == "__main__":
    unittest.main()
