"""Bounded pure-term observers for Church naturals, booleans, and pairs."""
from __future__ import annotations
from dataclasses import dataclass
from target import Var, Lam, App, Term
from evaluator import eval_target
from church import FST, SND

@dataclass(frozen=True)
class Observation:
    status: str                 # complete, exhausted, invalid
    value: object | None
    steps: int
    message: str = ""

def _invalid(msg: str, steps: int = 0): return Observation("invalid", None, steps, "OBSERVATION ERROR: " + msg)

def observe_num(value: Term, budget: int = 10000) -> Observation:
    step = Lam("tail", Lam("c", Lam("z", App(Var("c"), Var("tail")))))
    base = Lam("c", Lam("z", Var("z")))
    r = eval_target(App(App(value, step), base), budget)
    if r.status == "exhausted": return Observation("exhausted", None, r.steps, r.message)
    if r.status != "complete": return _invalid(r.message, r.steps)
    out = r.value
    if not isinstance(out, Lam) or not isinstance(out.body, Lam): return _invalid("natural observation is not two abstractions", r.steps)
    count, node = 0, out
    while True:
        if not isinstance(node, Lam) or not isinstance(node.body, Lam): return _invalid("malformed natural spine", r.steps)
        c, z, body = node.name, node.body.name, node.body.body
        if isinstance(body, Var) and body.name == z: break
        if not (isinstance(body, App) and isinstance(body.fn, Var) and body.fn.name == c):
            return _invalid("malformed natural spine", r.steps)
        count += 1; node = body.arg
    return Observation("complete", count, r.steps)

def observe_bool(value: Term, budget: int = 10000) -> Observation:
    left, right = Lam("left", Var("left")), Lam("right", Var("right"))
    r = eval_target(App(App(value, left), right), budget)
    if r.status == "exhausted": return Observation("exhausted", None, r.steps, r.message)
    if r.status != "complete": return _invalid(r.message, r.steps)
    out = r.value
    if out == left: return Observation("complete", True, r.steps)
    if out == right: return Observation("complete", False, r.steps)
    return _invalid("boolean selected neither marker", r.steps)

def observe_pair(value: Term, kinds: tuple, execution_budget: int = 10000, observation_budget: int = 10000) -> Observation:
    r = eval_target(value, execution_budget)
    if r.status == "exhausted": return Observation("exhausted", None, r.steps, r.message)
    if r.status != "complete": return _invalid(r.message, r.steps)
    if not isinstance(r.value, Lam): return _invalid("pair is not a lambda value", r.steps)
    def one(proj: Term, kind: tuple | str):
        q = eval_target(App(proj, r.value), observation_budget)
        if q.status != "complete": return Observation(q.status, None, q.steps, q.message)
        return observe_pair(q.value, kind, 0, observation_budget) if isinstance(kind, tuple) and kind and kind[0] == "pair" else (observe_num(q.value, observation_budget) if kind == "num" else observe_bool(q.value, observation_budget))
    a, b = one(FST, kinds[1]), one(SND, kinds[2])
    if a.status != "complete": return a
    if b.status != "complete": return b
    return Observation("complete", (a.value, b.value), r.steps + a.steps + b.steps)
