# Assignment 2 submission

## Interpreter extension

`lambda0.py` adds recursive support for `T0Mpair`, `T0Mpfst`, and
`T0Mpsnd` in size, free-variable, substitution, and call-by-value
evaluation. Pair evaluation is left-to-right and evaluates both components,
including the component not selected by a projection. The existing integer
comparison operators are sufficient for the queens translation; no new
primitive operators were needed.

Tests are in `TEST/test02_lambda0.py`. Run them from this directory with:

```sh
python3 -m unittest discover -s MySolution/TEST -p 'test02_lambda0.py'
```

The existing starter tests were also run against this copy of the interpreter.

## ATS2 translation

The source translated is `eight_queens.dats`, copied from
`../01/MySolution/eight_queens.dats`. Its `board_get`, `board_set`,
`safety_test1`, `safety_test2`, and `search` functions are represented by
LAMBDA0 functions. Recursive functions use `T0Mfix`; function calls use
`T0Mapp`; conditionals and arithmetic use the corresponding LAMBDA0
constructors.

The ATS tuple board is represented as an eight-element nested pair. The head
is the value for one row and the tail is the remaining nested pair. `get` and
`set` recursively walk this representation. The translated program follows
the ATS backtracking order and returns the solution count, rather than doing
the search in Python. It evaluates to `92`, matching the original ATS2
program's count for an 8-by-8 board. The Python `is_safe_board` function is
only an observation/checker, not part of the search.

Run the translation and its tests with:

```sh
python3 MySolution/queens_lambda0.py
python3 -m unittest discover -s MySolution/TEST -p 'test03_queens.py'
```

The call-by-value interpreter evaluates complete pairs before projections,
so a projection can evaluate a board component that it does not return. This
also means the direct substitution evaluator constructs large intermediate
terms for recursive search; `queens_lambda0.py` raises Python's recursion
limit for that expected implementation cost and caches the single computed
count for its tests.

The implementation was reviewed by checking each translated function against
the corresponding ATS2 branch structure, testing pair operations separately,
running the existing interpreter tests, and verifying the known ATS2 result
of 92 solutions.
