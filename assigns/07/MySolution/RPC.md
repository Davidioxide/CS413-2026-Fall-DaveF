# LAMBDA3 JSON-RPC contract

## Transport

The service accepts `POST http://127.0.0.1:8000/rpc` with
`Content-Type: application/json`. A request body is one JSON-RPC 2.0 request
object or a nonempty array of request objects. RPC outcomes, including parse
and invalid-request errors, use HTTP 200. Unsupported media types and unknown
paths are transport errors (415 and 404). A notification with no response uses
HTTP 204 and an empty body.

The maximum `source` is 65,536 UTF-8 bytes. Interpretation has a hard two
second deadline in a separate worker process. A timeout reports `-32012`; it
does not establish that the source is mathematically nonterminating.

## Methods

| Method | Params | Result |
|---|---|---|
| `service.health` | `{}` | `{ "status": "ok", "version": "1.0" }` |
| `lambda.typecheck` | `{ "source": string }` | `{ "type": string }` |
| `lambda.interpret` | `{ "source": string }` | `{ "type": string, "value": string }` |
| `lambda.compile` | `{ "source": string, "target": "python"\|"javascript" }` | `{ "target": string, "code": string }` |

Source operations always call the supplied LAMBDA3 parser and type checker
first. Interpretation uses `d0val_format`; compilation returns generated code
without executing it.

## Examples

Health:

```json
{"jsonrpc":"2.0","method":"service.health","params":{},"id":"h1"}
```

```json
{"jsonrpc":"2.0","result":{"status":"ok","version":"1.0"},"id":"h1"}
```

Successful type-check and interpretation:

```json
{"jsonrpc":"2.0","method":"lambda.typecheck","params":{"source":"1 + 2"},"id":2}
```

```json
{"jsonrpc":"2.0","result":{"type":"sint"},"id":2}
```

```json
{"jsonrpc":"2.0","method":"lambda.interpret","params":{"source":"20 + 22"},"id":3}
```

```json
{"jsonrpc":"2.0","result":{"type":"sint","value":"42"},"id":3}
```

Compilation (the `code` string is abbreviated here only for readability):

```json
{"jsonrpc":"2.0","method":"lambda.compile","params":{"source":"1 + 2","target":"python"},"id":"c1"}
```

```json
{"jsonrpc":"2.0","result":{"target":"python","code":"# The emitted program uses Python values for integers, booleans, lists and\n# tuples. Options need a tagged pair so optn_cons(None) remains distinct from\n# optn_nil (None); the private sentinel is created once per generated program.\ndef _lambda_list_cons(head, tail):\n    if not isinstance(tail, list):\n        raise TypeError(\"list_cons: list tail expected\")\n    return [head] + tail\n\ndef _lambda_list_nilq(value):\n    if not isinstance(value, list):\n        raise TypeError(\"list_nilq: list expected\")\n    return len(value) == 0\n\ndef _lambda_list_head(value):\n    if not isinstance(value, list):\n        raise TypeError(\"list_head: list expected\")\n    if not value:\n        raise ValueError(\"list_head: nonempty list expected\")\n    return value[0]\n\ndef _lambda_list_tail(value):\n    if not isinstance(value, list):\n        raise TypeError(\"list_tail: list expected\")\n    if not value:\n        raise ValueError(\"list_tail: nonempty list expected\")\n    return value[1:]\n\ndef _lambda_a1sz_index(array, index):\n    if not isinstance(array, list) or not isinstance(index, int) or isinstance(index, bool):\n        raise TypeError(\"A1sz indexing expects an array and sint index\")\n    if not 0 <= index < len(array): raise IndexError(\"A1sz index out of range\")\n    return index\ndef _lambda_a1sz_getat(array, index): return array[_lambda_a1sz_index(array, index)]\ndef _lambda_a1sz_setat(array, index, value):\n    array[_lambda_a1sz_index(array, index)] = value\n    return ()\ndef _lambda_a1sz_make_ncpy(size, value):\n    if not isinstance(size, int) or isinstance(size, bool): raise TypeError(\"A1sz size must be sint\")\n    if size < 0: raise ValueError(\"A1sz size must be nonnegative\")\n    return [value for _ in range(size)]\ndef _lambda_a1sz_make_nfun(size, fn):\n    if not isinstance(size, int) or isinstance(size, bool): raise TypeError(\"A1sz size must be sint\")\n    if size < 0: raise ValueError(\"A1sz size must be nonnegative\")\n    return [fn(i) for i in range(size)]\n\ndef _lambda_optn_cons(value):\n    return (_lambda_some_tag, value)\n\ndef _lambda_optn_nilq(value):\n    return value is None\n\ndef _lambda_optn_get(value):\n    if value is None or not (isinstance(value, tuple) and len(value) == 2 and value[0] is _lambda_some_tag):\n        raise ValueError(\"optn_get: nonempty option expected\")\n    return value[1]\n\nclass _LambdaLazy:\n    def __init__(self, thunk):\n        self.thunk, self.evaluated, self.value = thunk, False, None\n\ndef _lambda_lazy_make(thunk):\n    if not callable(thunk): raise TypeError(\"lazy_make: thunk function expected\")\n    return _LambdaLazy(thunk)\ndef _lambda_lazy_eval(value):\n    if not isinstance(value, _LambdaLazy): raise TypeError(\"lazy_eval: Lazy value expected\")\n    if not value.evaluated:\n        value.value = value.thunk(())\n        value.evaluated = True\n    return value.value\ndef _lambda_stcn_nil(): return {\"cons\": False}\ndef _lambda_stcn_cons(head, tail):\n    if not isinstance(tail, _LambdaLazy): raise TypeError(\"stcn_cons: lazy stream tail expected\")\n    return {\"cons\": True, \"head\": head, \"tail\": tail}\ndef _lambda_stcn_check(value, name):\n    if not isinstance(value, dict) or \"cons\" not in value: raise TypeError(name + \": Stcn value expected\")\ndef _lambda_stcn_nilq(value):\n    _lambda_stcn_check(value, \"stcn_nilq\")\n    return not value[\"cons\"]\ndef _lambda_stcn_consq(value):\n    _lambda_stcn_check(value, \"stcn_consq\")\n    return value[\"cons\"]\ndef _lambda_stcn_head(value):\n    _lambda_stcn_check(value, \"stcn_head\")\n    if not value[\"cons\"]: raise ValueError(\"stcn_head: nonempty stream constructor expected\")\n    return value[\"head\"]\ndef _lambda_stcn_tail(value):\n    _lambda_stcn_check(value, \"stcn_tail\")\n    if not value[\"cons\"]: raise ValueError(\"stcn_tail: nonempty stream constructor expected\")\n    return value[\"tail\"]\n\ndef _lambda_format(value):\n    if isinstance(value, _LambdaLazy): return \"<lazy>\"\n    if isinstance(value, dict) and \"cons\" in value:\n        if not value[\"cons\"]: return \"stcn_nil()\"\n        return \"stcn_cons(\" + _lambda_format(value[\"head\"]) + \", <lazy>)\"\n    if value is None:\n        return \"optn_nil()\"\n    if isinstance(value, tuple) and len(value) == 2 and value[0] is _lambda_some_tag:\n        return \"optn_cons(\" + _lambda_format(value[1]) + \")\"\n    if isinstance(value, bool):\n        return \"true\" if value else \"false\"\n    if isinstance(value, list):\n        return \"[\" + \", \".join(_lambda_format(item) for item in value) + \"]\"\n    if isinstance(value, tuple):\n        body = \", \".join(_lambda_format(item) for item in value)\n        return \"(\" + body + (\",\" if len(value) == 1 else \"\") + \")\"\n    if callable(value):\n        return \"<lam>\"\n    return str(value)\n\ndef _lambda_print(value):\n    print(_lambda_format(value))\n    return ()\n\n_lambda_some_tag = object()\n\ndef _lambda_main():\n    _v1 = 1\n    _v2 = 2\n    _v3 = (_v1 + _v2)\n    return _v3\n\n_lambda_result = _lambda_main()\n"},"id":"c1"}
```

