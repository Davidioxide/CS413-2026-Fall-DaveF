# LAMBDA Browser Environment Requirements Specification

## 1. Purpose

This document specifies a small, local web-based environment for writing,
compiling, running, inspecting, saving, and testing LAMBDA programs. It turns
the instructor's informal brief into requirements that can guide design,
implementation, and evaluation.

The environment is a client-facing workbench around a separately provided
LAMBDA compiler/interpreter. It is not a replacement for the compiler and
does not define the LAMBDA language, its final source notation, or its
implementation. The specification uses the term **compiler service** for the
compiler capability supplied to the environment; that capability may include
compilation, interpretation, or both.

## 2. Stakeholders, users, and goals

| Stakeholder | Main goals |
| --- | --- |
| Students writing LAMBDA | Enter or import programs, run examples, understand errors, and save work for later. |
| Students testing compiler changes | Create named expected-result and expected-error tests, rerun a collection, and investigate regressions. |
| Course instructor | Demonstrate examples efficiently in lectures, inspect compiler output when useful, and prepare/share examples if that feature is available. |
| Compiler/interface developers | Connect an evolving compiler through a defined interface and use representative responses before the real compiler is ready. |
| Course staff or evaluator | Set up the local system, verify its behavior, and maintain example data. |

## 3. Scope and boundaries

### 3.1 First-version scope

The first version includes:

- A browser interface that runs locally on a student's or instructor's computer.
- Editing, creating, importing, and locally saving LAMBDA programs.
- Starter examples that can be selected and copied for independent editing.
- Separate compile and run actions.
- Display of normal results, compiler output, source locations, and distinct
  compile/run/environment failure states.
- Optional inspection of available abstract syntax tree (AST) or generated
  code output.
- Cancellation of a long-running operation.
- Named test cases and collections containing expected values or expected
  compilation errors.
- Collection execution with per-test outcomes and an overall summary.
- Persistence across refreshes and later local sessions.
- A replaceable interface that can use sample responses during development and
  later connect to the actual compiler.
- Keyboard-operable primary actions, understandable text messages, and use of
  cues other than color alone.

### 3.2 Out of scope for the first version

The following are explicitly outside the initial boundary:

- Development of the LAMBDA compiler or interpreter itself.
- A public hosted website, cloud synchronization, or user accounts.
- Simultaneous collaborative editing or multi-user conflict resolution.
- Required online sharing of collections. Export/import may be considered as a
  later enhancement if the stakeholder confirms the desired format.
- A full integrated development environment, advanced debugging, version
  control, or sophisticated visual effects.
- A promise to support every browser, operating system, or future LAMBDA
  notation before those interfaces are defined.

The testing environment submits programs to and presents responses from the
compiler; it does not determine whether a program is semantically correct or
implement compilation and execution itself.

## 4. Clarification questions and current treatment

No stakeholder answers were supplied with the brief. The questions below
remain open. The specification records assumptions so that work can proceed
without presenting guesses as decisions.

| # | Clarification question | Why the answer matters | Current treatment |
| --- | --- | --- | --- |
| Q1 | What exact source notation and input/output conventions will the compiler accept? | Editor examples, import validation, run inputs, and test expectations depend on the language representation. | **Unresolved.** Requirements use “LAMBDA source” and keep notation-specific details behind the compiler interface. |
| Q2 | Should “run” mean compile-then-execute, interpretation of an AST, or both, and what result types/serialization are supported? | The run form, expected-value test format, and displayed results cannot be finalized without a result contract. | **Assumption A1:** the compiler adapter exposes separate compile and run operations and a serializable result representation. |
| Q3 | What compiler response schema is available for diagnostics, AST, generated code, and source locations? | The environment needs stable fields for messages, locations, optional artifacts, and failure categories. | **Assumption A2:** responses can identify status and include optional location and artifact fields; exact schema is a dependency to document. |
| Q4 | Where and in what format should programs, tests, and collections persist? | This affects refresh behavior, later sessions, portability, recovery, and setup instructions. | **Assumption A3:** first-version persistence is local to the machine/browser profile and uses a documented storage format. |
| Q5 | What are the permitted runtime/resource limits, and can the compiler enforce them? | A stop control alone may not protect the local machine from infinite or resource-intensive programs. | **Unresolved.** The UI must offer cancellation; a compiler-side timeout/resource policy is recommended but not stakeholder-approved. |
| Q6 | What starter examples and sample compiler responses should be distributed? | Examples and demonstrations need known content and must be clearly distinguished from real results. | **Assumption A4:** a small bundled set includes at least one successful program, one editable-input example, and representative diagnostic/sample responses. |
| Q7 | Is collection sharing needed in version one, and if not, should export/import be included as a transition feature? | The brief calls sharing useful but nonessential; this changes the boundary and data format. | **Assumption A5:** online sharing is deferred; export/import remains a candidate enhancement, not a required feature. |

