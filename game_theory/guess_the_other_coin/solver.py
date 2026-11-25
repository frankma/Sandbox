"""Guess the other coin: a two-player team game with hidden coins.

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

The change of view: treat the two coins as one draw from {HH, HT, TH, TT}. Every
guess is then a bet on an event of that draw. "Same as mine" bets on MATCH,
"opposite of mine" bets on NO MATCH. Two bets cover every toss only if they are
complements, and MATCH / NO MATCH is the only event both players can bet on.

As a game, the 4 x 4 win table is a common-payoff game. Its pure Nash
equilibria are the two 100% pairs and four 75% pairs (both name a fixed face),
which is why the plan has to be agreed beforehand.

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


def event(player, strategy):
    """The event a player's guess bets on: the set of (coin_a, coin_b) where it is right."""
    if player == "A":
        return frozenset((a, b) for a, b in product(COIN, COIN) if STRATEGIES[strategy](a) == b)
    return frozenset((a, b) for a, b in product(COIN, COIN) if STRATEGIES[strategy](b) == a)


MATCH = frozenset({("H", "H"), ("T", "T")})
NO_MATCH = frozenset({("H", "T"), ("T", "H")})


def event_name(ev):
    names = {MATCH: "match", NO_MATCH: "no match"}
    if ev in names:
        return names[ev]
    (a, b), _ = sorted(ev)
    side = "A" if all(x[0] == a for x in ev) else "B"
    face = a if side == "A" else b
    return f"{side} {'heads' if face == 'H' else 'tails'}"


def shared_events():
    """Events that both players can bet on."""
    return {event("A", s) for s in STRATEGIES} & {event("B", s) for s in STRATEGIES}


def nash_equilibria():
    """Pure pairs where neither player can raise the shared win rate alone."""
    table = win_table()
    return sorted(
        (a, b) for (a, b), r in table.items()
        if all(table[(x, b)] <= r for x in STRATEGIES) and all(table[(a, y)] <= r for y in STRATEGIES)
    )


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
    print("Events: A same ->", event_name(event("A", "same")), "| B opposite ->", event_name(event("B", "opposite")))
    print("Events both can bet on:", sorted(event_name(e) for e in shared_events()))
    print("Nash equilibria:", ", ".join(f"{a}/{b} ({win_rate(a, b):.0%})" for a, b in nash_equilibria()))
    print()
    print("A same / B opposite, every toss:")
    for (ca, cb), (ar, br, win) in outcomes("same", "opposite").items():
        print(f"  A {ca}  B {cb}  A guesses {ca} {'right' if ar else 'wrong'}, "
              f"B guesses {_other(cb)} {'right' if br else 'wrong'}  -> {'win' if win else 'lose'}")
