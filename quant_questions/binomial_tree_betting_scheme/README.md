# Binomial Tree Betting Scheme

*Source: Financial Mathematics and Modeling Practicum (QuIC Financial Technologies, 2003–2010). The problem is restated here, not quoted.*

## Problem

Your team plays your uncle's team in the World Series, where the first side to win four games wins. Before every game you choose a stake $b$:

- If your team wins the game, your uncle owes you $b$ (an IOU).
- If your team loses, you owe him $b$.

All IOUs are settled in cash once the series ends. You want to finish **up \$100 if your team wins the series** and **down \$100 if it loses**.

**How much should you bet on the first game?**

## Solution

### Answer

**Bet \$31.25 on the opening game.**

### Idea: replicate the payoff on a binomial tree

This is option replication with even-money bets as the hedging instrument. Label each state by your team's record $(w, l)$. Let $V(w, l)$ be the IOU balance you must hold on reaching that state so that the right bets from there on finish exactly at the target:

$$
V(4, l) = +100, \qquad V(w, 4) = -100.
$$

At a live state you bet $b$. A win moves you to $(w+1, l)$ with balance $V + b$, and a loss moves you to $(w, l+1)$ with balance $V - b$. Matching both branches gives

$$
V(w,l) = \frac{V(w+1,l) + V(w,l+1)}{2}, \qquad
b(w,l) = \frac{V(w+1,l) - V(w,l+1)}{2}.
$$

Each value is the plain average of its two successors, the risk-neutral measure with $p = \tfrac12$. The bets are fair, so the replicating "price" doesn't depend on how likely your team really is to win. Only the payoff and the structure of the tree matter.

### Backward induction

| state | value $V$ | bet $b$ |
|---|---|---|
| 3–3 | 0 | 100 |
| 3–2 / 2–3 | ±50 | 50 |
| 3–1 / 1–3 | ±75 | 25 |
| 2–2 | 0 | 50 |
| 3–0 / 0–3 | ±87.5 | 12.5 |
| 2–1 / 1–2 | ±37.5 | 37.5 |
| 2–0 / 0–2 | ±62.5 | 25 |
| 1–1 | 0 | 37.5 |
| 1–0 / 0–1 | ±31.25 | 31.25 |
| **0–0** | **0** | **31.25** |

### Closed form

Since $V$ is a martingale with $p = \tfrac12$,

$$
V(w,l) = 100\,\bigl(2\,P_{1/2}[\text{win series} \mid w, l] - 1\bigr).
$$

From 1–0 your team needs 3 more wins before 4 losses:

$$
P = \sum_{j=0}^{3}\binom{2+j}{j}\Bigl(\tfrac12\Bigr)^{3+j} = \tfrac{21}{32}.
$$

So $V(1,0) = 100\,(42/32 - 1) = 31.25$, and the opening bet is $b(0,0) = \bigl(V(1,0) - V(0,1)\bigr)/2 = 31.25$.

The same argument gives the general opening bet for a best-of-$(2n-1)$ series with payoff $X$:

$$
b(0,0) = X\binom{2n-2}{n-1}\Bigl(\tfrac12\Bigr)^{2n-1}.
$$

This is $X$ times the probability that a fair series reaches the deciding game. For $n = 4$: $100 \cdot 20/64 = 31.25$.

### Verification

[`test/test_solver.py`](test/test_solver.py) checks:

- The opening bet is 31.25.
- Playing out all $2^7$ win/loss sequences with the recursive bets ends at exactly $+100$ or $-100$, matching who won the series.
- The tree is antisymmetric: $V(w,l) = -V(l,w)$ and $b(w,l) = b(l,w)$.
- $V(1,0)$ matches the closed form with $P = 21/32$.
- At 3–3 the bet is the full \$100.
- Results scale correctly with the payoff and series length (best-of-1 → \$100, best-of-3 → \$50).

## Files

| File | Contents |
|---|---|
| [`solver.py`](solver.py) | Backward induction, betting tree and path simulator. `python3 solver.py` prints the tree. |
| [`test/test_solver.py`](test/test_solver.py) | Unit tests. From `quant_questions/`, run `python3 -m unittest discover -s binomial_tree_betting_scheme -t .` |
| [`index.html`](index.html) | Stand-alone interactive tree. Open it in a browser. |
