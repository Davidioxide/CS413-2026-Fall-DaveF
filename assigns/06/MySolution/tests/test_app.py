"""Black-box CLI tests for the interactive source-to-target application.

The tests deliberately invoke app.py as a subprocess rather than importing its
helpers.  This exercises argument handling, prompts, parsing, compilation, and
target rendering together.
"""
from __future__ import annotations
import os
from pathlib import Path
import subprocess
import sys
import unittest

TESTS = Path(__file__).resolve().parent
SOLUTION = TESTS.parent
APP = SOLUTION / "app.py"

def run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    return subprocess.run(
        [sys.executable, str(APP), *args], input=input_text, text=True,
        capture_output=True, cwd="/tmp", env=environment, timeout=30,
    )

class InteractiveAppTests(unittest.TestCase):
    def test_more_than_100_valid_inputs_in_interactive_cli(self):
        inputs = []
        inputs.extend(str(n) for n in range(30))
        inputs.extend(["true", "false"] * 5)
        inputs.extend(f"v{i}" for i in range(10))
        inputs.extend(f"lam x{i}. x{i}" for i in range(10))
        inputs.extend(f"{i} + {i + 1} * 2" for i in range(10))
        inputs.extend(f"{i} <= {i + 1}" for i in range(10))
        inputs.extend(["true and false", "false or true", "not false"] * 4)
        inputs.extend(f"let x = {i} in x + 1" for i in range(10))
        inputs.extend(["if true then 1 else 2", "if false then 1 else 2"] * 5)
        inputs.extend(["pair(2, true)", "fst(pair(2, true))", "snd(pair(2, true))"] * 4)
        inputs.extend([
            'D0Evar("x")', 'D0Elam("x", D0Evar("x"))',
            'D0Eapp(D0Elam("x", D0Evar("x")), D0Eint(3))',
            'D0Eop2("+", D0Eint(2), D0Eint(3))',
            'D0Eop1("not", D0Ebtf(false))',
            'D0Epair(D0Eint(1), D0Ebtf(true))',
            'D0Epfst(D0Epair(D0Eint(1), D0Ebtf(true)))',
            'D0Epsnd(D0Epair(D0Eint(1), D0Ebtf(true)))',
            'D0Eif0(D0Ebtf(true), D0Eint(1), D0Eint(2))',
            'D0Elet("x", D0Eint(2), D0Eop2("+", D0Evar("x"), D0Eint(3)))',
            'D0Efix("f", "x", D0Elam("y", D0Evar("x")))',
        ])
        self.assertGreaterEqual(len(inputs), 100)
        scripted = []
        for expression in inputs:
            scripted.extend((expression, "n"))
        result = run_cli(input_text="\n".join(scripted + [":quit", ""]))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count("Observe value? [y/n]: "), len(inputs))
        self.assertNotIn("ERROR", result.stdout, result.stdout[-1000:])
        self.assertNotRegex(result.stdout, r"D0E(?:int|var|lam|app|op|if|let|pair|pfst|psnd|fix)")

    def test_one_shot_cli_and_exact_basic_outputs(self):
        variable = run_cli('D0Evar("x")', input_text="n\n")
        abstraction = run_cli('D0Elam("x", D0Evar("x"))', input_text="n\n")
        self.assertEqual(variable.returncode, 0)
        self.assertEqual(abstraction.returncode, 0)
        self.assertIn("x\nObserve value? [y/n]: ", variable.stdout)
        self.assertIn("(lam x. x)\nObserve value? [y/n]: ", abstraction.stdout)

    def test_one_shot_cli_can_observe_a_compiled_boolean(self):
        result = run_cli("true", input_text="y\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("(lam t. (lam f. t))", result.stdout)
        self.assertTrue(result.stdout.rstrip().endswith("true"), result.stdout)

    def test_one_shot_cli_observes_naturals_and_pairs(self):
        natural = run_cli("2 + 3", input_text="y\n")
        pair = run_cli("pair(2, true)", input_text="y\n")
        self.assertEqual(natural.returncode, 0, natural.stderr)
        self.assertEqual(pair.returncode, 0, pair.stderr)
        self.assertTrue(natural.stdout.rstrip().endswith("5"), natural.stdout)
        self.assertTrue(pair.stdout.rstrip().endswith("(2, true)"), pair.stdout)

    def test_cli_observes_church_notation_abbreviations(self):
        numeral = run_cli("NUM(2)", input_text="y\n")
        truth = run_cli("TRUE", input_text="y\n")
        self.assertEqual(numeral.returncode, 0, numeral.stderr)
        self.assertEqual(truth.returncode, 0, truth.stderr)
        self.assertTrue(numeral.stdout.rstrip().endswith("2"), numeral.stdout)
        self.assertTrue(truth.stdout.rstrip().endswith("true"), truth.stdout)

    def test_observation_prompt_rejects_answers_other_than_y_or_n(self):
        result = run_cli("true", input_text="maybe\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("OBSERVATION ERROR: please answer y or n", result.stdout)

    def test_cli_reports_parser_and_compiler_errors(self):
        malformed = run_cli("let x = in x")
        self.assertNotEqual(malformed.returncode, 0)
        self.assertIn("PARSER ERROR:", malformed.stdout)
        unsupported = run_cli('D0Eop2("/", D0Eint(1), D0Eint(0))')
        self.assertNotEqual(unsupported.returncode, 0)
        self.assertIn("COMPILER ERROR:", unsupported.stdout)

    def test_interactive_commands_and_eof(self):
        result = run_cli(input_text=":help\n\nD0Evar(\"x\")\nn\n:exit\n")
        self.assertEqual(result.returncode, 0)
        self.assertGreaterEqual(result.stdout.count("Enter source expressions"), 2)
        self.assertIn("source> x", result.stdout)

if __name__ == "__main__": unittest.main()