## 5. Priorities and requirement conventions

Priority labels are:

- **Must:** required for a useful and evaluable first version.
- **Should:** important, but can follow the minimum viable workflow if schedule
  or compiler limitations require it.
- **Could:** desirable later work and not required for first-version acceptance.

Each requirement has one behavior and a verification-oriented wording. Where a
measurable threshold is needed but absent from the brief, it is identified as
a proposal rather than a stakeholder commitment.

## 6. Functional requirements

### 6.1 Program editing and persistence

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-01 | Must | The system shall let a user create a new editable LAMBDA program and enter, paste, select, and modify its source text. |
| FR-02 | Must | The system shall provide bundled starter examples that a user can select and open without manually entering their source. |
| FR-03 | Must | The system shall open a starter example as a separate editable working copy, preserving the original starter content for later reuse. |
| FR-04 | Must | The system shall let a user import a program from a local file and shall report an understandable error without discarding the current work when the file cannot be read or is not accepted. |
| FR-05 | Must | The system shall let a user save a named program locally and reopen it in a later browser session on the same machine. |
| FR-06 | Must | The system shall preserve saved programs and test collections across a page refresh and shall provide a way to identify or recover unsaved changes before a destructive navigation or replacement. |

### 6.2 Compilation, execution, and results

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-07 | Must | The system shall provide a compile action that sends the current program version to the compiler service and displays whether compilation succeeded or failed. |
| FR-08 | Must | The system shall provide a run action that sends the current program version to the compiler service for execution and displays the returned result or execution failure. |
| FR-09 | Must | The system shall distinguish at least compile errors, execution failures, compiler-connection/environment failures, cancelled operations, and successful results using text and structure rather than color alone. |
| FR-10 | Must | When a compiler response includes a source location, the system shall associate the diagnostic with the relevant source position and provide a way to find or highlight that position. |
| FR-11 | Should | The system shall allow a user to inspect available compiler artifacts, such as an AST or generated code, without displaying those details in the primary simple-result view. |
| FR-12 | Must | The system shall provide a way to cancel an in-progress compile or run operation and shall show that the operation was cancelled when cancellation is requested. |
| FR-13 | Must | The system shall keep the page's editing and navigation controls usable while a compile or run operation is in progress. |
| FR-14 | Must | The system shall associate every displayed compile/run response with the program version that produced it, and shall identify or discard a response that is no longer for the current source after an edit. |
| FR-15 | Must | If the compiler service cannot be reached or returns an environment-level failure, the system shall explain that the operation could not be completed, preserve the user's program, and allow the user to retry. |
| FR-16 | Must | The system shall clearly label a demonstration response based on sample data as sample or simulated and shall not present it as an actual compiler result. |

### 6.3 Test collections

| ID | Priority | Requirement |
| --- | --- | --- |
| FR-17 | Must | The system shall let a user create, name, edit, save, and delete a test case containing a LAMBDA program and one expectation: an expected serializable result or an expected compilation error. |
| FR-18 | Must | The system shall let a user group named test cases into a collection and run the collection against the configured compiler service. |
| FR-19 | Must | For each collection run, the system shall show each test's pass, fail, error, or cancelled status and enough actual-versus-expected or diagnostic detail to investigate a non-passing test. |
| FR-20 | Must | The system shall continue running other eligible tests after one test fails, errors, or produces an unexpected result, and shall provide an overall summary after the collection run. |

## 7. Quality requirements

The brief does not provide numeric targets for these qualities. The response
and accessibility thresholds below are proposed acceptance targets and should
be confirmed with the stakeholder.

| ID | Priority | Quality requirement and proposed assessment |
| --- | --- | --- |
| QR-01 | Must | The primary workflow (select/edit, compile or run, and read the result) shall be operable with a keyboard, with visible focus and logical focus order. Assessment: perform the workflow without a mouse and verify that every primary control is reachable and identifiable. |
| QR-02 | Must | Meaningful status and error information shall not depend on color alone; each state shall include text, an icon, structure, or another non-color cue. Assessment: inspect success, compile-error, run-failure, connection-failure, and test-summary states in a monochrome view. |
| QR-03 | Should | For ordinary local interface actions that do not wait for the compiler, the interface should acknowledge the action within 1 second under normal supported-machine conditions. This is a proposed target, not a stakeholder-provided guarantee. |
| QR-04 | Must | A compiler operation that is still running shall not block ordinary editing and navigation, and a user-requested cancellation shall transition to a visible final state within a proposed 2 seconds when the adapter is responsive. The compiler's own termination time remains a dependency. |
| QR-05 | Must | A person following the project setup instructions on a supported browser shall be able to start the local environment and open the interface without an account or public network deployment. The supported browser list and exact setup time are unresolved and must be documented before release. |

