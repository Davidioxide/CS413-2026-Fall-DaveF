"""Small service adapter around the supplied LAMBDA3 implementation."""

from __future__ import annotations

import multiprocessing
import os
import re
import sys
from dataclasses import dataclass

_LAMBDA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "LAMBDA3"))
if _LAMBDA_DIR not in sys.path:
    sys.path.insert(0, _LAMBDA_DIR)

import lambda3  # noqa: E402


MAX_SOURCE_BYTES = 64 * 1024
INTERPRET_TIMEOUT_SECONDS = 2.0


class ServiceError(Exception):
    """An expected RPC-facing service error."""

    def __init__(self, code: int, message: str, data: dict | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.data = data


def _diagnostic(exc: Exception) -> str:
    text = str(exc).strip() or exc.__class__.__name__
    # Do not return source paths or multi-line trace-like details to clients.
    text = text.replace("\\", "/").splitlines()[0]
    text = re.sub(r"(?:[A-Za-z]:)?/(?:[^/\\s]+/)+[^/\\s]*", "<path>", text)
    if "<lambda>" in text:
        text = text.replace("<lambda>", "source")
    return text[:500]


def parse_and_check(source: str):
    try:
        return lambda3.d0exp_parse_and_typecheck(source)
    except lambda3.LambdaSyntaxError as exc:
        raise ServiceError(-32010, "LAMBDA syntax error", {"kind": "syntax", "detail": _diagnostic(exc)}) from exc
    except lambda3.TypeCheckError as exc:
        raise ServiceError(-32011, "LAMBDA type-checking error", {"kind": "type", "detail": _diagnostic(exc)}) from exc


def typecheck(source: str) -> dict:
    _, typ = parse_and_check(source)
    return {"type": lambda3.format_type(typ)}


def _evaluate_worker(expression, connection) -> None:
    try:
        value = lambda3.d0exp_evaluate(expression)
        connection.send(("ok", lambda3.d0val_format(value)))
    except BaseException as exc:  # worker boundary: parent converts this safely
        connection.send(("error", exc.__class__.__name__, _diagnostic(exc)))
    finally:
        connection.close()


def interpret(source: str) -> dict:
    expression, typ = parse_and_check(source)
    parent, child = multiprocessing.Pipe(False)
    process = multiprocessing.Process(target=_evaluate_worker, args=(expression, child), daemon=True)
    process.start()
    child.close()
    try:
        if not parent.poll(INTERPRET_TIMEOUT_SECONDS):
            process.terminate()
            process.join(0.5)
            raise ServiceError(-32012, "LAMBDA execution timed out", {"kind": "timeout"})
        message = parent.recv()
    finally:
        parent.close()
        if process.is_alive():
            process.terminate()
        process.join(0.5)
    if message[0] == "error":
        raise ServiceError(-32603, "Internal error")
    return {"type": lambda3.format_type(typ), "value": message[1]}


def compile_source(source: str, target: str) -> dict:
    expression, _ = parse_and_check(source)
    try:
        if target == "python":
            code = lambda3.d0exp_compile(expression)
        elif target == "javascript":
            code = lambda3.d0exp_compile_js(expression)
        else:
            raise ServiceError(-32602, "Invalid params", {"field": "target", "expected": ["python", "javascript"]})
    except ServiceError:
        raise
    except Exception as exc:
        raise ServiceError(-32603, "Internal error") from exc
    return {"target": target, "code": code}


def validate_source(value) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ServiceError(-32602, "Invalid params", {"field": "source", "reason": "source must be a nonempty string"})
    if len(value.encode("utf-8")) > MAX_SOURCE_BYTES:
        raise ServiceError(-32602, "Invalid params", {"field": "source", "reason": "source exceeds maximum size"})
    return value

