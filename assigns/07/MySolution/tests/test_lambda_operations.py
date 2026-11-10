import unittest

from MySolution import server


class LambdaOperationTests(unittest.TestCase):
    def call(self, method, params, request_id=1):
        body, valid = server.dispatch({"jsonrpc": "2.0", "method": method, "params": params, "id": request_id})
        self.assertTrue(valid)
        self.assertEqual(body["id"], request_id)
        return body

    def test_typecheck_arithmetic(self):
        self.assertEqual(self.call("lambda.typecheck", {"source": "1 + 2"})["result"], {"type": "sint"})

    def test_typecheck_function(self):
        source = "let f : sint -> sint = lam (x: sint) => x in f end"
        self.assertEqual(self.call("lambda.typecheck", {"source": source})["result"], {"type": "sint -> sint"})

    def test_interpret_arithmetic_and_factorial(self):
        self.assertEqual(self.call("lambda.interpret", {"source": "20 + 22"})["result"], {"type": "sint", "value": "42"})
        factorial = "let fact : sint -> sint = fix fact(n: sint): sint => if n <= 1 then 1 else n * fact(n - 1) in fact(6) end"
        self.assertEqual(self.call("lambda.interpret", {"source": factorial})["result"], {"type": "sint", "value": "720"})

    def test_interpret_tuple_and_collection(self):
        self.assertEqual(self.call("lambda.interpret", {"source": "(1, true)"})["result"], {"type": "(sint, bool)", "value": "(1, true)"})
        self.assertEqual(self.call("lambda.interpret", {"source": "list_cons(1, list_cons(2, list_nil()))"})["result"], {"type": "List[sint]", "value": "[1, 2]"})

    def test_function_result_does_not_leak_closure(self):
        result = self.call("lambda.interpret", {"source": "let f : sint -> sint = lam (x: sint) => x in f end"})["result"]
        self.assertEqual(result, {"type": "sint -> sint", "value": "<lam>"})
        self.assertNotIn("environment", result["value"].lower())

    def test_python_and_javascript_compilation(self):
        for target in ("python", "javascript"):
            with self.subTest(target=target):
                result = self.call("lambda.compile", {"source": "1 + 2", "target": target})["result"]
                self.assertEqual(result["target"], target)
                self.assertTrue(result["code"].strip())


if __name__ == "__main__":
    unittest.main()