## 8. External interfaces and dependencies

### 8.1 Browser and local host

The system requires a supported mainstream browser and a local launch/setup
procedure. The exact browser versions are a release decision. Local storage or
an equivalent local persistence facility is required for saved programs and
collections. The first version does not require accounts or a hosted backend.

### 8.2 Compiler service interface

The environment depends on a compiler adapter/API supplied by the compiler
team. At minimum, the integration contract must define:

1. compile input: a program version and its LAMBDA source or AST representation;
2. run input: the program representation and any required input values;
3. success and failure status values;
4. result representation for supported values such as integers and Booleans;
5. diagnostics containing a human-readable message and, when available, a
   source location;
6. optional AST and generated-code artifacts;
7. connection, timeout, and cancellation behavior; and
8. a way to identify sample responses during interface development.

The source notation and AST boundary are unresolved because the brief says the
notation is still being discussed and the current interpreter uses Python ASTs.
The adapter must isolate those changes so that the browser workflow does not
need to be redesigned when the real compiler becomes available.

### 8.3 Files and sample data

The system needs a defined policy for accepted local program files and for
storing named programs, tests, collections, and sample responses. The exact
file format is an assumption and must be documented as part of implementation
setup. Import/read errors must be surfaced without overwriting current work.

## 9. Acceptance criteria

These are future checks, not test results from an implemented system. Each
scenario names the requirement, starting condition, action, and observable
expected result.

### AC-01 — Starter example isolation (FR-02, FR-03)

- **Starting condition:** The interface is open and contains a bundled
  factorial example.
- **Action:** Select the example, change its input/source, save or run the
  modified copy, then select the original example again.
- **Expected result:** The modified copy is editable and usable, while the
  original example remains unchanged and can be selected again.

### AC-02 — Compile diagnostic navigation (FR-07, FR-09, FR-10)

- **Starting condition:** The current source contains a deliberate syntax
  error, and the compiler returns a diagnostic with a line and column.
- **Action:** Choose Compile.
- **Expected result:** The result is labeled as a compilation error, shows a
  useful message and location, and lets the user find or highlight the
  reported source position. It is not labeled as a run failure.

### AC-03 — Successful run with version identity (FR-08, FR-14)

- **Starting condition:** A valid program is open.
- **Action:** Start Run, edit the source before the operation returns, and then
  inspect the response.
- **Expected result:** The response identifies the source version that produced
  it. The UI either marks it stale relative to the edited source or prevents
  it from being mistaken for a result of the new source.

### AC-04 — Unreachable compiler (FR-15)

- **Starting condition:** The compiler service is stopped or unreachable, and
  the user has unsaved source text.
- **Action:** Choose Compile or Run.
- **Expected result:** The system identifies an environment/connection failure,
  does not claim that the program is wrong, preserves the source, and exposes a
  retry path.

### AC-05 — Cancellation and usable page (FR-12, FR-13, QR-04)

- **Starting condition:** A program is running and is expected to take a long
  time or not terminate.
- **Action:** Continue editing or navigating, then request cancellation.
- **Expected result:** Editing/navigation remain usable while the operation is
  pending; the operation reaches a visible cancelled state and does not leave a
  misleading result as if it completed.

### AC-06 — Collection continues after failure (FR-17–FR-20)

- **Starting condition:** A collection contains a passing expected-value test,
  a deliberately failing expectation, an expected-compilation-error test, and
  a later passing test.
- **Action:** Run the collection.
- **Expected result:** Every eligible test receives a status; the failing test
  includes actual-versus-expected detail; the expected-error test passes only
  when the compiler rejects the program as specified; the later test still
  runs; and the summary counts the outcomes.

### AC-07 — Persistence after refresh (FR-05, FR-06)

- **Starting condition:** A named program and collection have been saved locally.
- **Action:** Refresh the page, close/reopen the local environment, and reopen
  the saved items.
- **Expected result:** The saved items remain available with their source and
  expectations intact. If an item was unsaved, the interface provided a warning
  or recovery path before replacement.

### AC-08 — Sample response disclosure (FR-16)

- **Starting condition:** The real compiler is unavailable and demonstration
  sample responses are enabled.
