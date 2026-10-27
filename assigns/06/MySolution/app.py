#!/usr/bin/env python3
"""Interactive Assignment 6 source-to-pure-lambda compiler."""
from __future__ import annotations
import argparse
from compiler import CompileError, compile_expr
from evaluator import eval_target
from observers import observe_bool, observe_num, observe_pair
from parser import ParseError, parse
from target import render

HELP = "Enter source expressions; commands: :help, :quit, :exit; answer y/n to observe"
OBSERVATION_BUDGET = 100_000

def main() -> int:
    arg = argparse.ArgumentParser(description="Compile Assignment 6 source language to pure lambda calculus")
    arg.add_argument("expression", nargs="*", help="compile one expression and exit")
    args = arg.parse_args()
    if args.expression:
        return compile_one(" ".join(args.expression))
    print(HELP)
    while True:
        try: text = input("source> ")
        except EOFError:
            print(); return 0
        if not text.strip(): continue
        if text.strip() in (":quit", ":exit"): return 0
        if text.strip() == ":help": print(HELP); continue
        compile_one(text, ask_to_observe=True)

def compile_one(text: str, *, ask_to_observe: bool = True) -> int:
    try:
        source = parse(text)
        term = compile_expr(source)
        print(render(term))
        if ask_to_observe:
            observe_from_cli(source, term)
        return 0
    except (ParseError, CompileError) as exc:
        print(exc)
        return 1


def _kind(expr: object, environment: dict[str, object] | None = None):
    """Infer the observable data kind for the small CLI source language.

    The compiler itself remains untyped.  This lightweight analysis only gives
    the CLI the expected kind required by the bounded observers; it does not
    reject programs or replace source evaluation.
    """
    environment = {} if environment is None else environment
    tag = getattr(expr, "ctag", type(expr).__name__)
    if tag == "D0Eint": return "num"
    if tag == "D0Ebtf": return "bool"
    if tag == "D0Evar": return environment.get(expr.arg1)
    if tag == "D0Eop1": return "bool" if expr.name == "not" else None
    if tag == "D0Eop2":
        return "num" if expr.name in {"+", "-", "*"} else "bool"
    if tag == "D0Eif0":
        yes, no = _kind(expr.arg2, environment), _kind(expr.arg3, environment)
        return yes if yes == no else None
    if tag == "D0Elet":
        bindings = environment.copy()
        bindings[expr.arg1] = _kind(expr.arg2, environment)
        return _kind(expr.arg3, bindings)
    if tag == "D0Epair":
        return ("pair", _kind(expr.arg1, environment), _kind(expr.arg2, environment))
    if tag in {"D0Epfst", "D0Epsnd"}:
        pair_kind = _kind(expr.arg1, environment)
        if isinstance(pair_kind, tuple) and pair_kind[0] == "pair":
            return pair_kind[1 if tag == "D0Epfst" else 2]
        return None
    if tag == "D0Eapp":
        if getattr(expr.arg1, "ctag", None) in {"D0Elam", "D0Efix"}:
            bindings = environment.copy()
            if expr.arg1.ctag == "D0Elam":
                bindings[expr.arg1.arg1] = _kind(expr.arg2, environment)
                return _kind(expr.arg1.arg2, bindings)
            bindings[expr.arg1.arg1] = "function"
            bindings[expr.arg1.arg2] = _kind(expr.arg2, environment)
            return _kind(expr.arg1.arg3, bindings)
        return None
    return None


def _format_observed(value: object) -> str:
    if isinstance(value, bool): return "true" if value else "false"
    if isinstance(value, tuple):
        return "(" + ", ".join(_format_observed(item) for item in value) + ")"
    return str(value)


def observe_from_cli(source: object, term: object) -> None:
    """Ask whether to decode the compiled value, using EOF as no."""
    try:
        answer = input("Observe value? [y/n]: ").strip().lower()
    except EOFError:
        return
    if answer == "n":
        return
    if answer != "y":
        print("OBSERVATION ERROR: please answer y or n")
        return

    kind = _kind(source)
    if kind is None or (isinstance(kind, tuple) and None in kind[1:]):
        print("OBSERVATION ERROR: could not infer the result kind")
        return
    run = eval_target(term, OBSERVATION_BUDGET)
    if run.status != "complete":
        print(run.message)
        return
    if kind == "num":
        observation = observe_num(run.value, OBSERVATION_BUDGET)
    elif kind == "bool":
        observation = observe_bool(run.value, OBSERVATION_BUDGET)
    else:
        observation = observe_pair(run.value, kind, OBSERVATION_BUDGET, OBSERVATION_BUDGET)
    if observation.status == "complete":
        print(_format_observed(observation.value))
    else:
        print(observation.message)

if __name__ == "__main__": raise SystemExit(main())
