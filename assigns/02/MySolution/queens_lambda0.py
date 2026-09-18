"""A LAMBDA0 translation of ``eight_queens.dats``.

The ATS program counts all solutions by backtracking.  This translation uses
an eight-element nested pair as the board (the first element is the head and
the second element is the tail).  The terminal tail is never inspected.  A
board is therefore a value made entirely from integer and pair terms.

The search, board operations, and conflict checks below construct and execute
LAMBDA0 terms.  Python is used only to build terms and decode the final count.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.setrecursionlimit(100_000)

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lambda0 import (  # noqa: E402
    T0Mint, T0Mbtf, T0Mstr, T0Mvar, T0Mlam, T0Mfix, T0Mapp,
    T0Mpair, T0Mpfst, T0Mpsnd, T0Mif0, T0Mop1, T0Mop2,
    t0erm, t0erm_cbv_evaluate0,
)


N = 8


def app(function: t0erm, *arguments: t0erm) -> t0erm:
    """Build left-associated applications."""
    for argument in arguments:
        function = T0Mapp(function, argument)
    return function


def lam(*names: str, body: t0erm) -> t0erm:
    for name in reversed(names):
        body = T0Mlam(name, body)
    return body


def let_(name: str, value: t0erm, body: t0erm) -> t0erm:
    return T0Mapp(T0Mlam(name, body), value)


def pair_list(values: list[int]) -> t0erm:
    result: t0erm = T0Mstr("end")
    for value in reversed(values):
        result = T0Mpair(T0Mint(value), result)
    return result


def make_board_get() -> t0erm:
    i, xs = T0Mvar("i"), T0Mvar("xs")
    body = T0Mif0(
        T0Mop2("==", i, T0Mint(0)),
        T0Mpfst(xs),
        app(T0Mvar("get"), T0Mop2("-", i, T0Mint(1)), T0Mpsnd(xs)),
    )
    return T0Mfix("get", "i", lam("xs", body=body))


def make_board_set() -> t0erm:
    i, j, xs = T0Mvar("i"), T0Mvar("j"), T0Mvar("xs")
    body = T0Mif0(
        T0Mop2("==", i, T0Mint(0)),
        T0Mpair(j, T0Mpsnd(xs)),
        T0Mpair(
            T0Mpfst(xs),
            app(T0Mvar("set"), T0Mop2("-", i, T0Mint(1)), j, T0Mpsnd(xs)),
        ),
    )
    return T0Mfix("set", "i", lam("j", "xs", body=body))


def make_safety_test1() -> t0erm:
    i0, j0, i1, j1 = map(T0Mvar, ("i0", "j0", "i1", "j1"))
    # abs(i0-i1), expressed with the available integer primitives.
    delta_i = T0Mop2("-", i0, i1)
    abs_delta_i = T0Mif0(
        T0Mop2("<", delta_i, T0Mint(0)),
        T0Mop1("-", delta_i),
        delta_i,
    )
    delta_j = T0Mop2("-", j0, j1)
    abs_delta_j = T0Mif0(
        T0Mop2("<", delta_j, T0Mint(0)),
        T0Mop1("-", delta_j),
        delta_j,
    )
    body = T0Mif0(
        T0Mop2("!=", j0, j1),
        T0Mop2("!=", abs_delta_i, abs_delta_j),
        T0Mbtf(False),
    )
    return lam("i0", "j0", "i1", "j1", body=body)


def make_safety_test2() -> t0erm:
    i0, j0, bd, i = map(T0Mvar, ("i0", "j0", "bd", "i"))
    check_previous = app(
        T0Mvar("safe2"), i0, j0, bd, T0Mop2("-", i, T0Mint(1))
    )
    check_current = app(
        T0Mvar("safe1"), i0, j0, i,
        app(T0Mvar("get"), i, bd),
    )
    body = T0Mif0(
        T0Mop2(">=", i, T0Mint(0)),
        T0Mif0(check_current, check_previous, T0Mbtf(False)),
        T0Mbtf(True),
    )
    return T0Mfix("safe2", "i0", lam("j0", "bd", "i", body=body))


def make_search() -> t0erm:
    bd, i, j, nsol = map(T0Mvar, ("bd", "i", "j", "nsol"))
    bd1 = app(T0Mvar("set"), i, j, bd)
    finished = app(
        T0Mvar("search"), bd, i, T0Mop2("+", j, T0Mint(1)),
        T0Mop2("+", nsol, T0Mint(1)),
    )
    descend = app(T0Mvar("search"), bd1, T0Mop2("+", i, T0Mint(1)), T0Mint(0), nsol)
    try_next_column = app(T0Mvar("search"), bd, i, T0Mop2("+", j, T0Mint(1)), nsol)
    backtrack = app(
        T0Mvar("search"), bd, T0Mop2("-", i, T0Mint(1)),
        T0Mop2("+", app(T0Mvar("get"), T0Mop2("-", i, T0Mint(1)), bd), T0Mint(1)),
        nsol,
    )
    place_or_skip = T0Mif0(
        app(T0Mvar("safe2"), i, j, bd, T0Mop2("-", i, T0Mint(1))),
        T0Mif0(T0Mop2("==", T0Mop2("+", i, T0Mint(1)), T0Mint(N)), finished, descend),
        try_next_column,
    )
    body = T0Mif0(
        T0Mop2("<", j, T0Mint(N)),
        place_or_skip,
        T0Mif0(T0Mop2(">", i, T0Mint(0)), backtrack, nsol),
    )
    return T0Mfix("search", "bd", lam("i", "j", "nsol", body=body))


def build_program() -> t0erm:
    """Construct the closed term corresponding to ATS ``main0``."""
    board = pair_list([0] * N)
    term = app(T0Mvar("search"), board, T0Mint(0), T0Mint(0), T0Mint(0))
    # These let-bindings model the named ATS functions and close their refs.
    term = let_("search", make_search(), term)
    term = let_("safe2", make_safety_test2(), term)
    term = let_("safe1", make_safety_test1(), term)
    term = let_("set", make_board_set(), term)
    term = let_("get", make_board_get(), term)
    return term


PROGRAM = build_program()


_solution_count: int | None = None


def solve() -> int:
    global _solution_count
    if _solution_count is not None:
        return _solution_count
    result = t0erm_cbv_evaluate0(PROGRAM)
    if not isinstance(result, T0Mint):
        raise TypeError(f"queens program returned {result!r}")
    _solution_count = result.arg1
    return _solution_count


def is_safe_board(board: tuple[int, ...]) -> bool:
    """Python-side observation/checker for a decoded board."""
    return all(
        board[i] != board[j] and abs(i - j) != abs(board[i] - board[j])
        for i in range(len(board)) for j in range(i + 1, len(board))
    )


if __name__ == "__main__":
    print(solve())
