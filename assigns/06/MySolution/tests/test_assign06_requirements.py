"""Explicit coverage of the numbered testing obligations in Assign06.md.

The feature-specific test modules contain focused regression tests.  This file
keeps the assignment checklist visible and verifies the end-to-end obligations
as a single unittest module.
"""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOLUTION = HERE.parent
sys.path.insert(0, str(SOLUTION))
from source_path import ASSIGN05
sys.path.insert(0, str(ASSIGN05))
from lambda1_vp import *

from church import ADD, FALSE, TRUE, Z, num
from compiler import CompileError, compile_expr
from demo import CASES
from evaluator import EvaluationError, evaluate, eval_source, eval_target
from observers import observe_bool, observe_num, observe_pair
from target import App, Lam, Var, free_vars, render, substitute


def apply2(fn, left, right):
    return App(App(fn, left), right)


def loop():
    return D0Eapp(
        D0Efix("loop", "x", D0Eapp(D0Evar("loop"), D0Evar("x"))),
        D0Eint(0),
    )


def compiled_result(source, kind, budget=250_000):
    run = eval_target(compile_expr(source), budget)
    if run.status != "complete":
        return run, None
    if kind == "num":
        observation = observe_num(run.value, budget)
    elif kind == "bool":
        observation = observe_bool(run.value, budget)
    else:
        observation = observe_pair(run.value, kind, budget, budget)
    return run, observation


