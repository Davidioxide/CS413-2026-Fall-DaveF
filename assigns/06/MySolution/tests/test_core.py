import copy, os, sys, unittest
from pathlib import Path

_solution = Path(__file__).resolve().parents[1]
_assigns = next(
    parent for parent in Path(__file__).resolve().parents
    if (parent / "05" / "lambda1_vp.py").is_file()
)
sys.path.insert(0, str(_solution))
sys.path.insert(0, str(_assigns / "05"))
from lambda1_vp import *
from target import *
from compiler import compile_expr, CompileError
from evaluator import eval_target
from observers import observe_num, observe_bool
from church import num, TRUE, FALSE, ADD, PRED
from parser import parse

class CoreTests(unittest.TestCase):
    def test_substitution_capture(self):
        r = substitute(Lam("y", Var("x")), "x", Var("y"))
        self.assertEqual(free_vars(r), {"y"}); self.assertIsInstance(r, Lam); self.assertNotEqual(r.name, "y")
    def test_budget_and_weak_values(self):
        i = Lam("x", Var("x"))
        self.assertEqual(eval_target(i, 0).status, "complete")
        self.assertEqual(eval_target(App(i, i), 0).status, "exhausted")
        self.assertEqual(eval_target(App(i, i), 1).steps, 1)
        self.assertEqual(eval_target(Lam("x", App(i, i)), 0).steps, 0)
    def test_observers(self):
        self.assertEqual(observe_num(num(4), 100).value, 4)
        self.assertTrue(observe_bool(TRUE, 20).value)
        self.assertFalse(observe_bool(FALSE, 20).value)
    def test_compile_pure_and_free_vars(self):
        e = D0Elet("x", D0Evar("s"), D0Eop2("+", D0Evar("x"), D0Evar("z")))
        before = copy.deepcopy(e); t = compile_expr(e)
        self.assertEqual(d0exp_fvset(e), {"s", "z"}); self.assertEqual(free_vars(t), {"s", "z"}); self.assertEqual(e, before)
    def test_validation_entire_ast(self):
        with self.assertRaisesRegex(CompileError, "unsupported operator"):
            compile_expr(D0Eif0(D0Ebtf(True), D0Eint(1), D0Eop2("/", D0Eint(1), D0Eint(0))))
        with self.assertRaisesRegex(CompileError, "negative"):
            compile_expr(D0Eint(-1))
    def test_short_circuit(self):
        loop = D0Eapp(D0Efix("f", "x", D0Eapp(D0Evar("f"), D0Evar("x"))), D0Eint(0))
        self.assertEqual(observe_bool(eval_target(compile_expr(D0Eop2("and", D0Ebtf(False), loop)), 100).value, 30).value, False)
        self.assertEqual(observe_bool(eval_target(compile_expr(D0Eop2("or", D0Ebtf(True), loop)), 100).value, 30).value, True)
    def test_constructor_notation_parser(self):
        self.assertEqual(render(compile_expr(parse('D0Evar("x")'))), "x")
        self.assertEqual(render(compile_expr(parse('D0Elam("x", D0Evar("x"))'))), "(lam x. x)")

if __name__ == "__main__": unittest.main()
