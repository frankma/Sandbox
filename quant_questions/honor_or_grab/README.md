# Honor or Grab

An $n$-team repeated social dilemma with per-rival decisions and random bonus rounds.

## Rules

Each round, every team decides **separately for each other team** whether to **honor** or **grab** that deal. A round is therefore an $n \times n$ decision matrix $D$, where $D_{ij}$ is team $i$'s decision toward team $j$ (the diagonal is unused). Each pair settles its deal from $D_{ij}$ and $D_{ji}$:

| Deal | Scores |
|---|---|
| both honor | +6 / +6 |
| one grabs, one honors | grabber +14, honorer −6 |
| both grab | −4 / −4 |

A team's round score is the sum over its $n-1$ deals. A unanimous matrix replaces the sums:

- **every decision is grab:** −12 each
- **every decision is honor:** +15 each

The game runs $m$ rounds (default 5) with $n$ teams (default 4). Each round is independently a **bonus round** with probability $q$ (default 0.25), announced before teams decide. In a bonus round every score is multiplied by $x$ (default 3).

Example round ($n = 4$). Team A grabs C, team C grabs everyone, everyone else honors:

|  | → A | → B | → C | → D | score |
|---|---|---|---|---|---|
| **A** | · | H +6 | G −4 | H +6 | +8 |
| **B** | H +6 | · | H −6 | H +6 | +6 |
| **C** | G −4 | G +14 | · | G +14 | +24 |
| **D** | H +6 | H +6 | H −6 | · | +6 |

## Analysis

### One round: grab dominates (for $n \ge 4$)

Each deal on its own is a prisoner's dilemma: grabbing pays 14 instead of 6 against an honorer, and −4 instead of −6 against a grabber. The −12 and +15 rules only bite when the whole matrix agrees, which leaves two small-game exceptions:

| teams | one-round game |
|---|---|
| 2 | **Honor dominates** (15 > 14 and −6 > −12), so there is no dilemma |
| 3 | No dominant move: against two total grabbers, honoring exactly one of them (−10) beats −12 |
| 4+ | Grabbing every deal strictly dominates; the equilibrium is everyone on −12 instead of +15 |

Your one-round score with $n = 4$ when $k$ rivals honor you (the rivals honor each other):

| rivals honoring you $k$ | you honor everyone | you grab everyone |
|---|---|---|
| 0 | −18 | −12 |
| 1 | −6 | 6 |
| 2 | 6 | 24 |
| 3 | 15 | 42 |

### A known number of rounds: unravelling

Everyone grabs in the last round, so the second-to-last is effectively the last, and so on. With a fixed, known $m$, the only equilibrium is to grab every deal, every round.

### An uncertain end: the shadow of the future

Suppose the game continues after each round with probability $\delta$, and a rival you grab grabs you back for good, while the others keep honoring you. Starting from full cooperation, grabbing $k$ rivals:

- gains $D_k = 14k + 6(n-1-k) - 15$ this round,
- costs $P_k = 15 - \bigl(-4k + 6(n-1-k)\bigr)$ every later round.

With $E = 1 + q(x-1) = 1.5$ the expected future multiplier and $M$ this round's multiplier, honoring is stable when

$$
\delta \ge \max_k \frac{M D_k}{M D_k + E P_k}.
$$

For $n = 4$: grabbing one rival gives $D_1 = 11$ and $P_1 = 7$, the worst case. It is more tempting than grabbing everyone ($D_3 = P_3 = 27$), because it breaks the +15 rule without provoking the whole table. The thresholds are $\delta \ge 0.51$ in a normal round and $\delta \ge 0.76$ in a bonus round.

### Strategy tournament

Each strategy decides toward every rival separately. Eight strategies play every line-up of four teams (330 groups) with random bonus rounds. Average total per game:

| strategy | 5 rounds | 20 rounds |
|---|---|---|
| Endgame defector (tit-for-tat, grab all in the last round) | **84.8** | 298.5 |
| Grim trigger | 72.3 | **300.8** |
| Tit-for-tat | 69.8 | 286.1 |
| Bonus grabber (tit-for-tat, grab all on bonus rounds) | 68.4 | 69.4 |
| Pavlov | 67.8 | 285.9 |
| Always honor | 61.4 | 262.7 |
| Coin flip | 51.3 | 137.5 |
| Always grab | 36.4 | 30.5 |

Per-rival decisions let reciprocal strategies keep cooperating with each other while isolating grabbers. Always-grab finishes last even in a 5-round game.

### What to play

1. **One-off round, or a round you know is the last:** grab.
2. **Treat each rival separately.** Honor the teams that honor you and grab back at the one that grabbed you.
3. **The real temptation is grabbing one rival.** Expect it, especially on bonus rounds, where cooperation needs $\delta \ge 0.76$.
4. **Grab everyone in the final round.** No one can punish you afterwards.
5. **Never grab everyone, every round.** Reciprocators all turn on you, and you finish last.

## Files

| File | Contents |
|---|---|
| [`solver.py`](solver.py) | Rules, decision-matrix scoring, strategies, game engine, cooperation threshold and tournament. `python3 solver.py` prints the analysis. |
| [`test/test_solver.py`](test/test_solver.py) | Unit tests. From `quant_questions/`, run `python3 -m unittest discover -s honor_or_grab -t .` |
| [`index.html`](index.html) | Interactive page: play against strategy bots with a live decision matrix, adjustable rules, a tournament and evolution. |
