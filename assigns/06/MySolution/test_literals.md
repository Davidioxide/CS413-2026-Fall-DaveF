# CLI Test Literals

From `assigns/06/`, run any expression in the fenced block with:

```text
python3 MySolution/app.py 'EXPRESSION'
```

To observe a result after the compiled lambda term, pipe `y` to the command:

```text
printf 'y\n' | python3 MySolution/app.py 'true'
```

Every line in the fenced block is an expression in the Assignment 6 source
language accepted by `app.py`. These are source-language expressions, not
Python constructor calls from `assigns/05/lambda1_vp.py` and not target-lambda
terms. The recursive examples exercise `fix`; `app.py` compiles them but does
not execute them.

```text
0
42
NUM(2)
true
false
TRUE
FALSE
lam x. x
lambda x. x + 1
lam x. lam y. x
((lam x. x + 1) 4)
let x = 3 in x + 4
let f = lam x. x * 2 in f 5
2 + 3
8 - 3
3 - 8
2 * 3 + 1
2 < 3
2 <= 2
3 > 2
3 >= 3
2 == 2
2 != 3
not false
if true then 1 else 0
pair(2, true)
pair 2 true
fst(pair(2, true))
snd(pair(2, true))
true and false
false or true
true and (2 == 2)
false or (3 < 4)
fix loop(x). loop x
fix f(x). if x == 0 then 0 else f (x - 1)
(fix fact(n). if n == 0 then 1 else n * fact (n - 1)) 4
```
