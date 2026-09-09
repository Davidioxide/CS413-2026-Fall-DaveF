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

    def assert_board_case(
        self,
        board: tuple[int, int],
        number_of_queens: int,
        expected_count: int,
    ) -> None:
        """Test one board/queen-count combination.

        Keeping the inputs as arguments lets one test exercise square boards,
        rectangular boards, impossible cases, and cases with fewer queens than
        rows without duplicating test logic.
        """
        rows, columns = board
        solutions = solve_board(rows, columns, number_of_queens)

        self.assertEqual(len(solutions), expected_count)
        self.assertTrue(
            all(
                len(solution) == number_of_queens
                and is_valid_placement(solution)
                for solution in solutions
            )
        )

    def test_board_and_queen_count_cases(self) -> None:
        cases = (
            ((1, 1), 1, 1),
            ((2, 2), 2, 0),
            ((3, 3), 3, 0),
            ((4, 4), 4, 2),
            ((5, 5), 5, 10),
            ((6, 6), 6, 4),
            ((7, 7), 7, 40),
            ((8, 8), 8, 92),
            ((9, 9), 9, 352),
            ((10, 10), 10, 724),
            ((4, 5), 3, 72),
            ((5, 6), 5, 40),
            ((6, 8), 4, 6196),
        )

        for board, number_of_queens, expected_count in cases:
            with self.subTest(board=board, number_of_queens=number_of_queens):
                self.assert_board_case(board, number_of_queens, expected_count)

    # all tests above passed, and all valid solutions are found during testing.


if __name__ == "__main__":
    unittest.main()
