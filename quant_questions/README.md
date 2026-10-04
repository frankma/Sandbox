# Brain Teasers

Each folder is self-contained, with the problem, a worked solution, runnable code, tests and a visual HTML page.

| Problem | Topic | Answer |
|---|---|---|
| [Heat-Equation Finite Difference](heat_equation_finite_difference/) | Crank–Nicolson for $V_t = (0.16 + 0.08\sin t)\,V_{xx}$ | $V(0.5, 1) \approx 0.0370$ (exact 0.0369996) |
| [Binomial Tree Betting Scheme](binomial_tree_betting_scheme/) | Replicating a ±\$100 World Series payoff with game-by-game bets | Bet \$31.25 on game 1 |
| [Honor or Grab](honor_or_grab/) | $n$-team repeated social dilemma, decided rival by rival, with random ×3 bonus rounds | Reciprocate rival by rival; grab only in the final round |

The first two problems come from the *Financial Mathematics and Modeling Practicum* (QuIC Financial Technologies, 2003–2010).

The code is pure Python 3 with no dependencies. To run all tests from this folder:

```bash
for d in heat_equation_finite_difference binomial_tree_betting_scheme honor_or_grab; do python3 -m unittest discover -s $d -t . || break; done
```
