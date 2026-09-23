# Assignment 2 Submission

This directory contains the LAMBDA0 interpreter extension, the translated
eight-queens program, and the associated regression tests.

## LAMBDA0 interpreter extension

`lambda0.py` adds support for the pair terms `T0Mpair`, `T0Mpfst`, and
`T0Mpsnd`. Pair terms are handled by the size, free-variable, substitution,
and call-by-value evaluation functions. Evaluation is left-to-right and
evaluates both components of a pair before a projection returns either the
first or second component. Consequently, projecting one component can still
evaluate—and fail because of—the other component.

The existing integer primitives are sufficient for the eight-queens
translation, so no new primitive operators were required.

## ATS2 translation

`queens_lambda0.py` translates `eight_queens.dats` into LAMBDA0 terms. The
translated `board_get`, `board_set`, `safety_test1`, `safety_test2`, and
`search` functions use the corresponding LAMBDA0 constructors. Recursive
functions use `T0Mfix`, applications use `T0Mapp`, and conditionals and
arithmetic use the existing LAMBDA0 constructs.

The ATS tuple board is represented as an eight-element nested pair. The head
stores one row value and the tail stores the remaining rows. Board lookup and
update recursively walk this representation. The translated search performs
the backtracking computation in LAMBDA0 and returns `92`, the known number of
solutions for the 8-by-8 queens problem. The Python `is_safe_board` helper is
only an independent checker; it is not used to perform the search.

## Running the tests

Run these commands from the assignment directory (the directory containing
`MySolution/`):

```sh
# Run every test in MySolution/TEST/.
python3 -m unittest discover -s MySolution/TEST -p 'test*.py' -v
```

The test files cover the following areas:

- `test02_lambda0.py`: pair construction, projections, substitution,
  evaluation order, and functions that accept or return pairs.
- `test03_queens.py`: the translated search, safety checks, and the expected
  solution count of `92`.
- `test04_lambda0_edge_cases.py`: nested pairs, recursive pair results, and
  additional substitution and evaluation regressions.
- `test05_queens_primitives.py`: board lookup/update, safety-check edge cases,
  and closure of the translated program.

To run one test module, use its filename with the same command. For example:

```sh
python3 -m unittest discover -s MySolution/TEST -p 'test02_lambda0.py' -v
python3 -m unittest discover -s MySolution/TEST -p 'test03_queens.py' -v
python3 -m unittest discover -s MySolution/TEST -p 'test04_lambda0_edge_cases.py' -v
python3 -m unittest discover -s MySolution/TEST -p 'test05_queens_primitives.py' -v
```

You can also run the test files directly from the assignment directory:

```sh
python3 MySolution/TEST/test02_lambda0.py
python3 MySolution/TEST/test03_queens.py
python3 MySolution/TEST/test04_lambda0_edge_cases.py
python3 MySolution/TEST/test05_queens_primitives.py
```

## Running the translated program

To execute the translated eight-queens search directly:

```sh
python3 MySolution/queens_lambda0.py
```

The program should report the result `92`. The implementation raises Python's
recursion limit because the direct substitution evaluator creates large
intermediate terms during the recursive search. The computed count is cached
for repeated use by the tests.
