"""Additional regression tests for pair-aware LAMBDA0 operations."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from lambda0 import (  # noqa: E402
    T0Mint,
    T0Mbtf,
    T0Mvar,
    T0Mlam,
    T0Mfix,
    T0Mapp,
    T0Mpair,
    T0Mpfst,
    T0Mpsnd,
    T0Mif0,
    T0Mop2,
    t0erm_cbv_evaluate0,
    t0erm_fvset,
    t0erm_size,
    t0erm_subst0,
)


class Lambda0PairRegressionTests(unittest.TestCase):
    def test_nested_pair_shape_is_preserved_by_ast_operations(self):
        term = T0Mlam(
            "outer",
            T0Mpair(
                T0Mvar("outer"),
                T0Mpfst(T0Mpair(T0Mvar("free"), T0Mvar("outer"))),
            ),
        )
        self.assertEqual(t0erm_fvset(term), frozenset({"free"}))
        self.assertEqual(t0erm_size(term), 7)

        replacement = T0Mpair(T0Mint(1), T0Mint(2))
        self.assertEqual(
            t0erm_subst0(term, "free", replacement),
            T0Mlam(
                "outer",
                T0Mpair(
                    T0Mvar("outer"),
                    T0Mpfst(T0Mpair(replacement, T0Mvar("outer"))),
                ),
            ),
        )

    def test_substitution_respects_both_fix_binders_inside_pairs(self):
        term = T0Mpair(
            T0Mfix("loop", "arg", T0Mpair(T0Mvar("loop"), T0Mvar("arg"))),
            T0Mvar("target"),
        )
        self.assertEqual(
            t0erm_subst0(term, "target", T0Mint(7)),
            T0Mpair(
                T0Mfix("loop", "arg", T0Mpair(T0Mvar("loop"), T0Mvar("arg"))),
                T0Mint(7),
            ),
        )

    def test_projection_evaluates_right_component_after_left_succeeds(self):
        term = T0Mpfst(
            T0Mpair(
                T0Mlam("x", T0Mvar("x")),
                T0Mop2("/", T0Mint(10), T0Mint(0)),
            )
        )
        with self.assertRaises(ZeroDivisionError):
            t0erm_cbv_evaluate0(term)

    def test_recursive_function_can_return_and_project_a_pair(self):
        make_pair = T0Mfix(
            "make",
            "n",
            T0Mif0(
                T0Mop2("==", T0Mvar("n"), T0Mint(0)),
                T0Mpair(T0Mint(4), T0Mint(9)),
                T0Mapp(T0Mvar("make"), T0Mop2("-", T0Mvar("n"), T0Mint(1))),
            ),
        )
        term = T0Mpsnd(T0Mapp(make_pair, T0Mint(3)))
        self.assertEqual(t0erm_cbv_evaluate0(term), T0Mint(9))

    def test_pair_can_contain_function_and_boolean_values(self):
        identity = T0Mlam("x", T0Mvar("x"))
        pair = T0Mpair(identity, T0Mbtf(False))
        self.assertEqual(t0erm_cbv_evaluate0(T0Mpfst(pair)), identity)
        self.assertEqual(t0erm_cbv_evaluate0(T0Mpsnd(pair)), T0Mbtf(False))


if __name__ == "__main__":
    unittest.main(verbosity=2)
