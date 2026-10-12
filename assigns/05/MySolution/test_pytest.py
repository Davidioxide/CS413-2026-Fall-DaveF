import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lambda1_vp import (D0Eapp, D0Ebtf, D0Efix, D0Eif0, D0Eint, D0Elet,
                        D0Elam, D0Eop1, D0Eop2, D0Epair, D0Epfst, D0Epsnd,
                        D0Evar, d0exp_fvset)
from solution import d0exp_pretty, d0exp_substitute


def test_pretty_nested_complete_expression():
    expr = D0Eapp(
        D0Elam("x", D0Eop2("+", D0Evar("x"), D0Eint(1))),
        D0Eif0(D0Ebtf(False), D0Eint(-2), D0Epair(D0Ebtf(True), D0Eint(10**30))),
    )
    assert d0exp_pretty(expr) == "((lam x. (x + 1)) (if false then -2 else (pair true 1000000000000000000000000000000)))"


def test_substitution_preserves_replacement_and_all_scopes():
    expr = D0Elet(
        "z", D0Evar("x"),
        D0Efix("f", "y", D0Elam("w", D0Epair(D0Evar("x"), D0Evar("z")))),
    )
    result = d0exp_substitute(expr, "x", D0Evar("z"))
    assert d0exp_pretty(result) == "(let z_1 = z in (fix f(y). (lam w. (pair z z_1))))"
    assert d0exp_pretty(D0Evar("z")) == "z"


def test_fix_binder_shadowing_and_equal_names():
    assert d0exp_pretty(d0exp_substitute(
        D0Efix("f", "x", D0Evar("f")), "f", D0Eint(0))) == "(fix f(x). f)"
    assert d0exp_pretty(d0exp_substitute(
        D0Efix("x", "x", D0Evar("x")), "x", D0Eint(0))) == "(fix x(x). x)"


def test_free_variable_property():
    examples = [
        (D0Eop2("+", D0Evar("x"), D0Evar("z")), D0Evar("y")),
        (D0Elam("a", D0Eapp(D0Evar("x"), D0Evar("a"))), D0Epair(D0Evar("b"), D0Evar("x"))),
        (D0Elet("a", D0Evar("x"), D0Evar("a")), D0Eint(4)),
    ]
    for expr, replacement in examples:
        result = d0exp_substitute(expr, "x", replacement)
        assert d0exp_fvset(result) == (d0exp_fvset(expr) - {"x"}) | d0exp_fvset(replacement)


def test_no_substitution_keeps_alpha_equivalent_structure_and_is_deterministic():
    expr = D0Elam("x", D0Elet("y", D0Eint(1), D0Evar("y")))
    snapshot = copy.deepcopy(expr)
    one = d0exp_substitute(expr, "missing", D0Evar("y"))
    two = d0exp_substitute(expr, "missing", D0Evar("y"))
    assert one == two == expr
    assert expr == snapshot


def test_every_constructor_is_traversed_by_substitution():
    expr = D0Eif0(
        D0Eop1("+1", D0Evar("x")),
        D0Eapp(D0Evar("x"), D0Epfst(D0Evar("x"))),
        D0Epsnd(D0Epair(D0Evar("x"), D0Evar("q"))),
    )
    result = d0exp_substitute(expr, "x", D0Eint(9))
    assert d0exp_pretty(result) == "(if (+1 9) then (9 (fst 9)) else (snd (pair 9 q)))"
