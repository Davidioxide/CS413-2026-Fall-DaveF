import sys, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from source_path import ASSIGN05
sys.path.insert(0, str(ASSIGN05))
from lambda1_vp import *
from compiler import compile_expr
from evaluator import eval_target
from observers import observe_pair

class NestedPairObservationTests(unittest.TestCase):
    def test_nested_and_mixed_pair_observation(self):
        source = D0Epair(D0Epair(D0Eint(2), D0Ebtf(True)), D0Eint(3))
        result = eval_target(compile_expr(source), 200000)
        self.assertEqual(result.status, "complete", result.message)
        observed = observe_pair(result.value, ("pair", ("pair", "num", "bool"), "num"), 200000, 200000)
        self.assertEqual(observed.status, "complete", observed.message)
        self.assertEqual(observed.value, ((2, True), 3))

    def test_pair_of_pair_and_natural(self):
        source = D0Epair(D0Epair(D0Eint(1), D0Eint(2)), D0Eint(3))
        result = eval_target(compile_expr(source), 200000)
        observed = observe_pair(result.value, ("pair", ("pair", "num", "num"), "num"), 200000, 200000)
        self.assertEqual(observed.status, "complete", observed.message)
        self.assertEqual(observed.value, ((1, 2), 3))

if __name__ == "__main__": unittest.main()
