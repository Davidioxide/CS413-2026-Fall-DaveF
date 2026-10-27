"""Regression coverage for every interactive parser constructor and operator."""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from compiler import CompileError, compile_expr
from parser import parse
from target import App, Lam, Var, render

class ParserConstructorTests(unittest.TestCase):
    def test_every_constructor_notation_parses_and_compiles(self):
        cases = [
            'D0Eint(0)', 'D0Ebtf(true)', 'D0Evar("x")',
            'D0Elam("x", D0Evar("x"))',
            'D0Eapp(D0Elam("x", D0Evar("x")), D0Eint(1))',
            'D0Eop1("not", D0Ebtf(false))',
            'D0Eif0(D0Ebtf(true), D0Eint(1), D0Eint(2))',
            'D0Elet("x", D0Eint(1), D0Evar("x"))',
            'D0Epair(D0Eint(1), D0Ebtf(false))',
            'D0Epfst(D0Epair(D0Eint(1), D0Ebtf(false)))',
            'D0Epsnd(D0Epair(D0Eint(1), D0Ebtf(false)))',
            'D0Efix("f", "x", D0Evar("x"))',
        ]
        for text in cases:
            with self.subTest(text=text):
                self.assertIsNotNone(compile_expr(parse(text)))

    def test_every_binary_operator_notation_parses(self):
        operators = ("+", "-", "*", "<", "<=", ">", ">=", "==", "!=", "and", "or")
        for operator in operators:
            text = f'D0Eop2("{operator}", D0Eint(2), D0Eint(1))'
            with self.subTest(operator=operator):
                self.assertIsNotNone(compile_expr(parse(text)))

    def test_nested_constructor_forms(self):
        text = ('D0Elet("x", D0Epair(D0Eint(1), D0Ebtf(true)), '
                'D0Epfst(D0Evar("x")))')
        target = compile_expr(parse(text))
        self.assertIsInstance(target, (Var, Lam, App))

    def test_negative_literals_reach_compiler_diagnostics(self):
        for text in ('D0Eint(-1)', '-1'):
            with self.subTest(text=text):
                with self.assertRaisesRegex(CompileError, r"COMPILER ERROR:.*negative"):
                    compile_expr(parse(text))

    def test_existing_surface_syntax_remains_supported(self):
        self.assertEqual(render(compile_expr(parse('lam x. x'))), '(lam x. x)')
        self.assertIsNotNone(compile_expr(parse('fix f(x). f')))
        self.assertIsNotNone(compile_expr(parse('pair(fst(pair(1, true)), snd(pair(2, false)))')))

    def test_church_documentation_abbreviations_expand_to_source_literals(self):
        self.assertEqual(parse('NUM(2)').arg1, 2)
        self.assertEqual(parse('NUM (0)').arg1, 0)
        self.assertTrue(parse('TRUE').arg1)
        self.assertFalse(parse('FALSE').arg1)

if __name__ == "__main__": unittest.main()
