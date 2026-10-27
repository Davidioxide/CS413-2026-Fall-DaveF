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
    # Share one freshness set across the entire substitution.  A separate
    # fresh-name search at each nested binder can otherwise generate the same
    # name twice in one call, despite the assignment's freshness requirement.
    used = all_names(t) | all_names(replacement) | {name}

    def fresh() -> str:
        candidate = fresh_name(used, "_a")
        used.add(candidate)
        return candidate

    def go(term: Term) -> Term:
        if isinstance(term, Var): return replacement if term.name == name else term
        if isinstance(term, App):
            return App(go(term.fn), go(term.arg))
        if term.name == name: return term
        if term.name in free_vars(replacement) and name in free_vars(term.body):
            new = fresh()
            body = rename_bound(term.body, term.name, new)
            return Lam(new, go(body))
        return Lam(term.name, go(term.body))

    return go(t)

def render(t: Term) -> str:
    if isinstance(t, Var): return t.name
    if isinstance(t, Lam): return f"(lam {t.name}. {render(t.body)})"
    return f"({render(t.fn)} {render(t.arg)})"

def is_value(t: Term) -> bool: return isinstance(t, Lam)
