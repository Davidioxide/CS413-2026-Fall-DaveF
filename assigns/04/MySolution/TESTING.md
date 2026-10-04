# Testing

Run `npm install`, `npm run build`, and `npm test` from `MySolution/`. The automated suite covers free-variable constructors and scope, non-evaluating Lint, arithmetic/error interpretation, model revision/rejection rules, placeholder dispatch, Execute availability, and backend failure followed by retry. The model test runs as Python unit code without a browser or server. `test_backend.py` directly exercises the real adapter and supplied interpreter; `model_rules.py` is a small browser-independent model-rule fixture for state-boundary tests.

| Requirement | Automated/browser evidence |
|---|---|
| F1 | `index.html` menu/file controls; smoke steps 1–2 |
| F2 | controller draft/apply/discard logic; smoke step 3 |
| F3 | model byte limit, backend empty check, fatal UTF-8 decoder; smoke step 5 |
| F4 | ordered buttons in `index.html`; smoke step 4 |
| F5 | `test_backend.py` free-variable and lint tests |
| F6 | `test_backend.py` arithmetic, malformed, and runtime tests |
| F7 | placeholder dispatch test and disabled Execute rendering |
| F8 | model revision test and `acceptSource` invalidation |
| F9 | `View.resultNode` uses `textContent` and `<pre>`; smoke step 6 |
| F10 | controller busy/failure/finally paths; backend timeout contract; smoke step 5 |

## Browser smoke test

1. Start `python3 source/backend.py`, open `http://127.0.0.1:8000`, and verify the Load source menu, file picker, editor, revision, and status are visible.
2. Select Factorial and click Lint then Interpret: both show revision-tagged success and Interpret shows `D0Vint(arg1=120)`. Repeat Fibonacci for `D0Vint(arg1=21)`.
3. Select Manual input, type `D0Evar("x")`, Apply, and Lint. The result lists `x`; replace the editor with `D0Eint(42)`, Apply, and retry Lint successfully. Discard restores the applied source.
4. Click Type-check and Compile and verify not-implemented messages. Execute remains disabled because no artifact exists.
5. Try blank or whitespace-only input and an invalid file; verify the previous applied source remains and the rejected draft/status is available for correction. Force a backend failure or stop the server, observe an error, restart it, and retry.
6. Enter `D0Evar("<b>literal</b>")` and confirm output is displayed as literal text, not HTML.

Observed in the final local run: build completed, all Python tests passed, the health endpoint returned `{"ok": true}`, and browser-facing static/API smoke checks matched the expected controls and response shapes. A real graphical browser is not available in this environment, so visual click-through should be repeated before submission.
