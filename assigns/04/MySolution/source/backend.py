"""HTTP adapter for the supplied lambda1.py interpreter."""
from __future__ import annotations

import ast
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import lambda1 as lang  # noqa: E402 - supplied source file

MAX_SOURCE_BYTES = 64 * 1024
OP_TIMEOUT_SECONDS = 2.0
CONSTRUCTORS: dict[str, tuple[type, int]] = {
    "D0Eint": (lang.D0Eint, 1), "D0Ebtf": (lang.D0Ebtf, 1),
    "D0Eop1": (lang.D0Eop1, 2), "D0Eop2": (lang.D0Eop2, 3),
    "D0Evar": (lang.D0Evar, 1), "D0Elam": (lang.D0Elam, 2),
    "D0Efix": (lang.D0Efix, 3), "D0Eapp": (lang.D0Eapp, 2),
    "D0Eif0": (lang.D0Eif0, 3), "D0Elet": (lang.D0Elet, 3),
    "D0Epair": (lang.D0Epair, 2), "D0Epfst": (lang.D0Epfst, 1),
    "D0Epsnd": (lang.D0Epsnd, 1),
}
STRING_ARGS = {"D0Eop1": {0}, "D0Eop2": {0}, "D0Evar": {0},
               "D0Elam": {0}, "D0Efix": {0, 1}, "D0Elet": {0}}


class InputError(ValueError):
    pass


def parse_source(source: str):
    if not isinstance(source, str) or not source.strip():
        raise InputError("Source is empty.")
    if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise InputError(f"Source exceeds the {MAX_SOURCE_BYTES}-byte limit.")
    try:
        tree = ast.parse(source, mode="eval")
    except (SyntaxError, ValueError) as exc:
        raise InputError(f"Malformed constructor expression: {exc}") from exc
    return _read_node(tree.body)


def _read_node(node: ast.AST):
    if isinstance(node, ast.Constant) and type(node.value) in (int, bool, str):
        return node.value
    if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
        raise InputError("Only named LAMBDA constructors and literal arguments are allowed.")
    name = node.func.id
    if name not in CONSTRUCTORS or node.keywords:
        raise InputError(f"Unsupported or invalid constructor: {name}")
    cls, arity = CONSTRUCTORS[name]
    if len(node.args) != arity:
        raise InputError(f"{name} expects {arity} argument(s), got {len(node.args)}.")
    args = []
    for index, child in enumerate(node.args):
        if name in STRING_ARGS and index in STRING_ARGS[name]:
            if not isinstance(child, ast.Constant) or type(child.value) is not str:
                raise InputError(f"{name} argument {index + 1} must be a string.")
            args.append(child.value)
        else:
            args.append(_read_node(child))
    return cls(*args)


def _has_error_value(value) -> bool:
    if isinstance(value, lang.D0V000) and type(value) is lang.D0V000:
        return True
    if isinstance(value, lang.D0Vpair):
        return _has_error_value(value.arg1) or _has_error_value(value.arg2)
    return False


def _text(value) -> str:
    return repr(value)


@dataclass
class Backend:
    def run(self, operation: str, source: str, revision: int) -> dict[str, Any]:
        base = {"operation": operation, "revision": revision}
        if operation in {"typecheck", "compile"}:
            message = ("Type checking is not yet implemented."
                       if operation == "typecheck" else
                       "Compilation is not yet implemented; no generated artifact exists.")
            return {**base, "outcome": "not_implemented", "message": message}
        if operation == "execute":
            return {**base, "outcome": "not_implemented",
                    "message": "Execute is unavailable because no compiled artifact exists."}
        try:
            expression = parse_source(source)
            if operation == "lint":
                free = lang.d0exp_fvset(expression)
                names = sorted(free)
                if names:
                    return {**base, "outcome": "language_error", "freeVariables": names,
                            "message": "Undeclared variables: " + ", ".join(names)}
                return {**base, "outcome": "success", "freeVariables": [],
                        "message": "No free variables found."}
            if operation == "interpret":
                value = lang.d0exp_evaluate(expression, lang.ENVnil())
                if _has_error_value(value):
                    return {**base, "outcome": "runtime_error",
                            "message": "Evaluation returned the D0V000() error sentinel."}
                return {**base, "outcome": "success", "message": _text(value)}
            return {**base, "outcome": "backend_error", "message": f"Unknown operation: {operation}"}
        except InputError as exc:
            return {**base, "outcome": "invalid_input", "message": str(exc)}
        except Exception as exc:  # language/runtime failures are user-visible diagnostics
            return {**base, "outcome": "runtime_error", "message": f"Runtime failure: {type(exc).__name__}: {exc}"}


backend = Backend()
executor = ThreadPoolExecutor(max_workers=4)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/health":
            self._json({"ok": True})
            return
        relative = self.path.removeprefix("/") or "index.html"
        root = Path(__file__).parent
        candidate = (root / relative).resolve()
        if not candidate.is_file() and relative.endswith(".js"):
            candidate = (root.parent / "build" / relative).resolve()
        allowed = (root, root.parent / "build")
        if not any(base.resolve() in candidate.parents for base in allowed):
            self.send_error(404)
            return
        if not candidate.is_file():
            self.send_error(404)
            return
        data = candidate.read_bytes()
        types = {".html": "text/html", ".js": "text/javascript", ".css": "text/css"}
        self.send_response(200)
        self.send_header("Content-Type", types.get(candidate.suffix, "application/octet-stream") + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        if self.path != "/api/operation":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length))
            operation, source, revision = payload["operation"], payload["source"], int(payload["revision"])
            future = executor.submit(backend.run, operation, source, revision)
            result = future.result(timeout=OP_TIMEOUT_SECONDS)
        except TimeoutError:
            result = {"operation": payload.get("operation", "unknown"), "revision": payload.get("revision", 0),
                      "outcome": "timeout", "message": f"Operation exceeded {OP_TIMEOUT_SECONDS:g} seconds."}
        except Exception as exc:
            result = {"operation": "unknown", "revision": 0, "outcome": "backend_error", "message": str(exc)}
        self._json(result)

    def _json(self, value):
        data = json.dumps(value).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *_args):
        return


if __name__ == "__main__":
    port = int(os.environ.get("LAMBDA_PORT", "8000"))
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"LAMBDA front-end: http://127.0.0.1:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
