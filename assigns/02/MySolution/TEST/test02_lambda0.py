"""Tests for pairs, projections, and their interaction with LAMBDA0."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lambda0 import (  # noqa: E402
    T0Mint, T0Mbtf, T0Mvar, T0Mlam, T0Mfix, T0Mapp, T0Mpair,
    T0Mpfst, T0Mpsnd, T0Mop2, t0erm_cbv_evaluate0, t0erm_fvset,
    t0erm_size, t0erm_subst0,
)


class PairASTTests(unittest.TestCase):
    def test_size_and_free_variables(self):
        term = T0Mpfst(T0Mpair(T0Mvar("x"), T0Mpsnd(T0Mvar("y"))))
        self.assertEqual(t0erm_size(T0Mpair(T0Mint(1), T0Mint(2))), 3)
        self.assertEqual(t0erm_fvset(term), frozenset({"x", "y"}))
        self.assertEqual(t0erm_size(term), 5)

    def test_substitution_reaches_both_components_and_projection(self):
        term = T0Mpair(T0Mvar("x"), T0Mpfst(T0Mvar("x")))
        replacement = T0Mpair(T0Mint(4), T0Mint(5))
        self.assertEqual(
            t0erm_subst0(term, "x", replacement),
            T0Mpair(replacement, T0Mpfst(replacement)),
        )

    def test_substitution_respects_lambda_and_fix_binders(self):
        replacement = T0Mint(9)
        under_lambda = T0Mlam("x", T0Mpair(T0Mvar("x"), T0Mvar("y")))
        under_fix = T0Mfix("f", "x", T0Mpair(T0Mvar("f"), T0Mvar("y")))
        self.assertEqual(t0erm_subst0(under_lambda, "x", replacement), under_lambda)
        self.assertEqual(
            t0erm_subst0(under_lambda, "y", replacement),
            T0Mlam("x", T0Mpair(T0Mvar("x"), replacement)),
        )
        self.assertEqual(t0erm_subst0(under_fix, "f", replacement), under_fix)
        self.assertEqual(
            t0erm_subst0(under_fix, "y", replacement),
            T0Mfix("f", "x", T0Mpair(T0Mvar("f"), replacement)),
        )


class PairEvaluationTests(unittest.TestCase):
    def test_pair_components_and_projections(self):
        pair = T0Mpair(T0Mop2("+", T0Mint(1), T0Mint(2)), T0Mop2("*", T0Mint(3), T0Mint(4)))
        self.assertEqual(t0erm_cbv_evaluate0(pair), T0Mpair(T0Mint(3), T0Mint(12)))
        self.assertEqual(t0erm_cbv_evaluate0(T0Mpfst(pair)), T0Mint(3))
        self.assertEqual(t0erm_cbv_evaluate0(T0Mpsnd(pair)), T0Mint(12))

    def test_nested_and_mixed_pairs(self):
        value = T0Mpair(T0Mlam("x", T0Mvar("x")), T0Mpair(T0Mbtf(True), T0Mint(2)))
        result = t0erm_cbv_evaluate0(T0Mpsnd(value))
        self.assertEqual(result, T0Mpair(T0Mbtf(True), T0Mint(2)))

    def test_functions_accept_and_return_pairs(self):
        first = T0Mlam("p", T0Mpfst(T0Mvar("p")))
        make_pair = T0Mlam("x", T0Mpair(T0Mvar("x"), T0Mint(8)))
        term = T0Mapp(first, T0Mapp(make_pair, T0Mop2("+", T0Mint(2), T0Mint(3))))
        self.assertEqual(t0erm_cbv_evaluate0(term), T0Mint(5))

    def test_projection_requires_pair_and_evaluates_both_components(self):
        with self.assertRaises(TypeError):
            t0erm_cbv_evaluate0(T0Mpfst(T0Mint(1)))
        bad_second = T0Mop2("/", T0Mint(1), T0Mint(0))
        with self.assertRaises(ZeroDivisionError):
            t0erm_cbv_evaluate0(T0Mpfst(T0Mpair(T0Mint(1), bad_second)))

    def test_pair_evaluates_left_before_right(self):
        with self.assertRaises(ZeroDivisionError):
            t0erm_cbv_evaluate0(T0Mpair(T0Mop2("/", T0Mint(1), T0Mint(0)), T0Mbtf(True)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
