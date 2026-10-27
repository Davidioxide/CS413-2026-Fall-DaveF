import copy, sys, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from source_path import ASSIGN05
sys.path.insert(0, str(ASSIGN05))
from lambda1_vp import *
from compiler import compile_expr
from evaluator import eval_target
from observers import observe_num
from target import free_vars

class RecursionAndScopeTests(unittest.TestCase):
    def test_coincident_fix_binders_use_parameter_binding(self):
        source = D0Eapp(D0Efix("f", "f", D0Evar("f")), D0Eint(3))
        result = eval_target(compile_expr(source), 100000)
        self.assertEqual(result.status, "complete", result.message)
        self.assertEqual(observe_num(result.value).value, 3)

    def test_recursive_parameter_and_function_names_can_collide_with_encodings(self):
        body = D0Eif0(D0Eop2("==", D0Evar("s"), D0Eint(0)), D0Eint(0),
                      D0Eapp(D0Evar("f"), D0Eop2("-", D0Evar("s"), D0Eint(1))))
        source = D0Eapp(D0Efix("f", "s", body), D0Eint(3))
        result = eval_target(compile_expr(source), 200000)
        self.assertEqual(result.status, "complete", result.message)
        self.assertEqual(observe_num(result.value).value, 0)

    def test_source_name_collisions_and_free_scope_are_preserved(self):
        source = D0Elet("s", D0Eint(2), D0Eop2("+", D0Evar("s"), D0Eint(1)))
        before = copy.deepcopy(source)
        target = compile_expr(source)
        self.assertEqual(free_vars(target), set())
        self.assertEqual(source, before)
        result = eval_target(target, 50000)
        self.assertEqual(observe_num(result.value).value, 3)

if __name__ == "__main__": unittest.main()
