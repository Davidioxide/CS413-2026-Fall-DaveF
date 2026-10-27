# Testing

From `assigns/06/`:

```text
PYTHONPATH=MySolution python3 -m unittest discover -s MySolution/tests -p 'test_*.py'
PYTHONPATH=MySolution python3 MySolution/demo.py
make -C MySolution all
python3 MySolution/app.py '2 + 3 * 4'
printf 'y\n' | python3 MySolution/app.py true
```

The CLI prints the compiled pure lambda term first. It then asks whether to
observe the value; enter `y` to print a primitive result such as `true`, `14`,
or `(2, true)`, and `n` to skip observation. EOF is treated as `n`.

The unittest suite is organized in two layers. Focused regression modules test
individual components, while `tests/test_assign06_requirements.py` is the
explicit checklist for the seven testing obligations in the Testing and
correctness argument section of `Assign06.md`.

| Assign06 obligation | Explicit test file and coverage |
| --- | --- |
| 1. Substitution shadowing and capture hazards | `test_assign06_requirements.py` and `test_core.py` test shadowing, alpha-renaming, replacement preservation, and free variables. |
| 2. CBV traversal and budgets | `test_assign06_requirements.py`, `test_target_budget.py`, and `test_cbv_control.py` test weak evaluation, deterministic counts, zero-step values, last-step completion, and exhaustion. |
| 3. Constructors/operators and encodings | `test_assign06_requirements.py` and `test_church_encodings.py` test source constructors, zero, predecessor, arithmetic, both comparison outcomes, booleans, and truth tables. |
| 4. Scope and immutability | `test_assign06_requirements.py`, `test_recursion_scope.py`, and `test_core.py` test nested scope, let initializers, both fix binders, coincident binders, open expressions, name collisions, and unchanged inputs. |
| 5. Strict and delayed control | `test_assign06_requirements.py` and `test_cbv_control.py` test divergent function arguments, let initializers, pair components, conditionals, and short-circuit operators. |
| 6. Demonstrations and diagnostics | `test_assign06_requirements.py` runs all DEMO-01 through DEMO-14; nested pairs, negative literals, and unsupported operators are also tested. |
| 7. Purity and compositional compilation | `test_assign06_requirements.py` and `test_compiled_purity.py` check pure output, closed combinators, source preservation, and that compilation does not call the evaluator. |

The dedicated checklist suite also verifies that the shared public evaluator
accepts both source ASTs and target terms. The focused tests additionally cover
parser behavior, CLI behavior, observer edge cases, target printing, and
source-path resolution.

The demo command is separate because it produces the required human-readable
report. It runs all fourteen mandatory examples, including factorial,
Fibonacci, nested data, short-circuit control, and bounded divergence. It shows
the source constructor, a generated pure-term prefix, execution status and
beta-step count, observation status and count, decoded result, and expected
result. Terminating examples use a 250,000-step execution and observation
budget; exhaustion cases are reported as exhaustion, not as proofs of
nontermination.
