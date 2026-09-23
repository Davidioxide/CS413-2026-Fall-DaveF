"""Additional tests for the LAMBDA0 eight-queens translation."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import queens_lambda0 as queens  # noqa: E402
from lambda0 import T0Mint, T0Mpair, t0erm_cbv_evaluate0, t0erm_fvset  # noqa: E402


class QueensPrimitiveTests(unittest.TestCase):
    def test_translated_program_is_closed(self):
        self.assertEqual(t0erm_fvset(queens.PROGRAM), frozenset())

    def test_board_get_reads_each_nested_pair_position(self):
        board = queens.pair_list(list(range(queens.N)))
        get = queens.make_board_get()
        for index in range(queens.N):
            with self.subTest(index=index):
                result = t0erm_cbv_evaluate0(
                    queens.app(get, T0Mint(index), board)
                )
                self.assertEqual(result, T0Mint(index))

    def test_board_set_changes_only_requested_position(self):
        board = queens.pair_list([0] * queens.N)
        set_board = queens.make_board_set()
        get = queens.make_board_get()
        updated = t0erm_cbv_evaluate0(
            queens.app(set_board, T0Mint(3), T0Mint(7), board)
        )
        self.assertIsInstance(updated, T0Mpair)
        for index, expected in enumerate([0, 0, 0, 7, 0, 0, 0, 0]):
            with self.subTest(index=index):
                result = t0erm_cbv_evaluate0(
                    queens.app(get, T0Mint(index), updated)
                )
                self.assertEqual(result, T0Mint(expected))

    def test_safety_checker_rejects_diagonal_and_column_conflicts(self):
        self.assertFalse(queens.is_safe_board((0, 1)))
        self.assertFalse(queens.is_safe_board((0, 2, 0)))
        self.assertFalse(queens.is_safe_board((0, 2, 4, 2)))
        self.assertTrue(queens.is_safe_board((0, 2, 4, 1, 3)))


if __name__ == "__main__":
    unittest.main(verbosity=2)
