# LAMBDA Web Front-End

This is a local, single-user MVC web application for restricted LAMBDA constructor expressions. It uses Python 3.12+ (tested with Python 3.14), the supplied `../lambda1.py`, TypeScript 5.6+, and a modern browser. The Python server uses only the standard library.

## Setup and use

```sh
cd MySolution
npm install
npm run build
python3 source/backend.py
```

Open <http://127.0.0.1:8000>. Tests run with `npm test` (the Python unittest suite). `npm run build` emits browser JavaScript into the ignored `build/` directory; the local server maps browser module requests there.

The Factorial and Fibonacci menu examples interpret to `D0Vint(arg1=120)` and `D0Vint(arg1=21)`. Manual input `D0Evar("x")` reports undeclared `x`; replace it with `D0Eint(42)` and Apply changes. `D0Eop2("/", D0Eint(1), D0Eint(0))` passes Lint but reports a runtime failure during Interpret. Type-check and Compile clearly report that they are not implemented; Execute stays disabled because it accepts only a future compiler artifact.

Supported input is one Python `ast` expression made from the `D0E...` constructors in `lambda1.py`, positional arguments, strings, integers, booleans, comments, and multiline formatting. Calls, attributes, imports, comprehensions, and arbitrary Python are rejected. Source is limited to 65,536 UTF-8 bytes. Each request has a two-second response timeout; a future production version should isolate evaluation in a killable worker process for stronger termination guarantees. Known limitations include no persistence, one local user, no real type checker/compiler, and a simple text result view.

## Reflection

MVC helped by giving each kind of change a clear home. The model owns the applied source, revision, draft, results, and artifact invalidation rules, so those rules do not depend on a particular page layout. The view is deliberately thin: it creates accessible controls, forwards events, and renders text with `textContent`, while the controller coordinates source transitions and asynchronous operations. The backend adapter keeps the browser unaware of Python imports and makes a substitute backend practical in controller tests. The most difficult boundary was the draft source: the interface must retain rejected text for correction while ensuring that language operations see only an applied revision. Treating a draft as separate state and disabling conflicting controls made that distinction explicit. A second awkward edge is timeout handling, because a thread timeout bounds the HTTP response but cannot forcibly stop Python code; process isolation is the natural future improvement. The architecture makes a real compiler easier to add: Compile can return an artifact record carrying a revision and executable metadata, and Execute can consume exactly that record without recompiling. A type checker can be added behind the same operation interface. Other future extensions—syntax highlighting, saved examples, richer diagnostics, or a worker pool—can be added without placing language logic in the view.
