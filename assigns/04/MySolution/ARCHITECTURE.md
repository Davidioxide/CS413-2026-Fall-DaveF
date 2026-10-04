# Architecture

```text
index.html/style.css
        | DOM events/rendering
      view.ts <------ app.ts ------> controller.ts ------> backend.ts ------HTTP------> backend.py
        |                              |                                      |
     browser DOM                    model.ts                            lambda1.py
```

| Area | Implementation | Responsibility |
|---|---|---|
| Model | `source/model.ts` | Applied source, draft, revision, results, artifacts, invalidation |
| View | `source/view.ts`, `index.html` | Accessible controls and literal text rendering |
| Controller | `source/controller.ts` | Source transitions, dispatch, busy/error/retry state |
| Adapter | `source/backend.ts` | Replaceable typed operation interface and HTTP implementation |
| Language backend | `source/backend.py` | Restricted parsing, free variables, evaluation, timeout boundary |

## Load → Lint → Interpret

1. The user selects a canned example or file. The controller validates it through the model, increments the revision, clears results/artifacts, and renders the source.
2. The controller sends `{operation, source, revision}` to the HTTP adapter. Python parses the expression using a whitelist over Python's AST; it never executes uploaded Python.
3. Lint calls `d0exp_fvset`, returns a `frozenset` internally, and reports sorted names for an undeclared-variable error. It never evaluates.
4. Interpret independently parses and calls `d0exp_evaluate` with `ENVnil()`. Values are rendered as text; malformed input and runtime failures have separate outcomes. A response for an old revision is ignored by the model.

## Contract and decisions

The adapter exposes `lint`, `interpret`, `typecheck`, `compile`, and `execute`. Results contain operation, revision, outcome, and message, with optional structured fields. Outcomes are `success`, `invalid_input`, `language_error`, `runtime_error`, `backend_error`, `timeout`, or `not_implemented`. An artifact will be `{revision, id, description}`; Execute must consume it directly. Failed compilation and any accepted source revision invalidate artifacts.

First, the controller—not the model—coordinates backend calls. This keeps the model framework-independent and makes substitute-backend controller tests straightforward, at the cost of a slightly larger controller. Second, the backend uses a constructor whitelist over `ast.parse` rather than a new concrete-syntax parser. This reuses Python's handling of comments and multiline input and is compact, but it intentionally supports only the supplied constructor representation. The two-second thread timeout bounds the request; process isolation would be preferable for forcibly stopping nontermination.

Real type-checking can replace the placeholder operation while preserving the result contract. Compile can produce an artifact tied to the current revision, such as a temporary executable or bytecode plus metadata. The model would enable Execute only after successful compilation for the same revision; Execute would validate the artifact revision and run the artifact without silently recompiling.
