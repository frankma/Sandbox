# Coin Toss series

Brain teasers built on tossing fair coins. Each folder is self-contained, with the problem, a worked solution, runnable code, tests and a visual HTML page.

| # | Problem | Answer |
|---|---|---|
| 1 | [Four Coins on a Spinning Table](rotating_table/) | Flip blind: opposite, neighbours, opposite, one, opposite, neighbours, opposite (7 moves, the minimum) |

The code is pure Python 3 with no dependencies. To run all tests from this folder:

```bash
for d in rotating_table; do python3 -m unittest discover -s $d -t . || break; done
```
