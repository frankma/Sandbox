# Coin Toss series

Brain teasers built on tossing fair coins. Each folder is self-contained, with the problem, a worked solution, runnable code, tests and a visual HTML page.

| # | Problem | Answer |
|---|---|---|
| 1 | [Guess the Other Coin](guess_the_other_coin/) | A guesses "same as mine", B guesses "opposite of mine": exactly one is right on every toss |
| 2 | [Four Coins on a Spinning Table](rotating_table/) | Flip blind: opposite, neighbours, opposite, one, opposite, neighbours, opposite (7 moves, the minimum) |

The code is pure Python 3 with no dependencies. To run all tests from this folder:

```bash
for d in guess_the_other_coin rotating_table; do python3 -m unittest discover -s $d -t . || break; done
```
