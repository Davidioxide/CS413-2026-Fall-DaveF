# Assignment 6 solution

Demo video:
https://drive.google.com/file/d/1Brwpgh8Fm4kd0JQCRQjTGM_DFwJlIHfF/view?usp=sharing

This is a Python 3.12+ command-line compiler and bounded Church-term evaluator.
It has no third-party dependencies. From `assigns/06/` run:

```text
PYTHONPATH=MySolution python3 MySolution/demo.py
PYTHONPATH=MySolution python3 -m unittest discover -s MySolution/tests -p 'test_*.py'
make -C MySolution all
```

The interactive compiler is `app.py`. From `assigns/06/`, launch it with:

```text
python3 MySolution/app.py
```

Then enter expressions such as `2 + 3 * 4`, `if true then 1 else 0`,
`let x = 3 in x + 4`, `lam x. x`, or `pair(2, true)`. Type `:help` or
`:quit`. A one-shot form is also available:

```text
python3 MySolution/app.py '2 + 3 * 4'
```

The parser is intentionally a small CLI convenience; library callers should
continue constructing Assignment 5 AST objects directly. After printing the
generated target term, the CLI asks `Observe value? [y/n]:`. Answer `y` to run
the bounded target evaluator and decode the result as a natural, boolean, or
nested pair inferred from the source expression; answer `n` to stop after the
target term. EOF behaves like `n`. For example:

```text
$ printf 'y\n' | python3 MySolution/app.py true
(lam t. (lam f. t))
Observe value? [y/n]: true
```

Observation uses the same pure target evaluator and the separate observation
budget below; it never replaces Church reduction with Python computation.
The specification’s notation abbreviations `NUM(n)`, `TRUE`, and `FALSE` are
also accepted by the CLI and expand to source literals.

The demo runs DEMO-01 through DEMO-14 and prints each expected value, execution
status and beta-step count, observation status/count, decoded value, source
constructor, and a generated pure-term prefix. Exit status is nonzero if a case
fails. The demo uses a 250,000-step execution/observation budget; source
evaluation is unbounded and is used only as a semantic oracle in tests.

`target.py` defines exactly `Var`, `Lam`, and `App`, printing, free variables,
and capture-avoiding substitution. `church.py` contains closed Church builders.
`evaluator.py` is the shared source/target evaluator. `compiler.py` implements
the Assignment 5 visitor method names without importing the Assignment 5 file.
`observers.py` decodes natural, boolean, and pair results. `demo.py` is the
batch demonstration runner. `parser.py` parses interactive source-language
expressions, `app.py` is the interactive compiler application, and
`source_path.py` resolves `assigns/05/lambda1_vp.py` independently of the
current working directory.

The test files are organized by requirement:

- `tests/test_church_encodings.py` independently tests exported Church
  combinator closure, arithmetic, predecessor, comparisons, booleans, pairs,
  successor, and zero testing.
- `tests/test_nested_pairs.py` tests recursive pair observation with mixed
  natural and boolean components.
- `tests/test_cbv_control.py` tests strict function arguments, let initializers,
  both pair components, conditionals, and short-circuit operators.
- `tests/test_recursion_scope.py` tests coincident fix binders, recursive scope,
  encoding-name collisions, and recursive execution.
- `tests/test_target_budget.py` tests deterministic reduction, immutability,
  zero-budget behavior, exhaustion, and final-step completion.
- `tests/test_observer_edges.py` tests alpha-renamed values, computed encodings,
  malformed observations, incomplete observations, and observation exhaustion.
- `tests/test_compiled_purity.py` recursively checks target purity for every
  source constructor/operator and verifies compilation does not invoke the
  evaluator.
- `tests/test_parser_constructors.py` covers every constructor notation,
  every supported binary operator, nested constructor expressions, existing
  surface syntax, and compiler diagnostics for negative literals.
- `tests/test_app.py` black-box tests the interactive CLI with 125 valid inputs.

The explicit mapping from `Assign06.md`'s Testing and correctness argument to
tests is:

| Assign06 obligation | Test coverage |
| --- | --- |
| 1. Substitution shadowing and capture | `test_assign06_requirements.py`, `test_core.py` |
| 2. Left-to-right/weak CBV, budgets, determinism | `test_assign06_requirements.py`, `test_target_budget.py`, `test_cbv_control.py` |
| 3. Every constructor/operator, zero, predecessor, comparisons, booleans | `test_assign06_requirements.py`, `test_church_encodings.py`, `test_compiled_purity.py` |
| 4. Scope, lets, lambdas, fix binders, open terms, collisions, immutability | `test_assign06_requirements.py`, `test_recursion_scope.py`, `test_core.py` |
| 5. Strict arguments/lets/pairs versus delayed conditionals and booleans | `test_assign06_requirements.py`, `test_cbv_control.py` |
| 6. Demonstrations, nested pairs, invalid literals/operators | `test_assign06_requirements.py`, `test_nested_pairs.py`, `test_parser_constructors.py` |
| 7. Pure output, closed combinators, no evaluator during compilation | `test_assign06_requirements.py`, `test_compiled_purity.py`, `test_church_encodings.py` |

`tests/test_assign06_requirements.py` is intentionally separate from the
focused regression tests so that the assignment's numbered obligations are
visible during review. It also runs the fourteen cases from `demo.py` as
unittest assertions. The demo command remains the human-readable report of
source, target prefix, budgets, statuses, counts, and answers.

The evaluator is intentionally weak CBV and bounded. Open target terms are
rejected for execution, although compilation and substitution support them.
Untyped malformed values are reported as observation errors rather than guessed.
The required presentation slides/video are not generated by this code; their
locations should be added here when supplied.
