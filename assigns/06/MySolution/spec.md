Specificiations:

Read the following instructions, and then read `06/Assign06.md` and `06/REQUIREMENTS.md`, where instructions inside should be followed to finish this project of building a compiler that translates the source language into a pure, untyped lambda calculus.

1. Source of truth
    - As stated in `Assign06.md`, "Use Python 3.12 or later and the source AST and D0ExpVisitor interface in Assignment 5's lambda1_vp.py." refers to `assigns/05/lambda1_vp.py`.
    - Use `assigns/05/lambda1_vp.py` directly as the reference for the source AST and visitor interface. Do not modify or copy this file into the Assignment 6 solution, and do not import it as a library at runtime. Implement the Assignment 6 compiler as a visitor compatible with its AST classes and visitor interface.
    - Do not modify `assigns/05/MySolution/solution.py` and don't import it as a library directly. Instead, use its code as a reference when implement the Assignment 6 solution in `assigns/06/MySolution/`.
    - Follow `Assign06.md` and `REQUIREMENTS.md` whenever this specification conflicts with either file.
    - Do not modify or delete `MySolution/AI-TRANSCRIPT.md`, `MySolution/spec.md`, `Assign06.md`, and `REQUIREMENTS.md`.
    - No implementation should begin before the finishing reading `Assign06.md`, `REQUIREMENTS.md`, and `lambda1_vp.py`.
    - If any ambiguity occurs or a possible typo exits, instead of proceed to implementation, ask user first about clarification, and then continue the implementation.

2. Files to include
    - All created files should be under `MySolution`, but it is allowed to create sub directories under it.
    - Use `MySolution/tests/` as the directory to put all tests.
    - Python modules for the compiler, Church encodings and operations, shared evaluator, observers/decoders, and demonstrations.
    - Automated tests using unittest or pytest.
    - `MySolution/README.md` with setup, dependencies, Python version, exact commands, module overview, budgets, and limitations.
    - Include in `MySolution/Makefile`, the `all` and `clean` command to conveniently run and clean the tests/aux files.
    - In `MySolution/meta.md`, record all the meta information that can be helpful, for example, the version of python3.12. 
    - In `MySolution/test.md`, record the ways to test the program.

3. Methodologies
    - The program should be implemented as a CLI app, instead of a web app.
    - The CLI must provide a documented command to run all mandatory demonstrations and report each case's expected result, actual status, reduction steps, observation status, and decoded result when available. It must return a nonzero exit status when a required demonstration fails. Core compiler and evaluator functionality must remain callable as Python library functions; do not place all logic inside the CLI.
    - When implementing the capture-avoiding substitution, use renaming strategies.
    - Raise errors as needed. Every error information must begin with a meta information indicating where does the error occur. For example, if it happens at the compile time that compiler can't properly compile it, begin the error message with "COMPILER ERROR:".
    - When the input is malformed, such as following situations, raise a readable compiler error with readable meta information: 
        - Reject negative numeric literals and unsupported unary or binary operators.
        - Validate the entire AST during compilation, not only the branch that executes.
        - Include the offending constructor, literal, or operator in the error message.
        - Do not add a parser or general-purpose type checker.
        - Distinguish compilation errors, evaluation budget exhaustion, and invalid or incomplete observations.
        - Never report a decoded result when evaluation or observation has exhausted its budget.

4. Checklist
    - [ ] Only Var, Lam, and App appear in compiled target terms.
    - [ ] Free variables are preserved, source ASTs are not mutated, and substitution avoids capture.
    - [ ] All required source constructors and operators compile.
    - [ ] Conditionals and boolean short-circuit operations skip unselected divergent expressions.
    - [ ] Function arguments, let initializers, and both pair components obey call-by-value evaluation.
    - [ ] Recursion works through the required fixed-point construction.
    - [ ] The bounded target evaluator has deterministic step counts and correct exhaustion semantics.
    - [ ] Decoders handle alpha-renaming, nested pairs, incomplete reduction, and the expected result kind.
    - [ ] All 14 mandatory demonstrations produce their specified results or exhaustion statuses.
    - [ ] Tests verify that compilation does not invoke the evaluator.
    - [ ] All test, demo, and setup commands are reproducible from assigns/06/.
    - [ ] Run the full test suite and all mandatory demonstrations after integrating the components.
    - [ ] DESIGN.md documents every translation rule, predecessor construction, freshness policy, evaluation strategy, correctness argument, and design tradeoff.