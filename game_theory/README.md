# Game Theory

Strategy problems where every player's payoff depends on what the others do. Each folder is self-contained, with the problem, a worked solution, runnable code, tests and a visual HTML page.

| Problem | Topic | Answer |
|---|---|---|
| [Honor or Grab](honor_or_grab/) | $n$-team repeated social dilemma, decided rival by rival, with random ×3 bonus rounds | Reciprocate rival by rival; grab only in the final round |

The code is pure Python 3 with no dependencies. To run all tests from this folder:

```bash
for d in honor_or_grab; do python3 -m unittest discover -s $d -t . || break; done
```
