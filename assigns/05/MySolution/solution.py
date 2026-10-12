"""Pretty printing and capture-avoiding substitution for lambda1_vp."""

from __future__ import annotations

import sys
from pathlib import Path

_ASSIGNMENT_DIR = str(Path(__file__).resolve().parent.parent)
if _ASSIGNMENT_DIR not in sys.path:
    sys.path.insert(0, _ASSIGNMENT_DIR)

from lambda1_vp import (  # noqa: E402
    D0E000, D0Eapp, D0Ebtf, D0Efix, D0Eif0, D0Eint, D0Elet,
    D0Elam, D0Eop1, D0Eop2, D0Epair, D0Epfst, D0Epsnd, D0Evar,
    D0ExpVisitor, d0exp, d0exp_fvset,
)


class PrettyPrintVisitor(D0ExpVisitor[str]):
    """Render every expression form without evaluating it."""

    def visit_int(self, dexp: D0Eint) -> str:
        return str(dexp.arg1)

    def visit_btf(self, dexp: D0Ebtf) -> str:
        return "true" if dexp.arg1 else "false"

    def visit_var(self, dexp: D0Evar) -> str:
        return dexp.arg1

    def visit_op1(self, dexp: D0Eop1) -> str:
        return f"({dexp.name} {dexp.arg1.accept(self)})"

    def visit_op2(self, dexp: D0Eop2) -> str:
        return f"({dexp.arg1.accept(self)} {dexp.name} {dexp.arg2.accept(self)})"

    def visit_lam(self, dexp: D0Elam) -> str:
        return f"(lam {dexp.arg1}. {dexp.arg2.accept(self)})"

    def visit_fix(self, dexp: D0Efix) -> str:
        return f"(fix {dexp.arg1}({dexp.arg2}). {dexp.arg3.accept(self)})"

    def visit_app(self, dexp: D0Eapp) -> str:
        return f"({dexp.arg1.accept(self)} {dexp.arg2.accept(self)})"

    def visit_if0(self, dexp: D0Eif0) -> str:
        return (f"(if {dexp.arg1.accept(self)} then "
                f"{dexp.arg2.accept(self)} else {dexp.arg3.accept(self)})")

    def visit_let(self, dexp: D0Elet) -> str:
        return (f"(let {dexp.arg1} = {dexp.arg2.accept(self)} in "
                f"{dexp.arg3.accept(self)})")

    def visit_pair(self, dexp: D0Epair) -> str:
        return f"(pair {dexp.arg1.accept(self)} {dexp.arg2.accept(self)})"

    def visit_pfst(self, dexp: D0Epfst) -> str:
        return f"(fst {dexp.arg1.accept(self)})"

    def visit_psnd(self, dexp: D0Epsnd) -> str:
        return f"(snd {dexp.arg1.accept(self)})"


def d0exp_pretty(expression: d0exp) -> str:
    return expression.accept(PrettyPrintVisitor())


class NameCollectorVisitor(D0ExpVisitor[set[str]]):
    """Collect every variable occurrence and binder name."""

    def visit_int(self, dexp: D0Eint) -> set[str]:
        return set()

    def visit_btf(self, dexp: D0Ebtf) -> set[str]:
        return set()

    def visit_var(self, dexp: D0Evar) -> set[str]:
        return {dexp.arg1}

    def visit_op1(self, dexp: D0Eop1) -> set[str]:
        return dexp.arg1.accept(self)

    def visit_op2(self, dexp: D0Eop2) -> set[str]:
        return dexp.arg1.accept(self) | dexp.arg2.accept(self)

    def visit_lam(self, dexp: D0Elam) -> set[str]:
        return {dexp.arg1} | dexp.arg2.accept(self)

    def visit_fix(self, dexp: D0Efix) -> set[str]:
        return {dexp.arg1, dexp.arg2} | dexp.arg3.accept(self)

    def visit_app(self, dexp: D0Eapp) -> set[str]:
        return dexp.arg1.accept(self) | dexp.arg2.accept(self)

    def visit_if0(self, dexp: D0Eif0) -> set[str]:
        return (dexp.arg1.accept(self) | dexp.arg2.accept(self)
                | dexp.arg3.accept(self))

    def visit_let(self, dexp: D0Elet) -> set[str]:
        return {dexp.arg1} | dexp.arg2.accept(self) | dexp.arg3.accept(self)

    def visit_pair(self, dexp: D0Epair) -> set[str]:
        return dexp.arg1.accept(self) | dexp.arg2.accept(self)

    def visit_pfst(self, dexp: D0Epfst) -> set[str]:
        return dexp.arg1.accept(self)

    def visit_psnd(self, dexp: D0Epsnd) -> set[str]:
        return dexp.arg1.accept(self)


