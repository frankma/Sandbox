# Quant Problems

Each folder is self-contained, with the problem, a worked solution and a visual HTML page. All but The Threshold also have runnable code and tests.

| Problem | Topic | Answer |
|---|---|---|
| [Heat-Equation Finite Difference](heat_equation_finite_difference/) | Crank–Nicolson for $V_t = (0.16 + 0.08\sin t)\,V_{xx}$ | $V(0.5, 1) \approx 0.0370$ (exact 0.0369996) |
| [Binomial Tree Betting Scheme](binomial_tree_betting_scheme/) | Replicating a ±\$100 World Series payoff with game-by-game bets | Bet \$31.25 on game 1 |
| [Four Coins on a Spinning Table](spinning_table/) | Match four hidden coins on a table that turns after every move | Flip D A D S D A D: 7 blind moves, the minimum |
| [The Threshold](the_threshold/) | Percolation on an N×N grid: when does a breadth-first flood first reach the bottom? | The chance jumps near p ≈ 0.593; a single page with no Python solver |

The first two problems come from the *Financial Mathematics and Modeling Practicum* (QuIC Financial Technologies, 2003–2010).

The code is pure Python 3 with no dependencies. To run all tests from this folder:

```bash
for d in heat_equation_finite_difference binomial_tree_betting_scheme spinning_table; do python3 -m unittest discover -s $d -t . || break; done
```
