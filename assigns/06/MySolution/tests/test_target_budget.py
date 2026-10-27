import copy, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from target import App, Lam, Var, render
from evaluator import eval_target

class TargetBudgetTests(unittest.TestCase):
    def setUp(self): self.identity = Lam("x", Var("x"))

    def test_value_and_exhaustion_at_zero_budget(self):
        self.assertEqual(eval_target(self.identity, 0).status, "complete")
        result = eval_target(App(self.identity, self.identity), 0)
        self.assertEqual((result.status, result.steps, result.value), ("exhausted", 0, None))

    def test_completion_on_the_last_permitted_beta_step(self):
        result = eval_target(App(self.identity, self.identity), 1)
        self.assertEqual(result.status, "complete")
        self.assertEqual(result.steps, 1)
        nested = App(App(self.identity, self.identity), self.identity)
        self.assertEqual(eval_target(nested, 1).status, "exhausted")
        self.assertEqual(eval_target(nested, 2).status, "complete")

    def test_reduction_is_deterministic_and_does_not_mutate_input(self):
        term = App(App(self.identity, self.identity), self.identity)
        snapshot = copy.deepcopy(term)
        first, second = eval_target(term, 10), eval_target(term, 10)
        self.assertEqual(first, second)
        self.assertEqual(term, snapshot)
        self.assertEqual(render(term), "(((lam x. x) (lam x. x)) (lam x. x))")

if __name__ == "__main__": unittest.main()
