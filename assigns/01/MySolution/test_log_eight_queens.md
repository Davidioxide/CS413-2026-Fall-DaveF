# Eight Queens Test Log

Date: 2026-09-08

## Test command

```text
python3 -m unittest -v test_eight_queens.py
```

Result: **PASS** — 2 tests ran in 0.174 seconds.

## Automated test samples

`test_board_and_queen_count_cases` checks the exact number of placements and
verifies that every returned placement has the requested number of queens and
contains no row, column, or diagonal conflicts. The board is recorded as
`(rows, columns)`.

| Board | Queens | Expected placements | Result |
|---|---:|---:|---|
| (1, 1) | 1 | 1 | PASS |
| (2, 2) | 2 | 0 | PASS |
| (3, 3) | 3 | 0 | PASS |
| (4, 4) | 4 | 2 | PASS |
| (5, 5) | 5 | 10 | PASS |
| (6, 6) | 6 | 4 | PASS |
| (7, 7) | 7 | 40 | PASS |
| (8, 8) | 8 | 92 | PASS |
| (9, 9) | 9 | 352 | PASS |
| (10, 10) | 10 | 724 | PASS |
| (4, 5) | 3 | 72 | PASS |
| (5, 6) | 5 | 40 | PASS |
| (6, 8) | 4 | 6196 | PASS |

The sample includes the original 8-by-8 problem, the standard no-solution
2-by-2 and 3-by-3 cases, larger square boards, rectangular boards, and cases
where the number of queens is smaller than the number of rows.

## Discovered tests

```text
test_board_and_queen_count_cases ... ok
test_original_8_by_8_program ... ok

Ran 2 tests ... OK
```
