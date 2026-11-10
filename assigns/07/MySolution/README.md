# LAMBDA3 JSON-RPC service

This is a Python 3.12+ JSON-RPC 2.0 HTTP service for the provided LAMBDA3
implementation. It uses FastAPI with Uvicorn.

From `assigns/07/`:

```sh
python3 -m pip install -r MySolution/requirements.txt
python3 MySolution/server.py
python3 -m unittest discover -s TEST -v
python3 -m unittest discover -s MySolution/tests -v
```

The [Makefile](Makefile) provides the same workflows when run from
`assigns/07/MySolution/`:

```sh
make -C MySolution test       # focused in-process tests
make -C MySolution test-http  # supplied HTTP contract tests; starts/stops server
make -C MySolution test-all   # runs both test suites
make -C MySolution serve      # starts the service on port 8000
```

`test-http` manages its temporary server process automatically. To use a
different port or endpoint, start the server manually with `serve` options
and set `LAMBDA_RPC_URL` when running the supplied tests.

The endpoint is `http://127.0.0.1:8000/rpc`. For example:

```sh
curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"service.health","params":{},"id":1}' \
  http://127.0.0.1:8000/rpc

curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"lambda.typecheck","params":{"source":"1 + 2"},"id":2}' \
  http://127.0.0.1:8000/rpc

curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"lambda.interpret","params":{"source":"let fact : sint -> sint = fix fact(n: sint): sint => if n <= 1 then 1 else n * fact(n - 1) in fact(6) end"},"id":3}' \
  http://127.0.0.1:8000/rpc

curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"lambda.compile","params":{"source":"1 + 2","target":"javascript"},"id":4}' \
  http://127.0.0.1:8000/rpc

curl -s -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"lambda.typecheck","params":{"source":"x"},"id":5}' \
  http://127.0.0.1:8000/rpc
```

The last request demonstrates the documented type-checking error. Python and
JavaScript compiler methods return generated source text only; the service
never executes submitted or generated programs. See [RPC.md](RPC.md) for the
complete contract, limits, examples, and error mapping.
