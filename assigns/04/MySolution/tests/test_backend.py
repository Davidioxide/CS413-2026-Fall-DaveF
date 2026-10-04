import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))
import backend
import lambda1 as lang

class BackendTests(unittest.TestCase):
    def test_free_variables_all_forms_and_scopes(self):
        e = lang.D0Eif0(lang.D0Eop1("+1", lang.D0Evar("a")), lang.D0Epair(lang.D0Evar("b"), lang.D0Evar("b")), lang.D0Epsnd(lang.D0Evar("c")))
        self.assertEqual(lang.d0exp_fvset(e), frozenset({"a", "b", "c"}))
        self.assertEqual(lang.d0exp_fvset(lang.D0Elam("x", lang.D0Eop2("+", lang.D0Evar("x"), lang.D0Evar("y")))), frozenset({"y"}))
        self.assertEqual(lang.d0exp_fvset(lang.D0Efix("f", "x", lang.D0Eapp(lang.D0Evar("f"), lang.D0Evar("z")))), frozenset({"z"}))
        self.assertEqual(lang.d0exp_fvset(lang.D0Elet("x", lang.D0Evar("x"), lang.D0Evar("x"))), frozenset({"x"}))
        self.assertIsInstance(lang.d0exp_fvset(lang.D0Eint(1)), frozenset)

    def test_lint_does_not_evaluate(self):
        source = 'D0Eop2("/", D0Eint(1), D0Eint(0))'
        result = backend.backend.run("lint", source, 3)
        self.assertEqual(result["outcome"], "success")

    def test_lint_open_and_interpret(self):
        self.assertEqual(backend.backend.run("lint", 'D0Evar("x")', 1)["outcome"], "language_error")
        self.assertEqual(backend.backend.run("interpret", 'D0Eop2("+", D0Eint(20), D0Eint(22))', 2)["message"], "D0Vint(arg1=42)")
        self.assertEqual(backend.backend.run("interpret", 'D0Eop2("/", D0Eint(1), D0Eint(0))', 2)["outcome"], "runtime_error")
        self.assertEqual(backend.backend.run("interpret", "not a call", 2)["outcome"], "invalid_input")

    def test_placeholders_and_execute(self):
        self.assertEqual(backend.backend.run("typecheck", "D0Eint(1)", 1)["outcome"], "not_implemented")
        self.assertEqual(backend.backend.run("compile", "D0Eint(1)", 1)["outcome"], "not_implemented")
        self.assertEqual(backend.backend.run("execute", "", 1)["outcome"], "not_implemented")

    def test_backend_failure_is_retryable_result(self):
        first = backend.backend.run("unknown", "D0Eint(1)", 4)
        retry = backend.backend.run("interpret", "D0Eint(1)", 4)
        self.assertEqual(first["outcome"], "backend_error")
        self.assertEqual(retry["outcome"], "success")
        self.assertEqual(first["revision"], retry["revision"])

if __name__ == "__main__": unittest.main()
