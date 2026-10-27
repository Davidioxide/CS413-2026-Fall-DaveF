"""The shared evaluator: source ASTs use source semantics; target terms use CBV."""
from __future__ import annotations
from dataclasses import dataclass
from target import Term, Var, Lam, App, substitute, free_vars

@dataclass(frozen=True)
class EvalResult:
    status: str                 # complete, exhausted, or error
    value: object | None
    steps: int
    message: str = ""

class EvaluationError(Exception): pass

def eval_target(term: Term, budget: int = 10000) -> EvalResult:
    if budget < 0: return EvalResult("error", None, 0, "EVALUATOR ERROR: negative budget")
    if free_vars(term):
        return EvalResult("error", None, 0, "EVALUATOR ERROR: open target term: " + ", ".join(sorted(free_vars(term))))
    used = 0
    def go(t: Term) -> Term:
        nonlocal used
        if isinstance(t, Lam): return t
        if isinstance(t, Var): raise EvaluationError(f"unbound target variable {t.name}")
        fn = go(t.fn)
        arg = go(t.arg)
        if not isinstance(fn, Lam): raise EvaluationError("target application of a non-lambda value")
        if used >= budget: raise BudgetExhausted
        used += 1
        return go(substitute(fn.body, fn.name, arg))
    try:
        return EvalResult("complete", go(term), used)
    except BudgetExhausted:
        return EvalResult("exhausted", None, used, "EVALUATOR ERROR: beta-step budget exhausted")
    except RecursionError:
        # A repeatedly self-applying term can exhaust Python's call stack before
        # the requested semantic budget.  It is still only a bounded observation
        # of execution, so report resource exhaustion and never a decoded value.
        return EvalResult("exhausted", None, used, "EVALUATOR ERROR: evaluation resource exhausted")
    except EvaluationError as exc:
        return EvalResult("error", None, used, "EVALUATOR ERROR: " + str(exc))

class BudgetExhausted(Exception): pass

@dataclass
class SClosure:
    name: str
    body: object
    env: dict[str, object]
@dataclass
class SFix:
    fname: str
    pname: str
    body: object
    env: dict[str, object]
@dataclass
class SPair:
    left: object
    right: object

def eval_source(expr: object, env: dict[str, object] | None = None) -> object:
    """Unbounded source oracle used for terminating demonstrations/tests."""
    env = {} if env is None else env
    tag = getattr(expr, "ctag", type(expr).__name__)
    if tag == "D0Eint":
        if expr.arg1 < 0: raise EvaluationError("SOURCE EVALUATOR ERROR: negative natural")
        return expr.arg1
    if tag == "D0Ebtf": return expr.arg1
    if tag == "D0Evar":
        if expr.arg1 not in env: raise EvaluationError("SOURCE EVALUATOR ERROR: unbound variable " + expr.arg1)
        return env[expr.arg1]
    if tag == "D0Elam": return SClosure(expr.arg1, expr.arg2, env.copy())
    if tag == "D0Efix": return SFix(expr.arg1, expr.arg2, expr.arg3, env.copy())
    if tag == "D0Eapp":
        fn = eval_source(expr.arg1, env); arg = eval_source(expr.arg2, env)
        if isinstance(fn, SClosure):
            e = fn.env.copy(); e[fn.name] = arg; return eval_source(fn.body, e)
        if isinstance(fn, SFix):
            e = fn.env.copy(); e[fn.fname] = fn; e[fn.pname] = arg; return eval_source(fn.body, e)
        raise EvaluationError("SOURCE EVALUATOR ERROR: application of non-function")
    if tag == "D0Eif0": return eval_source(expr.arg2 if eval_source(expr.arg1, env) else expr.arg3, env)
    if tag == "D0Elet":
        e = env.copy(); e[expr.arg1] = eval_source(expr.arg2, env); return eval_source(expr.arg3, e)
    if tag == "D0Epair": return SPair(eval_source(expr.arg1, env), eval_source(expr.arg2, env))
    if tag == "D0Epfst":
        p = eval_source(expr.arg1, env)
        if not isinstance(p, SPair): raise EvaluationError("SOURCE EVALUATOR ERROR: fst of non-pair")
        return p.left
    if tag == "D0Epsnd":
        p = eval_source(expr.arg1, env)
        if not isinstance(p, SPair): raise EvaluationError("SOURCE EVALUATOR ERROR: snd of non-pair")
        return p.right
    if tag == "D0Eop1":
        if expr.name != "not": raise EvaluationError("SOURCE EVALUATOR ERROR: unsupported unary operator " + expr.name)
        return not eval_source(expr.arg1, env)
    if tag == "D0Eop2":
        left = eval_source(expr.arg1, env)
        if expr.name == "and": return eval_source(expr.arg2, env) if left else False
        if expr.name == "or": return True if left else eval_source(expr.arg2, env)
        right = eval_source(expr.arg2, env)
        if expr.name == "+": return left + right
        if expr.name == "-": return max(0, left - right)
        if expr.name == "*": return left * right
        return {"<": left < right, "<=": left <= right, ">": left > right,
                ">=": left >= right, "==": left == right, "!=": left != right}[expr.name]
    raise EvaluationError("SOURCE EVALUATOR ERROR: unsupported constructor " + tag)

def evaluate(expr: object, budget: int = 10000) -> EvalResult | object:
    if isinstance(expr, (Var, Lam, App)): return eval_target(expr, budget)
    return eval_source(expr)
