# Guess the Other Coin

## Problem

Two players each toss a fair coin, separately and independently. Each sees only their own coin, then guesses the other player's coin. They win together if **at least one** guess is right, and lose if both are wrong. They may agree a plan beforehand but cannot communicate after the toss. Find a strategy that is guaranteed to win.

## Answer

- **A** guesses that B's coin is the **same** as A's.
- **B** guesses that A's coin is the **opposite** of B's.

If the coins match, A is right; if they differ, B is right. Exactly one guess is right on every toss.

| A | B | A guesses | B guesses | Right |
|---|---|---|---|---|
| H | H | H | T | A |
| H | T | H | H | B |
| T | H | T | T | B |
| T | T | T | H | A |

## The change of view

Stop looking at the coins one at a time. Together they are one draw from {HH, HT, TH, TT}, each with chance ¼, and every guess is a bet on an event of that draw:

| Plan | As A's guess, it bets on | As B's guess, it bets on |
|---|---|---|
| same as mine | **Match** {HH, TT} | **Match** |
| opposite of mine | **No match** {HT, TH} | **No match** |
| always heads | B has heads | A has heads |
| always tails | B has tails | A has tails |

Two bets cover every toss only if they are complements. Match / No match is the only event on both lists, so the only sure win is to split it: one player bets the coins match, the other bets they don't. It is a perfect hedge: neither bet beats 50%, but their payoffs are perfectly negatively correlated.

## Why

A player's guess can depend only on their own coin, so each has four plans: same, opposite, always heads, always tails. Random plans are mixtures of these and cannot beat the best of them.

Whatever the plan, each guess concerns a coin the guesser never sees and that is independent of their own, so each player is right in exactly 2 of the 4 equally likely tosses. That is 4 right guesses spread over 4 tosses. Winning every toss needs at least one right guess per toss, so there must be exactly one per toss: the two players' hits must never overlap. "Same" covers {HH, TT} and "opposite" covers {HT, TH}, a perfect split.

Win rate for every pair (rows A, columns B):

|  | same | opposite | heads | tails |
|---|---|---|---|---|
| **same** | 50% | **100%** | 75% | 75% |
| **opposite** | **100%** | 50% | 75% | 75% |
| **heads** | 75% | 75% | 75% | 75% |
| **tails** | 75% | 75% | 75% | 75% |

Random guessing wins 75%. Both saying "same" wins only 50%, because their right guesses always land on the same tosses.

### As a strategy game

The players share one payoff, so the table is a team game with hidden information. Six pairs are pure Nash equilibria (neither player gains by switching alone): the two 100% pairs, and the four where both always name a fixed face, which win 75%. Stability isn't enough; the team has to agree on the hedge beforehand.

## Files

| File | Contents |
|---|---|
| [`solver.py`](solver.py) | Plans, scoring, guesses as events, the 4 × 4 win table, Nash equilibria and a simulator. `python3 solver.py` prints the analysis. |
| [`test/test_solver.py`](test/test_solver.py) | Unit tests. From `game_theory/`, run `python3 -m unittest discover -s guess_the_other_coin -t .` |
| [`index.html`](index.html) | Interactive page: a five-step change of view from two coins to one event, toss the coins with any pair of plans, see all four tosses checked, and compare all 16 plan pairs. |
