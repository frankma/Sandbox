"""Replicating bets for a best-of-7 series on a binomial tree.

State (w, l) = games won / lost by your team so far. At the end of the series the
target cash position is +payoff if your team won four games, -payoff otherwise.
Each bet is even money, so whatever the true win probability, the position value is
the plain average of its two successors, and the bet that hedges game (w, l) is half
the spread between them:

    V(w, l) = (V(w+1, l) + V(w, l+1)) / 2
    b(w, l) = (V(w+1, l) - V(w, l+1)) / 2

Run `python3 solver.py` to print the opening bet and the full betting tree.
"""
from functools import lru_cache

WINS_NEEDED = 4
PAYOFF = 100.0


@lru_cache(maxsize=None)
def value(w, l, wins_needed=WINS_NEEDED, payoff=PAYOFF):
    """IOU balance you must already hold at state (w, l) to finish on +/- payoff."""
    if w == wins_needed:
        return payoff
    if l == wins_needed:
        return -payoff
    return 0.5 * (value(w + 1, l, wins_needed, payoff) + value(w, l + 1, wins_needed, payoff))


def bet(w, l, wins_needed=WINS_NEEDED, payoff=PAYOFF):
    """Stake to place on your team before the game played at state (w, l)."""
    return 0.5 * (value(w + 1, l, wins_needed, payoff) - value(w, l + 1, wins_needed, payoff))


def betting_tree(wins_needed=WINS_NEEDED, payoff=PAYOFF):
    """All live states with their value and bet, keyed by (w, l)."""
    return {
        (w, l): (value(w, l, wins_needed, payoff), bet(w, l, wins_needed, payoff))
        for w in range(wins_needed)
        for l in range(wins_needed)
    }


def simulate(outcomes, wins_needed=WINS_NEEDED, payoff=PAYOFF):
    """Play a sequence of results ('W'/'L') and return the cash balance at the end."""
    w = l = 0
    balance = 0.0
    for result in outcomes:
        if w == wins_needed or l == wins_needed:
            break
        b = bet(w, l, wins_needed, payoff)
        if result == "W":
            balance += b
            w += 1
        else:
            balance -= b
            l += 1
    return balance


if __name__ == "__main__":
    print(f"Opening bet: ${bet(0, 0):.4f}\n")
    print("state (W-L)   value       bet")
    for (w, l), (v, b) in sorted(betting_tree().items(), key=lambda kv: (sum(kv[0]), -kv[0][0])):
        print(f"   {w}-{l}     {v:9.4f}  {b:9.4f}")
