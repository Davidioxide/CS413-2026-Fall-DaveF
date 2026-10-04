import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source"))
from model_rules import ModelRules

class ModelTests(unittest.TestCase):
    def test_source_revisions_and_rejection(self):
        m = ModelRules(); m.accept("D0Eint(1)", "one")
        self.assertEqual(m.revision, 1); m.results.append("old")
        with self.assertRaises(ValueError): m.accept(" ", "bad")
        self.assertEqual(m.source, "D0Eint(1)"); self.assertEqual(m.revision, 1); self.assertEqual(m.results, ["old"])
        m.accept("D0Eint(2)", "two"); self.assertEqual(m.revision, 2); self.assertEqual(m.results, [])

if __name__ == "__main__": unittest.main()
