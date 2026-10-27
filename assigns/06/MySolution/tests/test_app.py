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
        result = run_cli(input_text="\n".join(inputs + [":quit\n"]))
        self.assertEqual(result.returncode, 0, result.stderr)
        # Blank input produces adjacent prompts; take the text after the last
        # prompt on each line and ignore the final prompt emitted by :quit.
        responses = [line.split("source> ")[-1] for line in result.stdout.splitlines()
                     if "source> " in line and line.split("source> ")[-1]]
        self.assertEqual(len(responses), len(inputs), result.stdout[-1000:])
        for response in responses:
            self.assertTrue(response and "ERROR" not in response, response)
            self.assertTrue(response.startswith(("(", "_", "v", "x", "z", "s", "t", "f")), response)
            self.assertNotRegex(response, r"D0E(?:int|var|lam|app|op|if|let|pair|pfst|psnd|fix)")

    def test_one_shot_cli_and_exact_basic_outputs(self):
        variable = run_cli('D0Evar("x")')
        abstraction = run_cli('D0Elam("x", D0Evar("x"))')
        self.assertEqual(variable.returncode, 0)
        self.assertEqual(abstraction.returncode, 0)
        self.assertEqual(variable.stdout.strip(), "x")
        self.assertEqual(abstraction.stdout.strip(), "(lam x. x)")

    def test_cli_reports_parser_and_compiler_errors(self):
        malformed = run_cli("let x = in x")
        self.assertNotEqual(malformed.returncode, 0)
        self.assertIn("PARSER ERROR:", malformed.stdout)
        unsupported = run_cli('D0Eop2("/", D0Eint(1), D0Eint(0))')
        self.assertNotEqual(unsupported.returncode, 0)
        self.assertIn("COMPILER ERROR:", unsupported.stdout)

    def test_interactive_commands_and_eof(self):
        result = run_cli(input_text=":help\n\nD0Evar(\"x\")\n:exit\n")
        self.assertEqual(result.returncode, 0)
        self.assertGreaterEqual(result.stdout.count("Enter source expressions"), 2)
        self.assertIn("source> x", result.stdout)

if __name__ == "__main__": unittest.main()