class BoundRenameVisitor(D0ExpVisitor[d0exp]):
    """Rename one binding's occurrences, stopping at shadowing binders."""

    def __init__(self, old: str, new: str) -> None:
        self.old = old
        self.new = new

    def visit_int(self, dexp: D0Eint) -> d0exp:
        return D0Eint(dexp.arg1)

    def visit_btf(self, dexp: D0Ebtf) -> d0exp:
        return D0Ebtf(dexp.arg1)

    def visit_var(self, dexp: D0Evar) -> d0exp:
        return D0Evar(self.new if dexp.arg1 == self.old else dexp.arg1)

    def visit_op1(self, dexp: D0Eop1) -> d0exp:
        return D0Eop1(dexp.name, dexp.arg1.accept(self))

    def visit_op2(self, dexp: D0Eop2) -> d0exp:
        return D0Eop2(dexp.name, dexp.arg1.accept(self), dexp.arg2.accept(self))

    def visit_lam(self, dexp: D0Elam) -> d0exp:
        if dexp.arg1 == self.old:
            return D0Elam(dexp.arg1, dexp.arg2)
        return D0Elam(dexp.arg1, dexp.arg2.accept(self))

    def visit_fix(self, dexp: D0Efix) -> d0exp:
        if dexp.arg1 == self.old or dexp.arg2 == self.old:
            return D0Efix(dexp.arg1, dexp.arg2, dexp.arg3)
        return D0Efix(dexp.arg1, dexp.arg2, dexp.arg3.accept(self))

    def visit_app(self, dexp: D0Eapp) -> d0exp:
        return D0Eapp(dexp.arg1.accept(self), dexp.arg2.accept(self))

    def visit_if0(self, dexp: D0Eif0) -> d0exp:
        return D0Eif0(dexp.arg1.accept(self), dexp.arg2.accept(self),
                      dexp.arg3.accept(self))

    def visit_let(self, dexp: D0Elet) -> d0exp:
        init = dexp.arg2.accept(self)
        if dexp.arg1 == self.old:
            return D0Elet(dexp.arg1, init, dexp.arg3)
        return D0Elet(dexp.arg1, init, dexp.arg3.accept(self))

    def visit_pair(self, dexp: D0Epair) -> d0exp:
        return D0Epair(dexp.arg1.accept(self), dexp.arg2.accept(self))

    def visit_pfst(self, dexp: D0Epfst) -> d0exp:
        return D0Epfst(dexp.arg1.accept(self))

    def visit_psnd(self, dexp: D0Epsnd) -> d0exp:
        return D0Epsnd(dexp.arg1.accept(self))


class TargetOccurrenceVisitor(D0ExpVisitor[bool]):
    """Find target occurrences not hidden by a binder name."""

    def __init__(self, target: str, barrier: str) -> None:
        self.target = target
        self.barrier = barrier

    def visit_int(self, dexp: D0Eint) -> bool: return False
    def visit_btf(self, dexp: D0Ebtf) -> bool: return False
    def visit_var(self, dexp: D0Evar) -> bool: return dexp.arg1 == self.target
    def visit_op1(self, dexp: D0Eop1) -> bool: return dexp.arg1.accept(self)
    def visit_op2(self, dexp: D0Eop2) -> bool:
        return dexp.arg1.accept(self) or dexp.arg2.accept(self)
    def visit_app(self, dexp: D0Eapp) -> bool:
        return dexp.arg1.accept(self) or dexp.arg2.accept(self)
    def visit_if0(self, dexp: D0Eif0) -> bool:
        return (dexp.arg1.accept(self) or dexp.arg2.accept(self)
                or dexp.arg3.accept(self))
    def visit_pair(self, dexp: D0Epair) -> bool:
        return dexp.arg1.accept(self) or dexp.arg2.accept(self)
    def visit_pfst(self, dexp: D0Epfst) -> bool: return dexp.arg1.accept(self)
    def visit_psnd(self, dexp: D0Epsnd) -> bool: return dexp.arg1.accept(self)

    def visit_lam(self, dexp: D0Elam) -> bool:
        if dexp.arg1 in (self.target, self.barrier): return False
        return dexp.arg2.accept(self)

    def visit_fix(self, dexp: D0Efix) -> bool:
        if (dexp.arg1 in (self.target, self.barrier)
                or dexp.arg2 in (self.target, self.barrier)):
            return False
        return dexp.arg3.accept(self)

    def visit_let(self, dexp: D0Elet) -> bool:
        if dexp.arg2.accept(self): return True
        if dexp.arg1 in (self.target, self.barrier): return False
        return dexp.arg3.accept(self)


