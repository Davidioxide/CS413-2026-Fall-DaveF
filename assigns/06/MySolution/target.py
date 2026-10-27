"""Pure untyped lambda-calculus terms and capture-avoiding operations."""
from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Var:
    name: str

@dataclass(frozen=True)
class Lam:
    name: str
    body: Term

@dataclass(frozen=True)
class App:
    fn: Term
    arg: Term

Term = Var | Lam | App

def free_vars(t: Term) -> frozenset[str]:
    if isinstance(t, Var): return frozenset((t.name,))
    if isinstance(t, Lam): return free_vars(t.body) - {t.name}
    return free_vars(t.fn) | free_vars(t.arg)

def all_names(t: Term) -> set[str]:
    if isinstance(t, Var): return {t.name}
    if isinstance(t, Lam): return {t.name} | all_names(t.body)
    return all_names(t.fn) | all_names(t.arg)

def fresh_name(used: set[str], hint: str = "_c") -> str:
    i = 0
    while f"{hint}{i}" in used: i += 1
    return f"{hint}{i}"

def rename_bound(t: Term, old: str, new: str) -> Term:
    """Rename occurrences bound by the immediately surrounding binder."""
    if isinstance(t, Var): return Var(new if t.name == old else t.name)
    if isinstance(t, App): return App(rename_bound(t.fn, old, new), rename_bound(t.arg, old, new))
    if t.name == old: return t
    return Lam(t.name, rename_bound(t.body, old, new))

def substitute(t: Term, name: str, replacement: Term) -> Term:
    """Capture-avoiding [replacement/name]t; inputs are immutable."""
    if isinstance(t, Var): return replacement if t.name == name else t
    if isinstance(t, App):
        return App(substitute(t.fn, name, replacement), substitute(t.arg, name, replacement))
    if t.name == name: return t
    if t.name in free_vars(replacement) and name in free_vars(t.body):
        new = fresh_name(all_names(t.body) | all_names(replacement) | {name}, "_a")
        body = rename_bound(t.body, t.name, new)
        return Lam(new, substitute(body, name, replacement))
    return Lam(t.name, substitute(t.body, name, replacement))

def render(t: Term) -> str:
    if isinstance(t, Var): return t.name
    if isinstance(t, Lam): return f"(lam {t.name}. {render(t.body)})"
    return f"({render(t.fn)} {render(t.arg)})"

def is_value(t: Term) -> bool: return isinstance(t, Lam)
