"""Small CLI parser for the Assignment 6 source language.

This parser is only for the interactive application; the compiler itself still
accepts Assignment 5 AST objects directly.
"""
from __future__ import annotations
import ast
import re
import sys
from source_path import ASSIGN05
sys.path.insert(0, str(ASSIGN05))
from lambda1_vp import (D0Eint, D0Ebtf, D0Evar, D0Elam, D0Eapp,
    D0Eop1, D0Eop2, D0Eif0, D0Elet, D0Epair, D0Epfst, D0Epsnd, D0Efix)

class ParseError(ValueError): pass

_token = re.compile(r'''\s*(?:(\d+)|("(?:\\.|[^"\\])*")|([A-Za-z_][A-Za-z0-9_]*)|(<=|>=|==|!=|[()+\-*<>=.,]))''')

def tokenize(text: str) -> list[str]:
    result, pos = [], 0
    while pos < len(text):
        match = _token.match(text, pos)
        if not match:
            if text[pos:].strip() == "": break
            raise ParseError(f"PARSER ERROR: unexpected input near {text[pos:]!r}")
        result.append(next(group for group in match.groups() if group is not None))
        pos = match.end()
    return result

class Parser:
    def __init__(self, text: str): self.tokens, self.pos = tokenize(text), 0
    def peek(self) -> str | None: return self.tokens[self.pos] if self.pos < len(self.tokens) else None
    def take(self, expected: str | None = None) -> str:
        actual = self.peek()
        if actual is None or (expected is not None and actual != expected):
            wanted = expected or "another token"
            raise ParseError(f"PARSER ERROR: expected {wanted!r}, got {actual!r}")
        self.pos += 1; return actual
    def parse(self):
        result = self.expr()
        if self.peek() is not None: raise ParseError(f"PARSER ERROR: unexpected token {self.peek()!r}")
        return result
    def expr(self, minimum: int = 0):
        left = self.prefix()
        precedence = {"or": 1, "and": 2, "==": 3, "!=": 3, "<": 3, "<=": 3, ">": 3, ">=": 3, "+": 4, "-": 4, "*": 5}
        while self.peek() in precedence and precedence[self.peek()] >= minimum:
            op = self.take(); right = self.expr(precedence[op] + 1); left = D0Eop2(op, left, right)
        return left
    def prefix(self):
        token = self.peek()
        if token == "not": self.take(); return D0Eop1("not", self.expr(6))
        if token == "-" and self.pos + 1 < len(self.tokens) and self.tokens[self.pos + 1].isdigit():
            self.take("-"); return D0Eint(-int(self.take()))
        if token == "if":
            self.take(); c = self.expr(); self.take("then"); t = self.expr(); self.take("else"); return D0Eif0(c, t, self.expr())
        if token == "let":
            self.take(); name = self.take(); self.take("="); init = self.expr(); self.take("in"); return D0Elet(name, init, self.expr())
        if token in ("lam", "lambda"):
            self.take(); name = self.take(); self.take("."); return D0Elam(name, self.expr())
        if token == "fix":
            self.take(); fn = self.take(); self.take("("); param = self.take(); self.take(")"); self.take("."); return D0Efix(fn, param, self.expr())
        return self.application()
    def application(self):
        result = self.atom()
        while self.peek() is not None and self.peek() not in (")", ",", "then", "else", "in") and self.peek() not in {"or", "and", "==", "!=", "<", "<=", ">", ">=", "+", "-", "*", "="}:
            result = D0Eapp(result, self.atom())
        return result
    def atom(self):
        token = self.peek()
        if token is None: raise ParseError("PARSER ERROR: expected an expression")
        if token in {"D0Eint", "D0Ebtf", "D0Evar", "D0Elam", "D0Eapp",
                     "D0Eop1", "D0Eop2", "D0Eif0", "D0Elet", "D0Epair",
                     "D0Epfst", "D0Epsnd", "D0Efix"}:
            return self.constructor()
        if token.isdigit(): self.take(); return D0Eint(int(token))
        if token == "true": self.take(); return D0Ebtf(True)
        if token == "false": self.take(); return D0Ebtf(False)
        # The assignment uses NUM(n), TRUE, and FALSE as documentation
        # abbreviations for Church encodings.  Accepting these spellings in
        # the CLI keeps the notation useful while still producing ordinary
        # source AST literals before compilation.
        if token in {"TRUE", "FALSE"}:
            self.take(); return D0Ebtf(token == "TRUE")
        if token == "NUM":
            self.take(); self.take("("); value = self.take()
            if not value.isdigit():
                raise ParseError("PARSER ERROR: NUM expects a natural-number literal")
            self.take(")"); return D0Eint(int(value))
        if token in ("fst", "snd"):
            self.take(); value = self.atom(); return D0Epfst(value) if token == "fst" else D0Epsnd(value)
        if token == "pair":
            self.take()
            if self.peek() == "(":
                self.take(); left = self.expr(); self.take(","); right = self.expr(); self.take(")")
            else:
                left, right = self.atom(), self.atom()
            return D0Epair(left, right)
        if token == "(":
            self.take(); result = self.expr(); self.take(")"); return result
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", token): self.take(); return D0Evar(token)
        raise ParseError(f"PARSER ERROR: unexpected token {token!r}")

    def constructor(self):
        """Parse the literal constructor notation used by Assignment 5."""
        name = self.take(); self.take("(")
        if name == "D0Eint":
            sign = -1 if self.peek() == "-" else 1
            if sign == -1: self.take("-")
            value = sign * int(self.take()); self.take(")"); return D0Eint(value)
        if name == "D0Ebtf":
            value = self.take()
            if value not in ("true", "false", "True", "False"):
                raise ParseError("PARSER ERROR: D0Ebtf expects a boolean")
            self.take(")"); return D0Ebtf(value.lower() == "true")
        if name == "D0Evar":
            value = self.string_arg(); self.take(")"); return D0Evar(value)
        if name == "D0Elam":
            binder = self.string_arg(); self.take(","); body = self.expr(); self.take(")")
            return D0Elam(binder, body)
        if name == "D0Elet":
            binder = self.string_arg(); self.take(","); init = self.expr()
            self.take(","); body = self.expr(); self.take(")")
            return D0Elet(binder, init, body)
        if name == "D0Efix":
            function = self.string_arg(); self.take(","); parameter = self.string_arg(); self.take(",")
            body = self.expr(); self.take(")"); return D0Efix(function, parameter, body)
        if name in ("D0Eop1", "D0Epfst", "D0Epsnd"):
            if name == "D0Eop1":
                operator = self.string_arg(); self.take(","); value = self.expr(); self.take(")")
                return D0Eop1(operator, value)
            value = self.expr(); self.take(")")
            return D0Epfst(value) if name == "D0Epfst" else D0Epsnd(value)
        if name in ("D0Eapp", "D0Epair"):
            left = self.expr(); self.take(","); right = self.expr(); self.take(")")
            return D0Eapp(left, right) if name == "D0Eapp" else D0Epair(left, right)
        if name == "D0Eop2":
            operator = self.string_arg(); self.take(","); left = self.expr(); self.take(","); right = self.expr(); self.take(")")
            return D0Eop2(operator, left, right)
        if name == "D0Eif0":
            condition = self.expr(); self.take(","); yes = self.expr(); self.take(","); no = self.expr(); self.take(")")
            return D0Eif0(condition, yes, no)
        raise ParseError(f"PARSER ERROR: unsupported constructor {name}")

    def string_arg(self) -> str:
        token = self.take()
        if not (len(token) >= 2 and token[0] == '"'):
            raise ParseError("PARSER ERROR: expected a quoted string")
        value = ast.literal_eval(token)
        if not isinstance(value, str): raise ParseError("PARSER ERROR: expected a string")
        return value

def parse(text: str): return Parser(text).parse()
