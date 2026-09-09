"""Tests for eight_queens.py.

Run with:

    python3 test_eight_queens.py
"""

import contextlib
import io
import unittest

import eight_queens


def solve_board(rows: int, columns: int, queens: int) -> list[tuple[tuple[int, int], ...]]:
    """Find placements for ``queens`` queens on a rows-by-columns board."""
    solutions: list[tuple[tuple[int, int], ...]] = []

    def search(row: int, placement: list[tuple[int, int]]) -> None:
        if len(placement) == queens:
            solutions.append(tuple(placement))
            return
        if row == rows:
            return

        # Leave this row empty, if enough rows remain for the queens.
        if rows - row - 1 >= queens - len(placement):
            search(row + 1, placement)

        for column in range(columns):
            if all(
                eight_queens.safety_test1(
                    previous_row,
                    previous_column,
                    row,
                    column,
                )
                for previous_row, previous_column in placement
            ):
                placement.append((row, column))
                search(row + 1, placement)
                placement.pop()

    search(0, [])
    return solutions


def is_valid_placement(placement: tuple[tuple[int, int], ...]) -> bool:
    """Return whether a placement has no row, column, or diagonal conflicts."""
    for index, (row, column) in enumerate(placement):
        for other_row, other_column in placement[index + 1 :]:
            if not eight_queens.safety_test1(
                row, column, other_row, other_column
            ):
                return False
    return True


class EightQueensTests(unittest.TestCase):
    def test_original_8_by_8_program(self) -> None:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            solution_count = eight_queens.search((0,) * 8, 0, 0, 0)

        self.assertEqual(solution_count, 92)
        self.assertEqual(output.getvalue().count("Solution #"), 92)

    def test_different_board_size_and_queen_count(self) -> None:
        # Five queens on a 5-by-6 board: the board and queen count differ
        # from the original 8-by-8 problem.
        solutions = solve_board(rows=5, columns=6, queens=5)

        self.assertEqual(len(solutions), 40)
        self.assertTrue(all(is_valid_placement(solution) for solution in solutions))

    def test_fewer_queens_than_rows(self) -> None:
        solutions = solve_board(rows=4, columns=5, queens=3)

        self.assertTrue(solutions)
        self.assertTrue(all(len(solution) == 3 for solution in solutions))
        self.assertTrue(all(is_valid_placement(solution) for solution in solutions))

    def test_nine_queens_requires_a_9_by_9_board(self) -> None:
        # Nine non-attacking queens need at least nine rows and nine columns:
        # no two queens can share either coordinate.  A 9-by-9 board is the
        # first square board that can contain nine queens.
        solutions = solve_board(rows=9, columns=9, queens=9)

        self.assertEqual(len(solutions), 352)
        self.assertTrue(all(is_valid_placement(solution) for solution in solutions))


if __name__ == "__main__":
    unittest.main()
