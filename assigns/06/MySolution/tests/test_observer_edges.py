import sys, unittest
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from target import App, Lam, Var
from church import ADD, FALSE, TRUE, num
from evaluator import eval_target
from observers import observe_bool, observe_num

class ObserverEdgeTests(unittest.TestCase):
    def test_alpha_renamed_natural_and_boolean_values(self):
        natural = Lam("count", Lam("zero", App(Var("count"), App(Var("count"), Var("zero")))))
        boolean = Lam("yes", Lam("no", Var("yes")))
        self.assertEqual(observe_num(natural, 100).value, 2)
        self.assertTrue(observe_bool(boolean, 100).value)

    def test_computed_encoding_with_redexes_is_observable(self):
        result = eval_target(App(App(ADD, num(2)), num(3)), 100000)
        self.assertEqual(result.status, "complete")
        self.assertEqual(observe_num(result.value, 100000).value, 5)

    def test_incomplete_and_malformed_observations_do_not_decode(self):
        incomplete = observe_num(num(2), 0)
        self.assertEqual(incomplete.status, "exhausted")
        self.assertIsNone(incomplete.value)
        malformed = observe_num(Lam("c", Lam("z", Var("free"))), 100)
        self.assertEqual(malformed.status, "invalid")
        self.assertIsNone(malformed.value)
        bool_incomplete = observe_bool(TRUE, 0)
        self.assertEqual(bool_incomplete.status, "exhausted")
        self.assertIsNone(bool_incomplete.value)

if __name__ == "__main__": unittest.main()
