# LAMBDA Web Front-End — Implementation Specification

## 1. Objective

Implement Assignment 04, described in `Assign04.md`, as a local, single-user web application using TypeScript, HTML, and CSS for the frontend and Python 3.12 or later for the language backend.

`Assign04.md` is an authoritative source for the implementation of this project. If conflict does happen between the specification of `Assign04.md` and this spec file, prioritize the specification in `Assign04.md`

## 2. Project Structure

Keep all project files under `MySolution/`, and use the following sub directories

 - `MySolution/source/`: put all source code inside this directory.
 - `MySolution/build`: put all build files and aux files inside this directory.
 - `MySolution/tests`: put all test files inside this directory.
 - `README.md`: Installation, startup, usage, demonstrations, and limitations.
 - `ARCHITECTURE.md`: Component diagram, responsibilities, dependencies, operation flow, and design decisions.
 - `TESTING.md`: Test procedures, expected results, observed results, and requirement traceability.
 - `.gitignore`: ignore all unnecessary files, for example, the npm modules directory

Do not commit installed dependencies, virtual environments, caches, or generated files that can be reproduced.

Do not create, read, write, or edit `AI-TRANSCRIPT.md`.

## 3. Technology and Integration

- Use Typescript, HTML, and CSS for the browser interface.
- Use npm for build, and make sure to add the npm modules into `.gitignore`.
- Use Python 3.12 or later and the supplied `lambda1.py` for language operations.
- Use a local Python web server to serve the frontend and expose the backend operations through HTTP.
- Keep the frontend and backend communication behind a documented interface.
- Bind the server to the loopback interface only.
- Document exact dependency installation, build, startup, and test commands.
- DO NOT inline any CSS or script inside HTML

The backend must parse a restricted LAMBDA constructor expression into a d0exp. Do not execute arbitrary uploaded Python or shell code.

Support nested constructors, comments, and multiline input. Do not implement a new LAMBDA concrete-syntax parser.

## 4. MVC Architecture

Implement `app.ts` to initialize the application and connect the model, view, controller, and backend interface. Keep application-specific business logic out of this module.

### `model.ts`

Own and manage application state, including:

- Applied source text, source name, and monotonically increasing source revision.
- Operation results and their associated source revisions.
- Generated-code artifact metadata, when available.
- Source validation and state-transition rules.
- Invalidation of results and artifacts after accepted source changes.

The model must not depend on HTML elements, DOM rendering, or HTTP request objects.

### `view.ts`

Manage presentation and user interaction:

- Source-selection menu and file input.
- Editable source area and Apply changes / Discard changes controls.
- Lint, Interpret, Type-check, Compile, and Execute buttons, in that order.
- Busy status, source revision, and textual operation results.
- Literal rendering of source and output, preserving line breaks.
- Accessible labels, keyboard interaction, and text-based status indicators.

The view must not implement language analysis, interpretation, or business rules. It must not assume how the backend invokes the language tools.

### `controller.ts`

Coordinate application behavior:

- Handle source loading, editing, applying, and discarding changes.
- Validate source changes and invoke model state transitions.
- Dispatch operation requests through the backend interface.
- Associate results with the correct source revision.
- Coordinate busy-state handling, errors, timeouts, and retries.
- Update the state and arrange for the view to reflect it.

The controller must not contain HTML rendering logic or reimplement the language interpreter.

## 5. Backend Contract

Define a replaceable backend interface with operations equivalent to:

- `lint(source)`
- `interpret(source)`
- `typecheck(source)`
- `compile(source)`
- `execute(artifact)`

Each operation result must identify its operation, source revision, outcome, and textual message. Include structured data such as free-variable names, returned values, or artifact metadata when applicable.

Distinguish successful operations, invalid input or language errors, runtime failures, backend failures, timeouts, and not-implemented operations.

### Lint

Parse the source and call d0exp_fvset. Return a Python frozenset of free-variable names. Report nonempty sets as undeclared-variable errors, listing names in deterministic order.

Respect lexical scope for lambda parameters, recursive function names and parameters, and nonrecursive let bindings. A let binding does not scope over its initializer. Analyze both conditional branches. Unused bindings are not errors.

Lint must not evaluate the expression.

### Interpret

Parse the source and call d0exp_evaluate with an empty environment. Display the returned value as text.

Treat D0V000() as an error sentinel, including when it appears inside a pair. Distinguish malformed input from runtime failures.

Lint and Interpret may be invoked independently. Passing Lint does not guarantee successful evaluation.

### Type-check and Compile

Provide the required controls and backend entry points. Return explicit not-implemented results. Do not fabricate successful results or generated artifacts.

### Execute

Reserve Execute for generated code. Keep it disabled until a valid artifact exists. Do not use the interpreter as a substitute.

Define the intended artifact contract for future compiler integration. Artifacts must be associated with the source revision that produced them. Source changes and failed recompilation must invalidate stale artifacts.

## 6. Testing

Create automated tests covering all six test categories in Assign04.md:

1. Free-variable analysis for all expression constructors and relevant scope rules.
2. Lint behavior, including verification that Lint does not evaluate expressions.
3. Interpretation of arithmetic, factorial, and Fibonacci, including malformed input and runtime failures.
4. Source loading, editing, replacement, and rejection of invalid changes.
5. Backend dispatch, placeholder operations, and Execute availability.
6. Busy-state handling, failures or timeouts, and retry behavior.

At least one model test must run without a browser or web server. At least one controller test must use a substitute backend without changing view code.

Perform and document a browser smoke test covering all five controls, source-management behavior, error recovery, disabled Execute, and literal rendering of HTML-like text.

Map automated and browser tests to F1–F10 in TESTING.md.

## 7. Documentation and Completion Criteria

Provide `README.md` with:

- Runtime versions and dependencies.
- Exact installation, build, startup, and test commands.
- The local URL to open.
- Factorial and Fibonacci demonstrations.
- An undeclared-variable demonstration and correction.
- A runtime failure after successful Lint.
- Type-check and Compile placeholder results and the reason Execute is disabled.
- Supported input syntax, execution bounds, and known limitations.
- A 200–300 word reflection on MVC separation and future extensibility.

Provide ARCHITECTURE.md with actual module dependencies, a component diagram, a Load source → Lint → Interpret sequence, two design decisions with tradeoffs, the backend contract, and the planned compiler/artifact extension.

The implementation is complete when all required behavior in Assign04.md is implemented, automated tests pass, browser checks are documented, and setup and tests work from a clean checkout.