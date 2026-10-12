# Assignment 5 Implementation Specification

## Scope

All implementation, tests, and documentation for this assignment belong in
`MySolution/`. The assignment is to add pretty printing and capture-avoiding
substitution to the supplied visitor-based LAMBDA abstract syntax tree.

The due date is Tuesday, October 13, 2026.

## Source-of-truth hierarchy

The `README.md` files under `JAVA/` and `NODE/` are explicit sources of truth
for the supplied interpreter behavior, runtime expectations, and testing
conventions. If any other description conflicts with a relevant Java or Node
README, follow that README.

The assignment instructions in `Assign05.md` define the required deliverables
and grading requirements. For the actual Python program, AST fields,
constructors, binding semantics, operators, and interpreter behavior,
`lambda1.py` and `lambda1_vp.py` are the sources of truth.

`lambda1.py` and `lambda1_vp.py` are the authoritative sources for implementing
the LAMBDA program. In particular, `lambda1_vp.py` is authoritative for the
required Visitor design: expression nodes dispatch operations through
`accept`, and operations are implemented by visitor classes. The supplied
interpreter files and expression classes must not be modified.

The Java and JavaScript implementations are demonstrations only. They are not
alternative submission languages and must not replace the Python
implementation.

## Non-negotiable agent restrictions

- Under no condition may agents modify `AI-TRANSCRIPT.md`. It is a protected
  record and may only be created or changed by the student directly.
- Agents must not modify `lambda1.py`, `lambda1_vp.py`, or the supplied AST
  classes and interpreter code.
- Agents must not modify files outside `MySolution/` for the implementation,
  tests, or documentation.
- Do not add installed dependencies, compiled classes, generated artifacts, or
  caches to the submission.
- Do not replace visitor dispatch with a central chain of type or tag tests.
  Helper traversals over expressions must also use visitors.
- Neither required operation may evaluate, simplify, mutate, or otherwise
  change its input ASTs.

## Required implementation

### Pretty printing

Implement `PrettyPrintVisitor`, returning a string, and an entry point
equivalent to:

```python
d0exp_pretty(expression) -> str
```

The output must be single-line, have no leading or trailing whitespace, and
have no final newline. Use these exact formats:

| Expression | Output |
|---|---|
| `D0Eint(n)` | Decimal integer, with no suffix |
| `D0Ebtf(True)` / `D0Ebtf(False)` | `true` / `false` |
| `D0Evar(x)` | `x` |
| `D0Eop1(op, e)` | `(op P(e))` |
| `D0Eop2(op, e1, e2)` | `(P(e1) op P(e2))` |
| `D0Elam(x, body)` | `(lam x. P(body))` |
| `D0Efix(f, x, body)` | `(fix f(x). P(body))` |
| `D0Eapp(e1, e2)` | `(P(e1) P(e2))` |
| `D0Eif0(c, t, f)` | `(if P(c) then P(t) else P(f))` |
| `D0Elet(x, init, body)` | `(let x = P(init) in P(body))` |
| `D0Epair(e1, e2)` | `(pair P(e1) P(e2))` |
| `D0Epfst(e)` | `(fst P(e))` |
| `D0Epsnd(e)` | `(snd P(e))` |

Printing must not evaluate expressions. For example, printing `1 / 0` must
produce `(1 / 0)` without raising an arithmetic error.

### Capture-avoiding substitution

Implement `SubstitutionVisitor`, returning an expression, and an entry point
equivalent to:

```python
d0exp_substitute(expression, variable, replacement) -> expression
```

The operation computes `expression[variable := replacement]`, replacing only
free occurrences of the target. Insert the replacement as an expression
without recursively substituting inside it. Preserve both input ASTs; reusing
unchanged subtrees is allowed.

Binding rules:

- A lambda binds its parameter in its body.
- A `fix` binds both its function name and parameter in its body.
- If a `fix` function name equals its parameter, the parameter shadows the
  function name, matching the supplied evaluator.
- A nonrecursive `let` binds its name in the body, but not in the initializer.
- All other forms introduce no bindings.

At a binder, stop substitution where the target is bound. If the replacement
has a free variable that would be captured by a binder in a region where
substitution occurs, alpha-rename that binder and exactly the occurrences it
binds. Renaming must respect nested shadowing; global string replacement is
incorrect.

For `let`, always substitute the initializer, including when its bound name is
the target. Alpha-renaming a `let` changes bound occurrences in the body only,
never occurrences in the initializer.

### Fresh-name policy

Use a deterministic, documented, counter-based fresh-name policy. Generated
names must avoid all variable and binder names in the original expression, all
names in the replacement, the substitution target, and names already generated
during the current call. Free-variable names alone are insufficient.

Avoid unnecessary alpha-renaming when no substitution can occur in the
binder's scope. Any deterministic names are acceptable if the result is
alpha-equivalent and the policy is documented.

## Required tests

Create two independent Python test suites in `MySolution/`:

1. A standard-library `unittest` suite with classes derived from
   `unittest.TestCase`.
2. A separate pytest suite using pytest-style test functions and plain
   `assert` statements. Running the unittest suite through pytest does not
   satisfy this requirement.

Both suites must independently cover:

- Exact pretty-printing for every constructor, nested expressions, negative
  and large integers, and both booleans.
- Substitution through every constructor, matching/nonmatching variables, and
  replacement expressions containing the target.
- Lambda shadowing, both `fix` binders, `let` shadowing, and `fix f(f, ...)`.
- Capture avoidance for lambda, `let`, and each distinct `fix` binder,
  including replacements conflicting with both `fix` binders.
- Nested shadowing during alpha-renaming and collisions with existing or
  previously generated names.
- The distinction between a `let` initializer and body.
- Input-AST preservation, deterministic repeated results, and no evaluation
  during either operation.
- The free-variable property:

  ```text
  FV(e[x := r]) = (FV(e) - {x}) union FV(r)
  ```

  when `x` occurs free in `e`; when it does not, the result must be
  alpha-equivalent to `e` and have the same free variables. Structural or
  exact-output tests are also required; the free-variable property alone is
  insufficient.

## Required documentation

Create `MySolution/README.md` containing:

- Python 3.12 or later requirement.
- Setup commands, including installation of pytest.
- Separate commands to run the unittest and pytest suites from the assignment
  directory.
- Usage examples for both operations.
- The deterministic fresh-name policy and known limitations.
- A 300–500 word design explanation covering visitor result types, context
  carried by substitution, scope-correct renaming, and why adding an
  operation differs from adding an expression constructor in the visitor
  design.

`AI-TRANSCRIPT.md` is also a required submission artifact, but it is protected
by the restriction above: agents must not create, edit, or rewrite it. The
student must supply it, recording AI tools used, important prompts and
suggestions, and how the output was reviewed and tested. If no AI was used,
the file must say so.

## Verification and handoff

Verify both documented test commands from the assignment directory. Confirm
that only intended files under `MySolution/` are present and that no compiled
classes, installed packages, or caches are included. The implementation is
complete only when the visitors, entry points, tests, documentation, and
student-maintained AI transcript are all present and the two test suites pass
independently.
