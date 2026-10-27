#!/usr/bin/env python3
"""Interactive Assignment 6 source-to-pure-lambda compiler."""
from __future__ import annotations
import argparse
from compiler import CompileError, compile_expr
from parser import ParseError, parse
from target import render

HELP = "Enter source expressions; commands: :help, :quit, :exit"

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
        compile_one(text)

def compile_one(text: str) -> int:
    try:
        print(render(compile_expr(parse(text))))
        return 0
    except (ParseError, CompileError) as exc:
        print(exc)
        return 1

if __name__ == "__main__": raise SystemExit(main())