- **Action:** Run the demonstration workflow and inspect the displayed output.
- **Expected result:** The response is visibly labeled sample/simulated at the
  point of use and in any history or test result view; no user could reasonably
  interpret it as a real compilation result.

## 10. Traceability matrix

Brief references use the stakeholder brief's section headings. “A#” refers to
the assumptions in Section 4; “Q#” refers to the unresolved questions there.

| Requirement | Source in brief, answer, or assumption |
| --- | --- |
| FR-01 | “Trying a program”; students typing/pasting programs. |
| FR-02 | “Trying a program”; “A few examples to start from.” |
| FR-03 | “Trying a program”; modify an example without losing the original. |
| FR-04 | “Trying a program”; students should not retype saved files. |
| FR-05 | “Trying a program”; keep a program and return later. |
| FR-06 | “Keeping examples as tests”; refreshing should not lose examples; return in another session. |
| FR-07 | “Trying a program”; ask the system to compile. |
| FR-08 | “Trying a program”; ask the system to run and see the answer. |
| FR-09 | “Understanding what happened”; compilation errors and run failures should differ; environment problems should be distinguishable. |
| FR-10 | “Understanding what happened”; help find a compiler-reported source location. |
| FR-11 | “Trying a program”; inspect AST/generated code without obstructing simple runs. |
| FR-12 | “Understanding what happened”; stop a long-running or nonterminating program. |
| FR-13 | “Understanding what happened”; page should remain usable while work is in progress. |
| FR-14 | “Understanding what happened”; identify which version produced a result after editing during a run. |
| FR-15 | “Understanding what happened”; preserve work and retry when compiler is unreachable. |
| FR-16 | “The compiler is still evolving”; sample responses acceptable only if not mistaken for actual results. |
| FR-17 | “Keeping examples as tests”; named tests with expected answers or intentional errors. A1/A2 define the proposed data contract. |
| FR-18 | “Keeping examples as tests”; collection of named tests and rerun after compiler changes. |
| FR-19 | “Keeping examples as tests”; quick summary with enough detail to investigate. |
| FR-20 | “Keeping examples as tests”; one troublesome test should not make the collection useless. |
| QR-01 | “Keeping the project manageable”; main tasks should be keyboard-operable. |
| QR-02 | “Keeping the project manageable”; messages should not depend only on colors. |
| QR-03 | “Keeping the project manageable”; respond promptly to ordinary actions. Target is proposed. |
| QR-04 | “Understanding what happened”; nonblocking work and stopping long runs. Timing target is proposed; Q5 remains open. |
| QR-05 | “Keeping the project manageable”; local setup, normal browser, no public website or accounts. Exact support is unresolved. |

## 11. Review notes and decisions

The following issues were found while reviewing the draft:

1. **Compiler boundary was ambiguous.** The brief mixes a web interface with a
   compiler that is still evolving and currently uses Python ASTs. The scope
   now explicitly treats the compiler as an external dependency and adds a
   replaceable adapter contract (FR-07–FR-16 and Section 8), so compiler
   implementation work is not accidentally required here.
2. **“Run,” “result,” and “error” were underspecified.** The brief does not
   establish whether run compiles first, which values can be returned, or how
   diagnostics are shaped. The specification records Q1–Q3, makes A1–A2
   explicit assumptions, and separates compile, execution, and environment
   states in FR-08–FR-10.
3. **Persistence and sharing could imply a much larger system.** The brief
   asks for later sessions and says sharing would be useful but not essential.
   The scope requires local persistence (FR-05–FR-06), excludes accounts and
   online collaboration, and defers sharing while recording Q7/A5.
4. **Long-running work could produce misleading stale results.** The original
   description mentions stopping work and changing a program while a run is in
   progress, but does not say how to associate output with source. FR-12–FR-14
   require cancellation, nonblocking behavior, and explicit version identity.
5. **“Easy,” “prompt,” and “useful explanation” were not directly verifiable.**
   The draft converts these into observable behaviors and proposed targets in
   FR-09, FR-10, QR-01–QR-05, and AC-02/AC-05. The proposed timing values must
   be confirmed rather than treated as stakeholder commitments.

## 12. Deferred decisions and release checklist

Before implementation is considered ready, the project team should obtain
answers to Q1–Q7, document the compiler schema, name supported browser
versions, specify local storage and import formats, and agree on runtime
termination limits. The first release should also verify all Must requirements
and the acceptance scenarios above. Should requirements such as artifact
inspection need to be staged because the compiler does not yet expose the
required data, the team should preserve the requirement and record the staged
scope. Could features such as sharing should not delay the core local workflow.