class SubstitutionVisitor(D0ExpVisitor[d0exp]):
    """Capture-avoiding single substitution with deterministic alpha-renaming."""

    def __init__(self, target: str, replacement: d0exp, original: d0exp) -> None:
        self.target = target
        self.replacement = replacement
        self.replacement_fv = d0exp_fvset(replacement)
        self.used = original.accept(NameCollectorVisitor()) | replacement.accept(NameCollectorVisitor()) | {target}
        self.counters: dict[str, int] = {}

    def _fresh(self, base: str) -> str:
        counter = self.counters.get(base, 0) + 1
        candidate = f"{base}_{counter}"
        while candidate in self.used:
            counter += 1
            candidate = f"{base}_{counter}"
        self.counters[base] = counter
        self.used.add(candidate)
        return candidate

    def _renames(self, body: d0exp, names: tuple[str, ...]) -> tuple[d0exp, tuple[str, ...]]:
        result = body
        fresh_names: list[str] = []
        for name in names:
            fresh = self._fresh(name)
            result = result.accept(BoundRenameVisitor(name, fresh))
            fresh_names.append(fresh)
        return result, tuple(fresh_names)

    def _needs(self, body: d0exp, name: str) -> bool:
        return name in self.replacement_fv and body.accept(TargetOccurrenceVisitor(self.target, name))

    def visit_int(self, dexp: D0Eint) -> d0exp: return D0Eint(dexp.arg1)
    def visit_btf(self, dexp: D0Ebtf) -> d0exp: return D0Ebtf(dexp.arg1)

    def visit_var(self, dexp: D0Evar) -> d0exp:
        return self.replacement if dexp.arg1 == self.target else D0Evar(dexp.arg1)

    def visit_op1(self, dexp: D0Eop1) -> d0exp:
        return D0Eop1(dexp.name, dexp.arg1.accept(self))

    def visit_op2(self, dexp: D0Eop2) -> d0exp:
        return D0Eop2(dexp.name, dexp.arg1.accept(self), dexp.arg2.accept(self))

    def visit_lam(self, dexp: D0Elam) -> d0exp:
        if dexp.arg1 == self.target:
            return D0Elam(dexp.arg1, dexp.arg2)
        name = dexp.arg1
        body = dexp.arg2
        if self._needs(body, name):
            fresh = self._fresh(name)
            name = fresh
            body = body.accept(BoundRenameVisitor(dexp.arg1, fresh))
        return D0Elam(name, body.accept(self))

    def visit_fix(self, dexp: D0Efix) -> d0exp:
        if dexp.arg1 == self.target or dexp.arg2 == self.target:
            return D0Efix(dexp.arg1, dexp.arg2, dexp.arg3)
        body = dexp.arg3
        f_name, x_name = dexp.arg1, dexp.arg2
        if f_name == x_name:
            if self._needs(body, f_name):
                fresh = self._fresh(f_name)
                body = body.accept(BoundRenameVisitor(f_name, fresh))
                f_name = x_name = fresh
        else:
            if self._needs(body, f_name):
                fresh = self._fresh(f_name)
                body = body.accept(BoundRenameVisitor(f_name, fresh))
                f_name = fresh
            if self._needs(body, x_name):
                fresh = self._fresh(x_name)
                body = body.accept(BoundRenameVisitor(x_name, fresh))
                x_name = fresh
        return D0Efix(f_name, x_name, body.accept(self))

    def visit_app(self, dexp: D0Eapp) -> d0exp:
        return D0Eapp(dexp.arg1.accept(self), dexp.arg2.accept(self))

    def visit_if0(self, dexp: D0Eif0) -> d0exp:
        return D0Eif0(dexp.arg1.accept(self), dexp.arg2.accept(self),
                      dexp.arg3.accept(self))

    def visit_let(self, dexp: D0Elet) -> d0exp:
        init = dexp.arg2.accept(self)
        if dexp.arg1 == self.target:
            return D0Elet(dexp.arg1, init, dexp.arg3)
        name = dexp.arg1
        body = dexp.arg3
        if self._needs(body, name):
            fresh = self._fresh(name)
            name = fresh
            body = body.accept(BoundRenameVisitor(dexp.arg1, fresh))
        return D0Elet(name, init, body.accept(self))

    def visit_pair(self, dexp: D0Epair) -> d0exp:
        return D0Epair(dexp.arg1.accept(self), dexp.arg2.accept(self))

    def visit_pfst(self, dexp: D0Epfst) -> d0exp:
        return D0Epfst(dexp.arg1.accept(self))

    def visit_psnd(self, dexp: D0Epsnd) -> d0exp:
        return D0Epsnd(dexp.arg1.accept(self))


def d0exp_substitute(expression: d0exp, variable: str, replacement: d0exp) -> d0exp:
    return expression.accept(SubstitutionVisitor(variable, replacement, expression))


__all__ = [
    "PrettyPrintVisitor", "SubstitutionVisitor", "NameCollectorVisitor",
    "d0exp_pretty", "d0exp_substitute",
]
