import sys, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from source_path import ASSIGN05
sys.path.insert(0, str(ASSIGN05))
from lambda1_vp import *
from compiler import compile_expr
from evaluator import eval_target
from observers import observe_bool, observe_num

def loop():
    return D0Eapp(D0Efix("loop", "x", D0Eapp(D0Evar("loop"), D0Evar("x"))), D0Eint(0))
def execute(expr, budget=5000): return eval_target(compile_expr(expr), budget)

class CallByValueControlTests(unittest.TestCase):
    def test_function_argument_and_let_initializer_are_strict(self):
        fn_arg = execute(D0Eapp(D0Elam("x", D0Eint(0)), loop()))
        let_init = execute(D0Elet("x", loop(), D0Eint(2)))
        self.assertEqual(fn_arg.status, "exhausted")
        self.assertEqual(let_init.status, "exhausted")

    def test_both_pair_components_are_strict(self):
        left = execute(D0Epair(loop(), D0Eint(1)))
        right = execute(D0Epair(D0Eint(1), loop()))
        self.assertEqual(left.status, "exhausted")
        self.assertEqual(right.status, "exhausted")

    def test_conditionals_and_boolean_operators_delay_unselected_terms(self):
        yes = execute(D0Eif0(D0Ebtf(True), D0Eint(1), loop()))
        no = execute(D0Eif0(D0Ebtf(False), loop(), D0Eint(2)))
        conjunction = execute(D0Eop2("and", D0Ebtf(False), loop()))
        disjunction = execute(D0Eop2("or", D0Ebtf(True), loop()))
        self.assertEqual(yes.status, "complete")
        self.assertEqual(no.status, "complete")
        self.assertEqual(conjunction.status, "complete")
        self.assertEqual(disjunction.status, "complete")
        self.assertEqual(observe_num(yes.value).value, 1)
        self.assertEqual(observe_num(no.value).value, 2)
        self.assertFalse(observe_bool(conjunction.value).value)
        self.assertTrue(observe_bool(disjunction.value).value)

if __name__ == "__main__": unittest.main()
