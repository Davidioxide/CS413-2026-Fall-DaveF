"""FastAPI JSON-RPC 2.0 service for LAMBDA3."""

from __future__ import annotations

import json
import logging
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response

try:
    from . import lambda_service as service
except ImportError:  # direct execution: python3 MySolution/server.py
    import lambda_service as service

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger("lambda-rpc")

app = FastAPI(title="LAMBDA3 JSON-RPC service", version="1.0")


def response(result=None, *, request_id=None, error=None):
    body = {"jsonrpc": "2.0", "id": request_id}
    if error is None:
        body["result"] = result
    else:
        body["error"] = error
    return body


def rpc_error(code: int, message: str, data=None):
    error = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return error


def _valid_id(value):
    return value is None or (isinstance(value, (str, int, float)) and not isinstance(value, bool))


def _invalid_request():
    return response(error=rpc_error(-32600, "Invalid Request"))


def dispatch(request: Any):
    """Dispatch one decoded JSON value and return (response-or-None, valid)."""
    if not isinstance(request, dict):
        return _invalid_request(), False
    request_id = request.get("id")
    if (request.get("jsonrpc") != "2.0" or not isinstance(request.get("method"), str)
            or not _valid_id(request_id)
            or ("params" in request and not isinstance(request.get("params"), dict))):
        return _invalid_request(), False
    notification = "id" not in request
    method = request["method"]
    params = request.get("params", {})
    try:
        if method == "service.health":
            if params != {}:
                raise service.ServiceError(-32602, "Invalid params")
            result = {"status": "ok", "version": "1.0"}
        elif method == "lambda.typecheck":
            result = service.typecheck(service.validate_source(params.get("source")))
        elif method == "lambda.interpret":
            result = service.interpret(service.validate_source(params.get("source")))
        elif method == "lambda.compile":
            source = service.validate_source(params.get("source"))
            target = params.get("target")
            if target not in ("python", "javascript"):
                raise service.ServiceError(-32602, "Invalid params", {"field": "target"})
            result = service.compile_source(source, target)
        else:
            raise service.ServiceError(-32601, "Method not found")
    except service.ServiceError as exc:
        if notification:
            return None, True
        return response(request_id=request_id, error=rpc_error(exc.code, exc.message, exc.data)), True
    except Exception:
        LOGGER.exception("Unhandled RPC failure")
        if notification:
            return None, True
        return response(request_id=request_id, error=rpc_error(-32603, "Internal error")), True
    if notification:
        return None, True
    return response(result, request_id=request_id), True


def _json_response(body):
    return JSONResponse(content=body, status_code=200)


@app.post("/rpc")
async def rpc_endpoint(request: Request):
    """Decode the JSON-RPC transport and delegate to the dispatcher."""
    content_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if content_type != "application/json":
        return JSONResponse(
            content={"detail": "Content-Type must be application/json"},
            status_code=415,
        )

    try:
        payload = json.loads((await request.body()).decode("utf-8"))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return _json_response(response(error=rpc_error(-32700, "Parse error")))

    if isinstance(payload, list):
        if not payload:
            return _json_response(_invalid_request())
        bodies = []
        for item in payload:
            body, _ = dispatch(item)
            if body is not None:
                bodies.append(body)
        if not bodies:
            return Response(status_code=204)
        return _json_response(bodies)

    body, _ = dispatch(payload)
    if body is None:
        return Response(status_code=204)
    return _json_response(body)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the LAMBDA3 JSON-RPC service")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    LOGGER.info("LAMBDA3 RPC listening at http://%s:%d/rpc", args.host, args.port)
    uvicorn.run(app, host=args.host, port=args.port)
