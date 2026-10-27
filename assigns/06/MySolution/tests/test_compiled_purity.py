import sys, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from source_path import ASSIGN05
sys.path.insert(0, str(ASSIGN05))
from lambda1_vp import *
from compiler import compile_expr
from target import App, Lam, Var

TARGET_TYPES = (Var, Lam, App)

def assert_pure(testcase, term):
    testcase.assertIsInstance(term, TARGET_TYPES)
    if isinstance(term, Var): return
    if isinstance(term, Lam): return assert_pure(testcase, term.body)
    assert_pure(testcase, term.fn); assert_pure(testcase, term.arg)

class CompiledPurityTests(unittest.TestCase):
    def test_every_source_constructor_and_operator_compiles_to_pure_target(self):
        values = [D0Eint(0), D0Ebtf(True), D0Evar("x"),
                  D0Elam("x", D0Evar("x")), D0Eapp(D0Elam("x", D0Evar("x")), D0Eint(1)),
                  D0Eop1("not", D0Ebtf(False)), D0Eif0(D0Ebtf(True), D0Eint(1), D0Eint(2)),
                  D0Elet("x", D0Eint(1), D0Evar("x")), D0Epair(D0Eint(1), D0Ebtf(False)),
                  D0Epfst(D0Epair(D0Eint(1), D0Ebtf(False))), D0Epsnd(D0Epair(D0Eint(1), D0Ebtf(False))),
                  D0Efix("f", "x", D0Evar("x"))]
        operators = ["+", "-", "*", "<", "<=", ">", ">=", "==", "!=", "and", "or"]
        values.extend(D0Eop2(op, D0Eint(1), D0Eint(0)) for op in operators)
        for source in values:
            assert_pure(self, compile_expr(source))

    def test_compilation_does_not_need_the_evaluator(self):
        source = D0Eop2("+", D0Eint(2), D0Eint(3))
        import evaluator
        original = evaluator.eval_target
        evaluator.eval_target = lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("evaluator called"))
        try: assert_pure(self, compile_expr(source))
        finally: evaluator.eval_target = original

if __name__ == "__main__": unittest.main()
