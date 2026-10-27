"""Closed Church encodings, all returned as pure target ASTs."""
from target import Var, Lam, App, Term

def apps(fn: Term, *args: Term) -> Term:
    for arg in args: fn = App(fn, arg)
    return fn
def lams(*names: str, body: Term) -> Term:
    for name in reversed(names): body = Lam(name, body)
    return body
def num(n: int) -> Term:
    if n < 0: raise ValueError("encoding numeral must be nonnegative")
    body: Term = Var("z")
    for _ in range(n): body = App(Var("s"), body)
    return lams("s", "z", body=body)
TRUE = lams("t", "f", body=Var("t")); FALSE = lams("t", "f", body=Var("f"))
IDENTITY = Lam("w", Var("w"))
PAIR = lams("a", "b", "p", body=apps(Var("p"), Var("a"), Var("b")))
FST = Lam("p", App(Var("p"), TRUE)); SND = Lam("p", App(Var("p"), FALSE))
SUCC = lams("n", "s", "z", body=App(Var("s"), apps(Var("n"), Var("s"), Var("z"))))
ADD = lams("m", "n", "s", "z", body=apps(Var("m"), Var("s"), apps(Var("n"), Var("s"), Var("z"))))
MUL = lams("m", "n", "s", body=apps(Var("m"), App(Var("n"), Var("s"))))
_PSTEP = lams("g", "h", body=apps(Var("h"), App(Var("g"), Var("s"))))
PRED = lams("n", "s", "z", body=apps(Var("n"), _PSTEP, Lam("u", Var("z")), Lam("u", Var("u"))))
ISZERO = lams("n", body=apps(Var("n"), Lam("x", FALSE), TRUE))
SUB = lams("m", "n", body=apps(Var("n"), PRED, Var("m")))
LEQ = lams("m", "n", body=apps(ISZERO, apps(SUB, Var("m"), Var("n"))))
AND = lams("p", "q", body=apps(Var("p"), Var("q"), FALSE))
OR = lams("p", "q", body=apps(Var("p"), TRUE, Var("q")))
NOT = Lam("b", apps(Var("b"), FALSE, TRUE))
EQ = lams("m", "n", body=apps(AND, apps(LEQ, Var("m"), Var("n")), apps(LEQ, Var("n"), Var("m"))))
NEQ = lams("m", "n", body=App(NOT, apps(EQ, Var("m"), Var("n"))))
LT = lams("m", "n", body=apps(AND, apps(LEQ, Var("m"), Var("n")), apps(NEQ, Var("m"), Var("n"))))
GT = lams("m", "n", body=apps(AND, apps(LEQ, Var("n"), Var("m")), apps(NEQ, Var("m"), Var("n"))))
GE = lams("m", "n", body=apps(LEQ, Var("n"), Var("m")))
Z = Lam("g", App(Lam("x", App(Var("g"), Lam("v", apps(Var("x"), Var("x"), Var("v"))))), Lam("x", App(Var("g"), Lam("v", apps(Var("x"), Var("x"), Var("v")))))))
OPS = {"+": ADD, "-": SUB, "*": MUL, "<": LT, "<=": LEQ, ">": GT, ">=": GE, "==": EQ, "!=": NEQ, "and": AND, "or": OR}
