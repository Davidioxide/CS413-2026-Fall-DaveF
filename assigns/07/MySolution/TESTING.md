# Testing

The black-box suite in `../TEST/test_rpc_api.py` runs against the documented
HTTP endpoint. The focused suites in `tests/` exercise the service adapter and
dispatcher in-process, while `test_http_transport.py` uses FastAPI's in-process
HTTP test client to verify transport behavior. They are separated by behavior:

```text
tests/test_health_and_notifications.py
tests/test_lambda_operations.py
tests/test_errors_and_validation.py
tests/test_batches.py
tests/test_http_transport.py
```

Architecture:

```text
FastAPI POST /rpc (Uvicorn in production)
      |
      v
JSON parser + envelope/batch dispatcher (server.py)
      |
      v
LAMBDA3 service adapter (lambda_service.py)
      |
      v
LAMBDA3 parser/type checker/interpreter/compiler (LAMBDA3/lambda3.py)
```

| Required behavior | Test |
|---|---|
| Health, IDs, and notifications | `test_health_and_notifications.py` |
| Arithmetic, factorial, tuple, list, and closure formatting | `test_lambda_operations.py` |
| Python/JavaScript compilation | `test_lambda_operations.py` |
| Syntax/type errors and unbound variables | `test_errors_and_validation.py` |
| Params, source limits, unknown methods, and backend failures | `test_errors_and_validation.py` |
| Batch IDs, notifications, and invalid members | `test_batches.py` |
| HTTP status, content type, malformed JSON, and endpoint responses | `test_http_transport.py` and `../TEST/test_rpc_api.py` |
| Injected backend failure and sanitized internal error | `test_http_transport.py::test_backend_failure_is_sanitized_over_http` |
| Interpretation timeout and preserved request ID | `test_http_transport.py::test_timeout_is_explicit_over_http` and `test_errors_and_validation.py::test_interpret_timeout_has_explicit_error` |

Observed verification: all 29 focused tests and all 15 supplied HTTP black-box
tests pass when run with the server started on port 8000. The timeout and
injected-failure paths are tested through FastAPI's HTTP client and the
dispatcher boundary; generated code is never executed.
