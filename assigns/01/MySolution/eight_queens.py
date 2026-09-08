import sys


N = 8
sys.setrecursionlimit(1_000_000)


def print_dots(count: int) -> None:
    if count > 0:
        print(". ", end="")
        print_dots(count - 1)


def print_row(row: int) -> None:
    print_dots(row)
    print("Q ", end="")
    print_dots(N - row - 1)
    print()


def print_board(board: tuple[int, ...]) -> None:
    for row in board:
        print_row(row)
    print()


def board_get(board: tuple[int, ...], index: int) -> int:
    if 0 <= index < N:
        return board[index]
    return -1


def board_set(board: tuple[int, ...], index: int, column: int) -> tuple[int, ...]:
    if 0 <= index < N:
        updated_board = list(board)
        updated_board[index] = column
        return tuple(updated_board)
    return board


def safety_test1(row0: int, column0: int, row1: int, column1: int) -> bool:
    return (
        column0 != column1
        and abs(row0 - row1) != abs(column0 - column1)
    )


def safety_test2(
    row0: int, column0: int, board: tuple[int, ...], row: int
) -> bool:
    if row >= 0:
        if safety_test1(row0, column0, row, board_get(board, row)):
            return safety_test2(row0, column0, board, row - 1)
        return False
    return True


def search(board: tuple[int, ...], row: int, column: int, solution_count: int) -> int:
    if column < N:
        if safety_test2(row, column, board, row - 1):
            updated_board = board_set(board, row, column)
            if row + 1 == N:
                print(f"Solution #{solution_count + 1}:\n")
                print_board(updated_board)
                return search(board, row, column + 1, solution_count + 1)
            return search(updated_board, row + 1, 0, solution_count)
        return search(board, row, column + 1, solution_count)

    if row > 0:
        return search(board, row - 1, board_get(board, row - 1) + 1, solution_count)
    return solution_count


def main() -> None:
    initial_board = (0, 0, 0, 0, 0, 0, 0, 0)
    search(initial_board, 0, 0, 0)


if __name__ == "__main__":
    main()
