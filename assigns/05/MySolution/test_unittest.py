import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lambda1_vp import (D0Eapp, D0Ebtf, D0Efix, D0Eif0, D0Eint, D0Elet,
                        D0Elam, D0Eop1, D0Eop2, D0Epair, D0Epfst, D0Epsnd,
                        D0Evar, d0exp_fvset)
from solution import d0exp_pretty, d0exp_substitute


class VisitorOperationTests(unittest.TestCase):
    def test_pretty_prints_every_constructor(self):
        self.assertEqual(d0exp_pretty(D0Eint(-12345678901234567890)), "-12345678901234567890")
        self.assertEqual(d0exp_pretty(D0Ebtf(True)), "true")
        self.assertEqual(d0exp_pretty(D0Ebtf(False)), "false")
        self.assertEqual(d0exp_pretty(D0Evar("x")), "x")
        self.assertEqual(d0exp_pretty(D0Eop1("-1", D0Evar("x"))), "(-1 x)")
        self.assertEqual(d0exp_pretty(D0Eop2("+", D0Eint(1), D0Eint(2))), "(1 + 2)")
        self.assertEqual(d0exp_pretty(D0Elam("x", D0Evar("x"))), "(lam x. x)")
        self.assertEqual(d0exp_pretty(D0Efix("f", "x", D0Evar("f"))), "(fix f(x). f)")
        self.assertEqual(d0exp_pretty(D0Eapp(D0Evar("f"), D0Eint(2))), "(f 2)")
        self.assertEqual(d0exp_pretty(D0Eif0(D0Ebtf(True), D0Eint(1), D0Eint(0))),
                         "(if true then 1 else 0)")
        self.assertEqual(d0exp_pretty(D0Elet("x", D0Eint(1), D0Evar("x"))),
                         "(let x = 1 in x)")
        self.assertEqual(d0exp_pretty(D0Epair(D0Eint(1), D0Ebtf(False))), "(pair 1 false)")
        self.assertEqual(d0exp_pretty(D0Epfst(D0Evar("p"))), "(fst p)")
        self.assertEqual(d0exp_pretty(D0Epsnd(D0Evar("p"))), "(snd p)")

    def test_substitutes_through_all_nonbinding_forms(self):
        expr = D0Eif0(
            D0Eop2("+", D0Evar("x"), D0Eint(1)),
            D0Epair(D0Eapp(D0Evar("x"), D0Evar("y")), D0Epfst(D0Evar("x"))),
            D0Epsnd(D0Eop1("+1", D0Evar("x"))),
        )
        result = d0exp_substitute(expr, "x", D0Eop2("+", D0Evar("x"), D0Eint(1)))
        self.assertEqual(d0exp_pretty(result),
                         "(if ((x + 1) + 1) then (pair ((x + 1) y) (fst (x + 1))) else (snd (+1 (x + 1))))")
        self.assertEqual(d0exp_pretty(d0exp_substitute(D0Evar("z"), "x", D0Eint(2))), "z")

    def test_shadowing_and_let_initializer(self):
        self.assertEqual(d0exp_pretty(d0exp_substitute(D0Elam("x", D0Evar("x")), "x", D0Eint(3))),
                         "(lam x. x)")
        self.assertEqual(d0exp_pretty(d0exp_substitute(D0Efix("f", "n", D0Evar("f")), "f", D0Eint(3))),
                         "(fix f(n). f)")
        self.assertEqual(d0exp_pretty(d0exp_substitute(D0Efix("f", "n", D0Evar("n")), "n", D0Eint(3))),
                         "(fix f(n). n)")
        same = D0Efix("x", "x", D0Evar("x"))
        self.assertEqual(d0exp_pretty(d0exp_substitute(same, "x", D0Eint(7))), "(fix x(x). x)")
        term = D0Elet("x", D0Evar("x"), D0Eop2("+", D0Evar("x"), D0Evar("y")))
        self.assertEqual(d0exp_pretty(d0exp_substitute(term, "x", D0Eint(3))),
                         "(let x = 3 in (x + y))")

    def test_capture_avoidance_for_lambda_let_and_fix(self):
        self.assertEqual(d0exp_pretty(d0exp_substitute(
            D0Elam("y", D0Eop2("+", D0Evar("x"), D0Evar("y"))), "x", D0Evar("y"))),
                         "(lam y_1. (y + y_1))")
        self.assertEqual(d0exp_pretty(d0exp_substitute(
            D0Elet("y", D0Evar("x"), D0Eop2("+", D0Evar("x"), D0Evar("y"))), "x", D0Evar("y"))),
                         "(let y_1 = y in (y + y_1))")
        self.assertEqual(d0exp_pretty(d0exp_substitute(
            D0Efix("f", "n", D0Eop2("+", D0Evar("x"), D0Eapp(D0Evar("f"), D0Evar("n")))),
            "x", D0Evar("f"))), "(fix f_1(n). (f + (f_1 n)))")
        both = D0Efix("f", "y", D0Eop2("+", D0Evar("x"), D0Evar("y")))
        self.assertEqual(d0exp_pretty(d0exp_substitute(both, "x", D0Epair(D0Evar("f"), D0Evar("y")))),
                         "(fix f_1(y_1). ((pair f y) + y_1))")

    def test_nested_shadowing_freshness_determinism_and_inputs(self):
        expr = D0Elam("y_1", D0Elam("y", D0Eop2("+", D0Evar("x"), D0Evar("y"))))
        replacement = D0Evar("y")
        before = copy.deepcopy(expr)
        first = d0exp_substitute(expr, "x", replacement)
        second = d0exp_substitute(expr, "x", replacement)
        self.assertEqual(first, second)
        self.assertEqual(expr, before)
        self.assertEqual(d0exp_fvset(first), (d0exp_fvset(expr) - {"x"}) | d0exp_fvset(replacement))

    def test_operations_do_not_evaluate(self):
        dangerous = D0Eop2("/", D0Eint(1), D0Eint(0))
        self.assertEqual(d0exp_pretty(dangerous), "(1 / 0)")
        self.assertEqual(d0exp_pretty(d0exp_substitute(dangerous, "x", D0Eint(2))), "(1 / 0)")


if __name__ == "__main__":
    unittest.main()
