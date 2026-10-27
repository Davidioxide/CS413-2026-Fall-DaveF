"""Visitor-based compositional compiler from Assignment 5 source ASTs."""
from __future__ import annotations
from target import Var, Lam, App, Term
from church import *
import church as E

class CompileError(Exception): pass

OPS = E.OPS

def _source_names(e: object) -> set[str]:
    tag = getattr(e, "ctag", type(e).__name__); out: set[str] = set()
    if tag == "D0Evar": out.add(e.arg1)
    elif tag in ("D0Elam",): out.add(e.arg1); out |= _source_names(e.arg2)
    elif tag == "D0Efix": out |= {e.arg1, e.arg2}; out |= _source_names(e.arg3)
    elif tag in ("D0Eint", "D0Ebtf"): pass
    elif tag == "D0Eop1": out.add(e.name); out |= _source_names(e.arg1)
    elif tag == "D0Eop2": out.add(e.name); out |= _source_names(e.arg1) | _source_names(e.arg2)
    elif tag in ("D0Eapp", "D0Epair"): out |= _source_names(e.arg1) | _source_names(e.arg2)
    elif tag in ("D0Eif0", "D0Elet"):
        if tag == "D0Elet": out.add(e.arg1)
        out |= _source_names(e.arg1) | _source_names(e.arg2) | (_source_names(e.arg3) if tag == "D0Eif0" else _source_names(e.arg3))
    elif tag in ("D0Epfst", "D0Epsnd"): out |= _source_names(e.arg1)
    return out

class Compiler:
    """Implements D0ExpVisitor's method names without importing the source module."""
    def __init__(self, root: object): self.used = _source_names(root); self.counter = 0
    def fresh(self, hint: str = "_c") -> str:
        while f"{hint}{self.counter}" in self.used: self.counter += 1
        name = f"{hint}{self.counter}"; self.used.add(name); self.counter += 1; return name
    def visit_int(self, e):
        if e.arg1 < 0: raise CompileError(f"COMPILER ERROR: D0Eint negative literal {e.arg1}")
        return num(e.arg1)
    def visit_btf(self, e): return TRUE if e.arg1 else FALSE
    def visit_var(self, e): return Var(e.arg1)
    def visit_lam(self, e): return Lam(e.arg1, e.arg2.accept(self))
    def visit_app(self, e): return App(e.arg1.accept(self), e.arg2.accept(self))
    def _branch(self, cond, yes, no):
        u, v = self.fresh("_then"), self.fresh("_else")
        return apps(cond, Lam(u, yes), Lam(v, no), IDENTITY)
    def visit_if0(self, e):
        c = e.arg1.accept(self); t = e.arg2.accept(self); f = e.arg3.accept(self)
        return self._branch(c, t, f)
    def visit_let(self, e): return App(Lam(e.arg1, e.arg3.accept(self)), e.arg2.accept(self))
    def visit_pair(self, e): return apps(PAIR, e.arg1.accept(self), e.arg2.accept(self))
    def visit_pfst(self, e): return App(FST, e.arg1.accept(self))
    def visit_psnd(self, e): return App(SND, e.arg1.accept(self))
    def visit_fix(self, e): return App(Z, Lam(e.arg1, Lam(e.arg2, e.arg3.accept(self))))
    def visit_op1(self, e):
        if e.name != "not": raise CompileError(f"COMPILER ERROR: D0Eop1 unsupported operator {e.name!r}")
        return App(NOT, e.arg1.accept(self))
    def visit_op2(self, e):
        if e.name not in OPS: raise CompileError(f"COMPILER ERROR: D0Eop2 unsupported operator {e.name!r}")
        left = e.arg1.accept(self)
        if e.name in ("and", "or"):
            right = e.arg2.accept(self)
            return self._branch(left, right, FALSE) if e.name == "and" else self._branch(left, TRUE, right)
        return apps(OPS[e.name], left, e.arg2.accept(self))

def compile_expr(source_expression: object) -> Term:
    try: return source_expression.accept(Compiler(source_expression))
    except CompileError: raise
    except AttributeError as exc: raise CompileError(f"COMPILER ERROR: unsupported source constructor {type(source_expression).__name__}") from exc