Syntax and type errors:

```json
{"jsonrpc":"2.0","method":"lambda.typecheck","params":{"source":"if then"},"id":"s1"}
```

```json
{"jsonrpc":"2.0","error":{"code":-32010,"message":"LAMBDA syntax error","data":{"kind":"syntax","detail":"Expected an expression (source, line 1)"}},"id":"s1"}
```

```json
{"jsonrpc":"2.0","method":"lambda.typecheck","params":{"source":"1 + true"},"id":"t1"}
```

```json
{"jsonrpc":"2.0","error":{"code":-32011,"message":"LAMBDA type-checking error","data":{"kind":"type","detail":"+: expected bool, got sint"}},"id":"t1"}
```

Batch with a call and a notification:

```json
[{"jsonrpc":"2.0","method":"lambda.interpret","params":{"source":"6 * 7"},"id":"answer"},{"jsonrpc":"2.0","method":"service.health","params":{}}]
```

```json
[{"jsonrpc":"2.0","result":{"type":"sint","value":"42"},"id":"answer"}]
```

Notification-only batch:

```json
[{"jsonrpc":"2.0","method":"service.health","params":{}},{"jsonrpc":"2.0","method":"lambda.typecheck","params":{"source":"1 + 2"}}]
```

The response is an empty body with HTTP 204.

## Errors and envelopes

Every response has `jsonrpc: "2.0"` and the request `id`; it has exactly one
of `result` or `error`. IDs are strings, numbers, or null. Missing IDs denote
notifications, which are executed but produce no response. Batch response
order is not meaningful; clients match responses by ID. Invalid batch members
and empty batches produce an Invalid Request response with `id: null`.

| Code | Meaning | Data |
|---:|---|---|
| -32700 | Invalid JSON | omitted |
| -32600 | Invalid Request envelope | omitted |
| -32601 | Unknown method | omitted |
| -32602 | Invalid params, including blank/oversized source | field/reason when useful |
| -32603 | Unexpected server failure | omitted |
| -32010 | LAMBDA syntax error | `kind`, client-safe `detail` |
| -32011 | LAMBDA type-checking error | `kind`, client-safe `detail` |
| -32012 | Interpretation deadline expired | `kind: "timeout"` |

Tracebacks and filesystem paths are never returned. The following JSON Schema
describes the common request and response envelopes (method-specific params
and result shapes are specified in the table above):

```json
{
  "$schema":"https://json-schema.org/draft/2020-12/schema",
  "$defs":{
    "id":{"type":["string","number","null"]},
    "request":{"type":"object","required":["jsonrpc","method"],"properties":{"jsonrpc":{"const":"2.0"},"method":{"type":"string"},"params":{"type":"object"},"id":{"$ref":"#/$defs/id"}},"additionalProperties":true},
    "error":{"type":"object","required":["code","message"],"properties":{"code":{"type":"integer"},"message":{"type":"string"},"data":{}}},
    "response":{"type":"object","required":["jsonrpc","id"],"properties":{"jsonrpc":{"const":"2.0"},"id":{"$ref":"#/$defs/id"},"result":{},"error":{"$ref":"#/$defs/error"}},"oneOf":[{"required":["result"],"not":{"required":["error"]}},{"required":["error"],"not":{"required":["result"]}}],"additionalProperties":true}
  }
}
```
