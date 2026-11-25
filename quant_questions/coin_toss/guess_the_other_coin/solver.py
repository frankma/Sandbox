"""Coin Toss 1: guess the other coin.

Two players each toss a fair coin, separately and independently. Each sees only
their own coin, then guesses the other player's coin. They win together if at
least one guess is right, and lose if both are wrong. They may agree on a plan
beforehand but cannot communicate after the toss.

A deterministic plan for one player is a function from their own coin to a
guess, so there are four: copy, flip, always heads, always tails. Any random
plan is a mixture of these, so checking the 4 x 4 = 16 pairs is enough.

Winning plan: A guesses B's coin is the SAME as A's; B guesses A's coin is the
OPPOSITE of B's. If the coins match A is right, if they differ B is right, so
exactly one guess is right on every toss.

Run `python3 solver.py` to print the win rate of every pair of plans.
"""
from itertools import product
import random

COIN = ("H", "T")


def _other(c):
    return "T" if c == "H" else "H"


STRATEGIES = {
    "same": lambda own: own,
    "opposite": _other,
    "heads": lambda own: "H",
    "tails": lambda own: "T",
}


def play(strategy_a, strategy_b, coin_a, coin_b):
    """Return (a_right, b_right, win) for one toss."""
    a_right = STRATEGIES[strategy_a](coin_a) == coin_b
    b_right = STRATEGIES[strategy_b](coin_b) == coin_a
    return a_right, b_right, a_right or b_right


def outcomes(strategy_a, strategy_b):
    """All four equally likely tosses, keyed by (coin_a, coin_b)."""
    return {(a, b): play(strategy_a, strategy_b, a, b) for a, b in product(COIN, COIN)}


def win_rate(strategy_a, strategy_b):
    """Exact chance of winning with fair coins."""
    return sum(win for _, _, win in outcomes(strategy_a, strategy_b).values()) / 4


def win_table():
    """Win rate for every pair of deterministic plans."""
    return {(a, b): win_rate(a, b) for a, b in product(STRATEGIES, STRATEGIES)}


def guaranteed():
    """Pairs of plans that win on every toss."""
    return [pair for pair, rate in win_table().items() if rate == 1]


def simulate(strategy_a, strategy_b, n, rng=None):
    """Play n random tosses and return the number of wins."""
    rng = rng or random.Random()
    return sum(play(strategy_a, strategy_b, rng.choice(COIN), rng.choice(COIN))[2] for _ in range(n))


def random_guessing_rate():
    """Both players guess at random: each is right half the time, so 1 - 1/4."""
    return 1 - 0.5 * 0.5


if __name__ == "__main__":
    names = list(STRATEGIES)
    print("Win rate, rows = A's plan, columns = B's plan")
    print(f"{'':>10}" + "".join(f"{n:>10}" for n in names))
    for a in names:
        print(f"{a:>10}" + "".join(f"{win_rate(a, b):>10.0%}" for b in names))
    print()
    print("Guaranteed wins:", ", ".join(f"A {a} / B {b}" for a, b in guaranteed()))
    print(f"Random guessing wins {random_guessing_rate():.0%} of the time.")
    print()
    print("A same / B opposite, every toss:")
    for (ca, cb), (ar, br, win) in outcomes("same", "opposite").items():
        print(f"  A {ca}  B {cb}  A guesses {ca} {'right' if ar else 'wrong'}, "
              f"B guesses {_other(cb)} {'right' if br else 'wrong'}  -> {'win' if win else 'lose'}")
