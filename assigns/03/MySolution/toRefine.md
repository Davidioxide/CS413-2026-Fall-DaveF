# Items to Refine

This file records choices that may need refinement after stakeholder or
compiler-team feedback. They are not hidden requirements or claimed decisions.

## Organization

- The specification is comprehensive for the assignment, but the functional
  requirement tables are dense. During implementation planning, they could be
  split into separate subsections for the editor, compiler interaction, and
  test runner while keeping the IDs stable.
- The traceability matrix is intentionally compact. If the brief gains stable
  paragraph or line references, replace the section-level references with
  precise source anchors.
- The release checklist could become a separate project-readiness document if
  the course expects implementation planning beyond this assignment.

## Wording and terminology

- Confirm whether the course consistently uses “compile,” “interpret,” “run,”
  and “execute.” The requirements currently use “compiler service” to cover
  the evolving compiler/interpreter, but the final terminology should match
  the actual API.
- Replace “serializable result” with the exact supported value and encoding
  vocabulary after Q2 is answered.
- Replace “supported mainstream browser” with named browser versions after
  the setup environment is agreed upon.
- Confirm whether “source version” should be shown to users as a revision
  number, timestamp, hash, or a simpler label such as “result for previous
  edit.”
- The phrase “useful explanation” from the brief is represented through
  message, location, and failure-category requirements. Add an instructor-
  approved example of an acceptable explanation when diagnostic examples are
  available.

## Technical and scope decisions

- Define the compiler adapter's exact request/response schema, including AST
  input versus source input, optional artifacts, diagnostics, timeouts, and
  cancellation. This is the most important open dependency.
- Decide whether runtime limits belong to the browser adapter, the compiler,
  or both. A UI stop button may not be sufficient to terminate an unresponsive
  compiler process safely.
- Confirm the local persistence mechanism and whether saved data should survive
  browser-profile clearing or be exportable to a file.
- Decide whether local export/import of collections should be included in the
  first version even though online sharing is deferred.
- Specify how expected compilation errors are matched: error category, exact
  message, source location, or a deliberately less brittle predicate.
- Determine how a collection run behaves when one test hangs, including per-
  test timeout and cancellation rules.

## Review priorities

1. Resolve Q1–Q3 with the compiler team before finalizing the editor and test
   data model.
2. Resolve Q4–Q5 before claiming persistence and cancellation are operationally
   safe.
3. Confirm Q6–Q7 with the instructor before packaging examples or adding any
   sharing/export workflow.
