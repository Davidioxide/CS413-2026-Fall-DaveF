"""Tests for the LAMBDA0 translation of the ATS2 eight-queens program."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import queens_lambda0 as queens  # noqa: E402
from lambda0 import T0Mint, T0Mbtf, t0erm_cbv_evaluate0  # noqa: E402


class QueensTranslationTests(unittest.TestCase):
    def test_count_matches_original_ats_program(self):
        # eight_queens.dats prints/counts the 92 solutions of the 8x8 problem.
        self.assertEqual(queens.solve(), 92)

    def test_conflict_checker_logic(self):
        safe = queens.make_safety_test1()
        def check(i0, j0, i1, j1):
            return t0erm_cbv_evaluate0(
                queens.app(safe, T0Mint(i0), T0Mint(j0), T0Mint(i1), T0Mint(j1))
            )
        self.assertEqual(check(0, 0, 1, 2), T0Mbtf(True))
        self.assertEqual(check(0, 0, 1, 1), T0Mbtf(False))
        self.assertEqual(check(0, 0, 2, 0), T0Mbtf(False))

    def test_reference_solution_is_valid(self):
        # The original program enumerates rather than returns a board.  This
        # validates the same representation/check used by the translation.
        self.assertTrue(queens.is_safe_board((0, 4, 7, 5, 2, 6, 1, 3)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