class Assign06RequirementTests(unittest.TestCase):
    def test_01_substitution_shadowing_and_capture_preserve_replacement(self):
        shadowed = substitute(Lam("x", Var("x")), "x", Var("replacement"))
        self.assertEqual(shadowed, Lam("x", Var("x")))

        captured = substitute(Lam("y", App(Var("x"), Var("z"))), "x", Var("y"))
        self.assertIsInstance(captured, Lam)
        self.assertNotEqual(captured.name, "y")
        self.assertEqual(free_vars(captured), {"y", "z"})
        self.assertIsInstance(captured.body, App)
        self.assertEqual(captured.body.fn, Var("y"))
        self.assertEqual(captured.body.arg, Var("z"))

        direct = substitute(Lam("y", Var("x")), "x", Var("y"))
        self.assertEqual(direct, Lam("_a0", Var("y")))

        nested = substitute(
            Lam("y", Lam("y", App(Var("x"), Var("y")))),
            "x", Var("y"),
        )
        self.assertEqual(free_vars(nested), {"y"})
        self.assertIsInstance(nested, Lam)
        self.assertIsInstance(nested.body, Lam)
        self.assertNotEqual(nested.name, nested.body.name)

    def test_02_target_strategy_values_budget_and_determinism(self):
        identity = Lam("x", Var("x"))
        value = eval_target(identity, 0)
        self.assertEqual((value.status, value.steps), ("complete", 0))
        self.assertEqual(eval_target(Lam("x", App(identity, identity)), 0).steps, 0)

        term = App(App(identity, identity), identity)
        first = eval_target(term, 10)
        second = eval_target(term, 10)
        self.assertEqual(first, second)
        self.assertEqual(first.steps, 2)
        self.assertEqual(eval_target(App(identity, identity), 0).status, "exhausted")
        self.assertEqual(eval_target(App(identity, identity), 1).status, "complete")

        left_failure = D0Eop2(
            "+", D0Eapp(D0Eint(1), D0Eint(2)), D0Evar("right"),
        )
        with self.assertRaisesRegex(EvaluationError, "application of non-function"):
            eval_source(left_failure)

    def test_03_all_source_constructors_and_operators_have_expected_results(self):
        cases = [
            (D0Eint(0), "num", 0),
            (D0Ebtf(True), "bool", True),
            (D0Evar("x"), None, None),
            (D0Elam("x", D0Evar("x")), None, None),
            (D0Eapp(D0Elam("x", D0Eint(2)), D0Eint(1)), "num", 2),
            (D0Eop1("not", D0Ebtf(True)), "bool", False),
            (D0Eif0(D0Ebtf(False), D0Eint(1), D0Eint(2)), "num", 2),
            (D0Elet("x", D0Eint(2), D0Eop2("+", D0Evar("x"), D0Eint(1))), "num", 3),
            (D0Epair(D0Eint(2), D0Ebtf(True)), ("pair", "num", "bool"), (2, True)),
            (D0Epfst(D0Epair(D0Eint(2), D0Ebtf(True))), "num", 2),
            (D0Epsnd(D0Epair(D0Eint(2), D0Ebtf(True))), "bool", True),
        ]
        for source, kind, expected in cases:
            with self.subTest(source=type(source).__name__):
                target = compile_expr(source)
                if kind is None:
                    self.assertIsInstance(target, (Var, Lam, App))
                    continue
                run, observation = compiled_result(source, kind)
                self.assertEqual(run.status, "complete", run.message)
                self.assertEqual(observation.status, "complete", observation.message)
                self.assertEqual(observation.value, expected)

        binary_expected = {
            "+": 5, "-": 0, "*": 6,
            "<": True, "<=": True, ">": False, ">=": False,
            "==": False, "!=": True,
            "and": False, "or": True,
        }
        for operator, expected in binary_expected.items():
            with self.subTest(operator=operator):
                source = D0Eop2(operator, D0Eint(2), D0Eint(3)) if operator not in ("and", "or") else D0Eop2(operator, D0Ebtf(True), D0Ebtf(False) if operator == "and" else D0Ebtf(True))
                kind = "num" if operator in ("+", "-", "*") else "bool"
                _, observation = compiled_result(source, kind)
                self.assertEqual(observation.value, expected)

    def test_03b_compiled_comparisons_cover_both_outcomes(self):
        cases = {
            "<": ((1, 2, True), (2, 1, False)),
            "<=": ((1, 2, True), (2, 1, False)),
            ">": ((2, 1, True), (1, 2, False)),
            ">=": ((2, 1, True), (1, 2, False)),
            "==": ((2, 2, True), (2, 1, False)),
            "!=": ((2, 1, True), (2, 2, False)),
        }
        for operator, examples in cases.items():
            for left, right, expected in examples:
                with self.subTest(operator=operator, left=left, right=right):
                    source = D0Eop2(operator, D0Eint(left), D0Eint(right))
                    run, observation = compiled_result(source, "bool")
                    self.assertEqual(run.status, "complete", run.message)
                    self.assertEqual(observation.status, "complete", observation.message)
                    self.assertEqual(observation.value, expected)

        for operator in ("and", "or"):
            for left in (False, True):
                for right in (False, True):
                    with self.subTest(operator=operator, left=left, right=right):
                        source = D0Eop2(operator, D0Ebtf(left), D0Ebtf(right))
                        run, observation = compiled_result(source, "bool")
                        self.assertEqual(run.status, "complete", run.message)
                        self.assertEqual(observation.value, (left and right) if operator == "and" else (left or right))

    def test_04_scope_open_terms_collisions_and_immutability(self):
        source = D0Elet(
            "s", D0Evar("z"),
            D0Elam("x", D0Eop2("+", D0Evar("s"), D0Evar("free"))),
        )
        snapshot = copy.deepcopy(source)
        target = compile_expr(source)
        self.assertEqual(free_vars(target), {"z", "free"})
        self.assertEqual(source, snapshot)

        coincident = D0Eapp(D0Efix("f", "f", D0Evar("f")), D0Eint(3))
        run, observation = compiled_result(coincident, "num")
        self.assertEqual(run.status, "complete", run.message)
        self.assertEqual(observation.value, 3)

        for name in ("s", "z", "t", "f", "x"):
            self.assertEqual(free_vars(compile_expr(D0Evar(name))), {name})

        nested = D0Elet(
            "x", D0Evar("free"),
            D0Elam("x", D0Eop2("+", D0Evar("x"), D0Evar("free"))),
        )
        nested_snapshot = copy.deepcopy(nested)
        self.assertEqual(free_vars(compile_expr(nested)), {"free"})
        self.assertEqual(nested, nested_snapshot)

        initializer_scope = D0Elet("x", D0Evar("x"), D0Evar("x"))
        self.assertEqual(free_vars(compile_expr(initializer_scope)), {"x"})

    def test_05_strict_and_delayed_control(self):
        strict_cases = [
            D0Eapp(D0Elam("x", D0Eint(0)), loop()),
            D0Elet("x", loop(), D0Eint(2)),
            D0Epair(loop(), D0Eint(1)),
            D0Epair(D0Eint(1), loop()),
        ]
        for source in strict_cases:
            with self.subTest(source=type(source).__name__):
                self.assertEqual(eval_target(compile_expr(source), 5000).status, "exhausted")

        delayed = [
            (D0Eif0(D0Ebtf(True), D0Eint(1), loop()), "num", 1),
            (D0Eif0(D0Ebtf(False), loop(), D0Eint(2)), "num", 2),
            (D0Eop2("and", D0Ebtf(False), loop()), "bool", False),
            (D0Eop2("or", D0Ebtf(True), loop()), "bool", True),
        ]
        for source, kind, expected in delayed:
            with self.subTest(source=type(source).__name__):
                run, observation = compiled_result(source, kind, 5000)
                self.assertEqual(run.status, "complete", run.message)
                self.assertEqual(observation.value, expected)

    def test_06_all_fourteen_mandatory_demonstrations(self):
        self.assertEqual(len(CASES), 14)
        for identifier, source, kind, expected in CASES:
            with self.subTest(identifier=identifier):
                run, observation = compiled_result(source, kind)
                if expected is None:
                    self.assertEqual(run.status, "exhausted", identifier)
                else:
                    self.assertEqual(run.status, "complete", identifier)
                    self.assertEqual(observation.status, "complete", identifier)
                    self.assertEqual(observation.value, expected, identifier)

    def test_07_validation_is_complete_and_output_is_pure(self):
        invalid = [
            D0Eint(-1),
            D0Eop1("negate", D0Eint(1)),
            D0Eop2("/", D0Eint(1), D0Eint(0)),
            D0Eif0(D0Ebtf(True), D0Eint(1), D0Eop2("/", D0Eint(1), D0Eint(0))),
            D0Elam("x", D0Eop2("/", D0Eint(1), D0Eint(0))),
        ]
        for source in invalid:
            with self.subTest(source=type(source).__name__):
                with self.assertRaises(CompileError):
                    compile_expr(source)

        def check(term):
            self.assertIsInstance(term, (Var, Lam, App))
            if isinstance(term, Var):
                return
            if isinstance(term, Lam):
                return check(term.body)
            check(term.fn)
            check(term.arg)

        check(compile_expr(D0Eop2("+", D0Eint(2), D0Eint(3))))

    def test_08_combinators_observe_computed_values_and_nested_pairs(self):
        for term in (TRUE, FALSE, ADD, Z):
            self.assertEqual(free_vars(term), set())
        self.assertEqual(observe_num(num(0), 100).value, 0)
        self.assertFalse(observe_bool(FALSE, 100).value)
        computed = eval_target(apply2(ADD, num(2), num(3)), 100_000)
        self.assertEqual(computed.status, "complete")
        self.assertEqual(observe_num(computed.value, 100_000).value, 5)
        source = D0Epair(D0Epair(D0Eint(2), D0Ebtf(True)), D0Eint(3))
        run, observation = compiled_result(source, ("pair", ("pair", "num", "bool"), "num"))
        self.assertEqual(run.status, "complete")
        self.assertEqual(observation.value, ((2, True), 3))

    def test_09_shared_evaluator_accepts_both_source_and_target_inputs(self):
        source_result = evaluate(D0Eop2("+", D0Eint(2), D0Eint(3)))
        self.assertEqual(source_result, 5)
        target_result = evaluate(App(Lam("x", Var("x")), Lam("z", Var("z"))), 1)
        self.assertEqual((target_result.status, target_result.steps), ("complete", 1))


if __name__ == "__main__":
    unittest.main()
