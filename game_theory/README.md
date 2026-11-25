# Game Theory

Strategy problems where every player's payoff depends on what the others do. Each folder is self-contained, with the problem, a worked solution, runnable code, tests and a visual HTML page.

| Problem | Topic | Answer |
|---|---|---|
| [Honor or Grab](honor_or_grab/) | $n$-team repeated social dilemma, decided rival by rival, with random ×3 bonus rounds | Reciprocate rival by rival; grab only in the final round |
| [Guess the Other Coin](guess_the_other_coin/) | Two-player team game: each sees only their own coin and guesses the other's | Bind the coins into one event: one bets they match, the other bets they don't |

The code is pure Python 3 with no dependencies. To run all tests from this folder:

```bash
for d in honor_or_grab guess_the_other_coin; do python3 -m unittest discover -s $d -t . || break; done
```
