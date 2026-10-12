# MySolution test instructions

The implementation requires Python 3.12 or later. Run the commands below from
the assignment directory:

```sh
cd CS413-2026-Fall/CS413-2026-Fall-DaveF/assigns/05
```

This might depend on which diretcory is my assignment under, please adjust the directory address accordingly.

## Standard-library `unittest` suite

This suite is implemented in `MySolution/test_unittest.py` and uses classes
derived from `unittest.TestCase`. It requires no third-party packages.

```sh
python3 -m unittest discover -s MySolution -p 'test_unittest.py' -v
```

To use a specific Python installation, replace `python3` with its executable,
for example:

```sh
python3.12 -m unittest discover -s MySolution -p 'test_unittest.py' -v
```

## Pytest suite

The independent pytest-style suite is in `MySolution/test_pytest.py`. Install
pytest once with:

```sh
python3 -m pip install pytest
```

Run it with:

```sh
python3 -m pytest -q MySolution/test_pytest.py
```

For verbose output, use `-v` instead of `-q`:

```sh
python3 -m pytest -v MySolution/test_pytest.py
```

The two suites must be run independently. Running the unittest suite through
pytest does not count as the separate pytest suite required by the assignment.

## Full verification

Run both commands from the assignment directory before submission:

```sh
python3 -m unittest discover -s MySolution -p 'test_unittest.py' -v
python3 -m pytest -q MySolution/test_pytest.py
```

Both commands should finish successfully with exit status `0`.

# Design Explanation

## Visitor Result Types

Each visitor represents an operation on expressions, and its result type depends on that operation. In this design, `D0ExpVisitor[R]` uses the generic type parameter `R` to specify the return type of its methods. For example, `EvaluateVisitor` returns runtime values (`d0val`), while `FreeVariableVisitor` returns a `frozenset` of variable names. Each expression class implements `accept`, which dispatches to the corresponding method of the visitor and returns its result. This allows the same expression to be processed by different visitors without putting every operation inside the expression class itself.

## Context and Substitution

Context is represented by an environment, implemented as a linked structure of dataclasses. `ENVnil` represents an empty environment, while `ENVcns` stores a variable name, its associated value, and the rest of the environment. When entering a new scope, the interpreter extends the environment with a new binding while preserving the previous context. Variable lookup searches from the newest binding toward older bindings, so an inner binding takes precedence over an outer binding with the same name. Closures also retain the environment in which they were defined, preserving lexical scope. This approach carries contextual information through evaluation without requiring every expression to store the entire context itself.

## Scope-Respecting Renaming

Renaming must preserve the binding relationships in an expression. When renaming a variable, only occurrences bound by the target binding should change. For example, in `λx. x + (λx. x)`, renaming the outer `x` must not change the inner `x`, because the inner lambda introduces a new binding that shadows the outer one. Renaming must also avoid variable capture: if a new name would become bound by an inner expression, that inner binding must first be renamed to a fresh name. A renaming visitor can implement these rules by traversing the expression and tracking which bindings are in scope.

## Adding Operations versus Constructors

The visitor pattern makes it convenient to add a new operation to existing expression types. For example, a printing visitor can implement a method for each existing expression constructor without modifying those constructors. Adding a new expression constructor is different: the new expression must support visitor dispatch, and each existing visitor must implement the corresponding method to handle it. Therefore, this design makes adding operations relatively easy, but adding expression forms requires updating all visitors that process expressions.