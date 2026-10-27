# Assignment 6 requirements review

Reviewed against `06/Assign06.md` and `06/REQUIREMENTS.md` on 2026-10-26.

## Completed or substantially implemented

- Target AST contains only `Var`, `Lam`, and `App`.
- Target rendering, free-variable analysis, and capture-avoiding substitution
  are implemented.
- Weak, left-to-right call-by-value target evaluation has bounded execution,
  step counts, completion, and exhaustion statuses.
- Church booleans, naturals, pairs, predecessor, arithmetic, comparisons,
  boolean operations, projections, and the call-by-value fixed-point combinator
  are implemented.
- The compiler covers the required source constructors and operators, keeps
  compilation compositional, preserves source free variables, and uses delayed
  branches for conditionals and short-circuit boolean operations.
- Compiler-generated names use a deterministic freshness policy.
- Natural, boolean, and pair observers exist and report invalid/exhausted
  observations separately.
- The shared evaluator accepts both source ASTs and target terms.
- `app.py` provides an interactive CLI and `demo.py` runs the 14 required
  demonstrations.
- `tests/test_core.py` and `tests/test_app.py` exist; the CLI suite currently
  exercises 125 valid inputs. The full current suite passes.
- `README.md`, `DESIGN.md`, `meta.md`, `test.md`, and `Makefile` are present.

## Requirements not yet met or needing stronger evidence

### High priority

- [ ] Submit the required presentation slide deck as a PDF. No PDF is present
  under `MySolution/`.
- [ ] Submit the required 15–20 minute presentation recording, or add an
  accessible recording link to `README.md`. Neither is currently present.
- [ ] Make the demo print the complete generated target term, or save each
  complete term to a file. It currently prints only a truncated term prefix,
  while DEM-02 requires the generated pure term or a saved file containing it.
- [ ] Make the demo obtain terminating source-side expected results through the
  shared source evaluator, rather than relying only on hard-coded expected
  values. The current README describes source evaluation as an oracle, but the
  demonstration code does not visibly run it.

### Testing and verification gaps

- [x] Add explicit automated tests for every Church combinator independently,
  including both outcomes of every comparison, predecessor of zero, all boolean
  truth-table cases, and closure of every exported combinator.
- [x] Add explicit nested-pair observation tests, including a pair containing a
  pair and mixed natural/boolean component kinds.
- [x] Add explicit tests for pair call-by-value in both component positions,
  let-initializer divergence, function-argument divergence, and selected versus
  unselected conditional branches.
- [x] Add explicit tests for recursion scope hazards, coincident fix binders,
  source-name collisions with encoding names, and execution of `(fix f(f). f) 3`.
- [x] Add target evaluator tests for deterministic repeated runs and exact
  budget boundaries, including value-at-zero-budget, exhaustion-at-zero, and
  completion on the final permitted beta step.
- [x] Add malformed/incomplete observer tests and alpha-renamed computed
  encodings, including observation-budget exhaustion with no decoded result.
- [x] Add a structural test that recursively verifies every compiled result
  contains only target constructors.

### CLI/parser consistency

- [x] Add parser regression tests for every supported constructor notation,
  including `D0Elet`, `D0Efix`, all projections, all operators, nested
  constructors, and negative literals.

### Documentation and packaging cleanup

- [x] Update the README module description so `app.py` is identified as the
  interactive CLI and `demo.py` as the batch demonstration runner; it currently
  calls `demo.py` “the CLI” in one sentence.
- [ ] Before submission, remove Python `__pycache__` directories and compiled
  artifacts from the submitted tree. The current workspace contains tracked
  cache artifacts inherited from the repository; the submission requirement
  says not to submit caches.
- [ ] Add the final slide and recording locations to `README.md` once created.

## Current verification command

From `assigns/06/`:

```text
PYTHONPATH=MySolution python3 -m unittest discover -s MySolution/tests -p 'test_*.py'
PYTHONPATH=MySolution python3 MySolution/demo.py
```

Both currently pass for the implemented software, but passing tests do not
close the presentation deliverables or the evidence gaps listed above.
