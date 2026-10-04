# LAMBDA Web Front-End — Implementation Specification

## 1. Objective

Implement Assignment 04, described in `Assign04.md`, as a local web application for one user. Use TypeScript, HTML, and CSS for the frontend, and Python 3.12 or later for the backend.

`Assign04.md` is the main source of requirements. If it conflicts with this file, follow `Assign04.md`.

DO NOT read `MySolution/spec_init0.md`.
DO NOT read `MySolution/spec_init1.md`.
Do not create, read, write, or edit `AI-TRANSCRIPT.md`.

## 2. Project Structure

Keep the project under `MySolution/`:

- `source/`: all source code.
- `build/`: generated build files and auxiliary files.
- `tests/`: all test files.
- `README.md`: installation, startup, usage examples, and limitations.
- `ARCHITECTURE.md`: component diagram, responsibilities, dependencies, operation flow, and design decisions.
- `TESTING.md`: test steps, expected and actual results, and links between tests and requirements.
- `.gitignore`: files and directories Git should ignore, including installed npm modules.

Do not commit installed dependencies, virtual environments, caches, or reproducible generated files.

## 3. Technology and Integration

- Use TypeScript, HTML, and CSS for the browser interface.
- Use npm for the frontend build. Add the npm modules directory to `.gitignore`.
- Use Python 3.12 or later and the supplied `lambda1.py` for language operations.
- Use a local Python web server to serve the frontend and provide backend operations over HTTP.
- Document the interface between the frontend and backend.
- Bind the server to the loopback interface only.
- Document the exact commands to install dependencies, build, start, and test the application.
- Keep CSS and JavaScript in separate files; do not place them inside HTML files.

The backend must parse restricted LAMBDA constructor expressions into `d0exp` values. Never execute uploaded Python or shell code.

Support nested constructors, comments, and multiline input. Do not build a new parser for LAMBDA's concrete syntax.

## 4. MVC Architecture

Use `app.ts` to initialize the application and connect the model, view, controller, and backend interface. Keep application logic out of this file.

### `model.ts`

The model owns application state and rules. It must manage:

- Applied source text, source name, and a source revision number that increases with every accepted change.
- Operation results and the source revision each result belongs to.
- Generated-code artifact metadata, when available.
- Source validation and state changes.
- Clearing old results and artifacts after an accepted source change.

The model must not depend on HTML elements, DOM rendering, or HTTP request objects.

### `view.ts`

The view manages the interface and user interaction. It must provide:

- A source-selection menu and file input.
- An editable source area, with Apply changes and Discard changes controls.
- Lint, Interpret, Type-check, Compile, and Execute buttons, in that order.
- Busy status, source revision, and text results for operations.
- Literal display of source and output, preserving line breaks.
- Accessible labels, keyboard interaction, and text-based status indicators.

The view must not implement language analysis, interpretation, or business rules. It must not depend on how the backend runs language operations.

### `controller.ts`

The controller coordinates the application. It must:

- Handle source loading, editing, applying, and discarding.
- Validate source changes and update model state.
- Send operation requests through the backend interface.
- Associate each result with the correct source revision.
- Manage busy status, errors, timeouts, and retries.
- Update application state and refresh the view.

The controller must not render HTML or reimplement the interpreter.

## 5. Backend Contract

Define a replaceable backend interface with these operations:

- `lint(source)`
- `interpret(source)`
- `typecheck(source)`
- `compile(source)`
- `execute(artifact)`

Each result must identify the operation, source revision, outcome, and text message. Include structured data when useful, such as free-variable names, returned values, or artifact metadata.

Distinguish success, invalid input or language errors, runtime failures, backend failures, timeouts, and operations that are not implemented.

### Lint

Parse the source and call `d0exp_fvset`. Return the free-variable names as a Python `frozenset`. If the set is not empty, report an undeclared-variable error and list the names in a consistent order.

Apply the correct scope rules:

- A lambda parameter is in scope in the lambda body.
- A recursive function's name and parameter are in scope in its body.
- A `let` name is in scope in its body, but not in its initializer.
- Analyze both branches of a conditional.
- Unused bindings are not errors.

Lint must not evaluate the expression.

### Interpret

Parse the source and call `d0exp_evaluate` with an empty environment. Display the returned value as text.

Treat `D0V000()` as an error sentinel, including when it appears inside a pair. Report malformed input separately from runtime failures.

Lint and Interpret must work independently. Passing Lint does not guarantee that Interpret will succeed.

### Type-check and Compile

Provide the required controls and backend operations. Return clear not-implemented results. Do not report success or create fake artifacts.

### Execute

Execute is for generated code only. Keep it disabled until a valid artifact exists. Do not use the interpreter as a substitute.

Define the artifact interface for future compiler support. Associate each artifact with the source revision that produced it. Source changes and failed compilation must invalidate old artifacts.

## 6. Testing

Write automated tests for all six test categories in `Assign04.md`:

1. Free-variable analysis for every expression constructor and the relevant scope rules.
2. Lint behavior, including a test proving that Lint does not evaluate expressions.
3. Arithmetic, factorial, and Fibonacci interpretation, including malformed input and runtime failures.
4. Source loading, editing, replacement, and rejection of invalid changes.
5. Backend dispatch, placeholder operations, and Execute availability.
6. Busy-state handling, failures or timeouts, and retry behavior.

At least one model test must run without a browser or web server. At least one controller test must use a substitute backend without changing the view code.

Run and document a browser smoke test for all five operation buttons, source management, error recovery, disabled Execute, and literal display of HTML-like text.

Map automated and browser tests to requirements F1–F10 in `TESTING.md`.

## 7. Documentation and Completion

Provide a `README.md` containing:

- Runtime versions and dependencies.
- Exact installation, build, startup, and test commands.
- The local URL to open.
- Factorial and Fibonacci examples.
- An undeclared-variable example and how to correct it.
- An example of a runtime failure after Lint succeeds.
- Type-check and Compile placeholder results, and why Execute is disabled.
- Supported input syntax, execution limits, and known limitations.
- A 200–300 word reflection on MVC separation and future extensions.

Provide an `ARCHITECTURE.md` containing the actual module dependencies, a component diagram, the Load source → Lint → Interpret sequence, two design decisions and their tradeoffs, the backend interface, and the planned compiler and artifact design.

The project is complete when it meets all requirements in `Assign04.md`, all automated tests pass, browser checks are documented, and setup and tests work from a clean checkout.
