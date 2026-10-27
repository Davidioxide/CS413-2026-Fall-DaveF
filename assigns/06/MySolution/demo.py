#!/usr/bin/env python3
"""Run the fourteen required end-to-end demonstrations."""
from __future__ import annotations
import sys
from source_path import ASSIGN05
sys.path.insert(0, str(ASSIGN05))
from lambda1_vp import *
from compiler import compile_expr
from evaluator import eval_target
from observers import observe_num, observe_bool
from target import render

def loop(): return D0Eapp(D0Efix("loop", "x", D0Eapp(D0Evar("loop"), D0Evar("x"))), D0Eint(0))
def factorial():
    b = D0Eif0(D0Eop2("==", D0Evar("n"), D0Eint(0)), D0Eint(1), D0Eop2("*", D0Evar("n"), D0Eapp(D0Evar("fact"), D0Eop2("-", D0Evar("n"), D0Eint(1)))))
    return D0Eapp(D0Efix("fact", "n", b), D0Eint(4))
def fibonacci():
    b = D0Eif0(D0Eop2("==", D0Evar("n"), D0Eint(0)), D0Eint(0), D0Eif0(D0Eop2("==", D0Evar("n"), D0Eint(1)), D0Eint(1), D0Eop2("+", D0Eapp(D0Evar("fib"), D0Eop2("-", D0Evar("n"), D0Eint(1))), D0Eapp(D0Evar("fib"), D0Eop2("-", D0Evar("n"), D0Eint(2))))))
    return D0Eapp(D0Efix("fib", "n", b), D0Eint(5))

CASES = [
 ("DEMO-01", D0Eop2("+", D0Eint(2), D0Eop2("*", D0Eint(3), D0Eint(4))), "num", 14),
 ("DEMO-02", D0Eop2("-", D0Eint(2), D0Eint(5)), "num", 0),
 ("DEMO-03", D0Eif0(D0Eop2("<=", D0Eint(2), D0Eint(3)), D0Eint(7), D0Eint(9)), "num", 7),
 ("DEMO-04", D0Elet("x", D0Eint(3), D0Eapp(D0Elam("y", D0Eop2("+", D0Evar("x"), D0Evar("y"))), D0Eint(4))), "num", 7),
 ("DEMO-05", D0Epfst(D0Epair(D0Eint(2), D0Ebtf(True))), "num", 2),
 ("DEMO-06", D0Epsnd(D0Epair(D0Eint(2), D0Ebtf(True))), "bool", True),
 ("DEMO-07", D0Eapp(D0Elam("f", D0Eapp(D0Evar("f"), D0Eint(3))), D0Elam("x", D0Eop2("+", D0Evar("x"), D0Eint(1)))), "num", 4),
 ("DEMO-08", D0Eif0(D0Ebtf(True), D0Eint(1), loop()), "num", 1),
 ("DEMO-09", D0Eapp(D0Elam("x", D0Eint(0)), loop()), "exhausted", None),
 ("DEMO-10", factorial(), "num", 24), ("DEMO-11", fibonacci(), "num", 5),
 ("DEMO-12", loop(), "exhausted", None),
 ("DEMO-13", D0Eop2("and", D0Ebtf(True), D0Ebtf(False)), "bool", False),
 ("DEMO-14", D0Eop2("or", D0Ebtf(False), D0Ebtf(True)), "bool", True),
]

def main() -> int:
    failures = 0; budget = 250000
    for ident, source, kind, expected in CASES:
        try: term = compile_expr(source)
        except Exception as exc:
            print(f"{ident}: COMPILATION ERROR: {exc}"); failures += 1; continue
        run = eval_target(term, budget)
        decoded = None; obs_status = "not-run"; obs_steps = 0
        if run.status == "complete":
            obs = observe_num(run.value, budget) if kind == "num" else observe_bool(run.value, budget)
            obs_status, obs_steps, decoded = obs.status, obs.steps, obs.value
        ok = (run.status == "complete" and obs_status == "complete" and decoded == expected) or (expected is None and run.status == "exhausted")
        if not ok: failures += 1
        print(f"{ident}: expected={expected!r} status={run.status} steps={run.steps} observation={obs_status} observation_steps={obs_steps} decoded={decoded!r}")
        print("  source:", type(source).__name__, "target:", render(term)[:180] + ("..." if len(render(term)) > 180 else ""))
    return 1 if failures else 0
if __name__ == "__main__": raise SystemExit(main())
