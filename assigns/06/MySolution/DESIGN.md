# Design

The source AST remains the Assignment 5 AST. `Compiler` is compatible with its
`D0ExpVisitor` interface: each `accept` call invokes one visitor method. The
compiler never evaluates a source term. It translates every child before
combining it, so validation reaches unused branches and unapplied lambda bodies.
Negative `D0Eint` values and unsupported operators raise `COMPILER ERROR`.

The Assignment 5 module is not copied into Assignment 6. `source_path.py`
searches upward from the executing module until it finds the repository
directory containing `05/lambda1_vp.py`, then adds that exact `assigns/05`
directory to `sys.path`. The parser, demonstration runner, and tests therefore
use the supplied source classes regardless of the current working directory.
The compiler library itself remains independent of that module and relies on
the visitor-compatible `accept` protocol.

The target language is the immutable dataclasses `Var`, `Lam`, and `App`. Its
printer is recursive and uses `x`, `(lam x. body)`, and `(fn arg)` (the latter is
printed as the ordinary parenthesized application). Free-variable analysis and
substitution are structural. Substitution stops at a shadowing lambda; when a
replacement's free variable would be captured, it deterministically renames the
binding to the first unused `_aN` name before continuing.

The translation rules are:

```text
C[n] = NUM(n)                         C[b] = TRUE or FALSE
C[x] = x                              C[lam x.e] = lam x.C[e]
C[e1 e2] = C[e1] C[e2]                C[let x=e1 in e2] = (lam x.C[e2]) C[e1]
C[if c then t else f] = (C[c] (lam u.C[t]) (lam v.C[f])) I
C[pair a b] = PAIR C[a] C[b]         C[fst e] = FST C[e]
C[snd e] = SND C[e]                  C[fix f(x).e] = Z (lam f.lam x.C[e])
C[not e] = NOT C[e]                   C[op a b] = OP C[a] C[b]
```

`and` and `or` use the conditional rule: their right operands are placed in a
thunk and only the selected thunk is forced. `I` is a closed identity. Every
compiler-generated branch name is `_thenN` or `_elseN`, selected by a monotone
counter and avoided against every source identifier in the whole AST. Thus
ordinary source names such as `s`, `z`, `t`, `f`, and `x` remain available, and
the source free-variable set is preserved. Encoding terms are closed, so they
cannot capture source variables.

The interactive front end is deliberately separate from compilation. `parser.py`
supports both readable source notation (`lam x. x`, `if c then t else f`, and
`pair(a, b)`) and the literal constructor notation used by Assignment 5, such
as `D0Evar("x")` and `D0Elam("x", D0Evar("x"))`. It tokenizes without using
Python `eval`, constructs the supplied source AST, and passes that AST to
`compile_expr`. `app.py` supports a REPL with `:help`, `:quit`, and `:exit`, as
well as one-shot command-line expressions. It prints only the generated target
term; `demo.py` is the separate batch runner for execution and observation.

`church.py` uses the standard encodings: booleans select two arguments, numerals
iterate a successor, and pairs apply a selector to their two components.
Predecessor is the state-pair construction: its step maps `(previous,current)`
to `(current,current+1)`; after `n` iterations the first component is `n-1`,
with an initial zero state. Subtraction iterates predecessor and less-than or
greater-than comparisons combine non-strict ordering with inequality. Equality
is the conjunction of both directions of `<=`, and inequality is boolean
negation of equality. No target evaluator case recognizes an encoding or
performs host arithmetic.

`eval_target` is weak, deterministic, left-to-right call-by-value. It evaluates
the function, then argument, and contracts only when the function is a lambda
and the argument is a lambda. Each contraction increments the beta-value count;
alpha-renaming does not. A value takes zero steps, and a contraction consuming
the last budget is allowed; a further needed contraction reports exhaustion.
Inputs are immutable. The shared module also evaluates source ASTs with lexical
closures, source short-circuiting, left-to-right pairs/operations, and recursive
closures. The compiler and evaluator are intentionally separate.

Observers apply pure contexts through the same target evaluator. Naturals are
applied to `STEP = lam tail.lam c.lam z.c tail` and `BASE = lam c.lam z.z`, then
their finite lambda spine is counted without reducing under lambdas. Booleans
select two distinct identity markers. Pairs are evaluated first, projected by
the Church selectors, and recursively observed with separately bounded calls.
Incomplete or malformed outputs and observation exhaustion are distinct from a
decoded value.

The automated tests are divided by obligation: Church encoding semantics and
closure, nested pair observations, call-by-value divergence and short-circuit
control, recursion and lexical scope, exact target budgets, observer edge cases,
compiled-target structural purity, parser constructor coverage, and black-box
interactive CLI behavior. The CLI test launches `app.py` as a subprocess from
outside the project directory and exercises 125 valid inputs, which also
verifies that source-path resolution is not dependent on the working directory.

The correctness claim is: for closed, well-typed source programs that terminate
with a natural, boolean, or finite pair result, sufficient target reduction and
observation resources yield the same data. Application and let preserve CBV
order; Church operators preserve the corresponding data algebra; delayed
branches preserve source control flow; and `Z` produces a recursive function
value before recursive calls. Testing supports this claim but cannot prove it
for all untyped terms. Main tradeoffs are a simple substitution reducer (clear
and inspectable, but not optimized) and a large-step evaluator (easy budget
accounting, but divergent terms can consume considerable memory).
