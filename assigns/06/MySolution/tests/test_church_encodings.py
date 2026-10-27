import sys, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from target import App, Lam, Var, free_vars
from church import *
from evaluator import eval_target
from observers import observe_bool, observe_num

def apply2(fn, a, b): return App(App(fn, a), b)
def run(term, budget=200000):
    result = eval_target(term, budget)
    if result.status != "complete": raise AssertionError(result)
    return result.value

class ChurchEncodingTests(unittest.TestCase):
    def test_all_exported_combinators_are_closed(self):
        names = ("TRUE", "FALSE", "PAIR", "FST", "SND", "SUCC", "ADD", "MUL",
                 "PRED", "ISZERO", "SUB", "LEQ", "EQ", "NEQ", "AND", "OR",
                 "LT", "GT", "GE", "NOT", "Z")
        for name in names:
            self.assertFalse(free_vars(globals()[name]), name)

    def test_numerals_and_predecessor(self):
        for n in range(4):
            self.assertEqual(observe_num(run(num(n)), 1000).value, n)
            self.assertEqual(observe_num(run(App(PRED, num(n))), 10000).value, max(0, n - 1))

    def test_arithmetic(self):
        for a, b in ((0, 0), (1, 2), (2, 1), (3, 2)):
            self.assertEqual(observe_num(run(apply2(ADD, num(a), num(b))), 30000).value, a + b)
            self.assertEqual(observe_num(run(apply2(SUB, num(a), num(b))), 30000).value, max(0, a - b))
            self.assertEqual(observe_num(run(apply2(MUL, num(a), num(b))), 30000).value, a * b)

    def test_zero_test_comparisons_and_boolean_truth_tables(self):
        self.assertTrue(observe_bool(run(App(ISZERO, num(0)))).value)
        self.assertFalse(observe_bool(run(App(ISZERO, num(2)))).value)
        for a, b in ((0, 0), (0, 1), (2, 1), (1, 2)):
            expected = {"LEQ": a <= b, "EQ": a == b, "NEQ": a != b,
                        "LT": a < b, "GT": a > b, "GE": a >= b}
            for name, answer in expected.items():
                self.assertEqual(observe_bool(run(apply2(globals()[name], num(a), num(b)))).value, answer, (name, a, b))
        for left in (False, True):
            for right in (False, True):
                lterm, rterm = TRUE if left else FALSE, TRUE if right else FALSE
                self.assertEqual(observe_bool(run(apply2(AND, lterm, rterm))).value, left and right)
                self.assertEqual(observe_bool(run(apply2(OR, lterm, rterm))).value, left or right)
        self.assertFalse(observe_bool(run(App(NOT, TRUE))).value)
        self.assertTrue(observe_bool(run(App(NOT, FALSE))).value)

    def test_pair_and_successor(self):
        pair = run(apply2(PAIR, num(2), TRUE))
        self.assertEqual(observe_num(run(App(FST, pair))).value, 2)
        self.assertTrue(observe_bool(run(App(SND, pair))).value)
        self.assertEqual(observe_num(run(App(SUCC, num(2)))).value, 3)

if __name__ == "__main__": unittest.main()
