# Testing

From `assigns/06/`:

```text
PYTHONPATH=MySolution python3 -m unittest discover -s MySolution/tests -p 'test_*.py'
PYTHONPATH=MySolution python3 MySolution/demo.py
make -C MySolution all
python3 MySolution/app.py '2 + 3 * 4'
```

The tests cover capture avoidance, weak CBV and budget boundaries, observers,
free-variable preservation and immutability, validation of unused branches and
negative literals, and short-circuit compilation. The demo covers all fourteen
mandatory examples, including factorial, Fibonacci, nested data, and bounded
divergence.
