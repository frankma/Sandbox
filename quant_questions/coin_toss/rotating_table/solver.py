"""Coin Toss 2: four coins on a rotating table.

Four coins sit at the corners of a square on a round table, each heads or tails
at random. You can't see them. Each turn you name some seats (relative to you)
and those coins are flipped. If all four coins then show the same face, you win
and the game stops. Otherwise the table is turned by an unknown multiple of a
quarter turn and you go again. Find a sequence of instructions that always wins.

Coins are bits (1 = heads) in seat order 0, 1, 2, 3 around the table, so a state
is a 4-bit number and a move is a non-empty mask of seats to flip.

Because you can't see anything, a plan is a fixed list of moves. Track the set
of states still possible (the belief): flip each by the move, drop the ones that
win, then close under rotation. A plan always wins when the belief becomes empty.
Breadth-first search over beliefs finds the shortest plan and proves nothing
shorter works.

Up to rotation and swapping heads with tails, a losing table is one of three
shapes, and only three moves matter:

    shapes: ONE (3-1 split), ADJACENT (HHTT), DIAGONAL (HTHT)
    moves:  D = flip two opposite coins, A = flip two neighbours, S = flip one

Run `python3 solver.py` to print the plan and a step-by-step trace.
"""
from collections import deque
from itertools import product
import random

N = 4
FULL = (1 << N) - 1
STATES = range(1 << N)
MOVES = {"D": 0b0101, "A": 0b0011, "S": 0b0001}
PLAN = ["D", "A", "D", "S", "D", "A", "D"]


def rotate(state, k):
    k %= N
    return ((state << k) | (state >> (N - k))) & FULL


def won(state):
    return state in (0, FULL)


def orbit(state):
    return {rotate(state, k) for k in range(N)}


def shape(state):
    """Name the state's class up to rotation and heads/tails swap."""
    if won(state):
        return "WON"
    ones = bin(state).count("1")
    if ones in (1, 3):
        return "ONE"
    return "DIAGONAL" if state in (0b0101, 0b1010) else "ADJACENT"


START = frozenset(s for s in STATES if not won(s))


def step(belief, mask):
    """Belief after flipping `mask`, removing wins, then an unknown rotation."""
    out = set()
    for s in belief:
        t = s ^ mask
        if not won(t):
            out |= orbit(t)
    return frozenset(out)


def run(belief, plan):
    """Beliefs after each move of `plan` (move names or masks)."""
    trace = [belief]
    for m in plan:
        trace.append(step(trace[-1], MOVES.get(m, m)))
    return trace


def shortest_plan(masks=range(1, 1 << N)):
    """BFS over beliefs: the shortest list of masks that always wins."""
    seen = {START: None}
    queue = deque([START])
    while queue:
        b = queue.popleft()
        for m in masks:
            nb = step(b, m)
            if nb in seen:
                continue
            seen[nb] = (b, m)
            if not nb:
                plan = []
                while seen[nb]:
                    nb, m = seen[nb]
                    plan.append(m)
                return plan[::-1]
            queue.append(nb)
    return None


def min_moves():
    return len(shortest_plan())


def play(start, plan=PLAN, rotations=None, rng=None):
    """Play one game. Returns the number of moves used to win, 0 if the start
    is already won, or None if the plan runs out. `rotations` fixes the table
    turns; otherwise they are random."""
    rng = rng or random.Random()
    state = start
    if won(state):
        return 0
    for i, m in enumerate(plan):
        state ^= MOVES.get(m, m)
        if won(state):
            return i + 1
        k = rotations[i] if rotations is not None else rng.randrange(N)
        state = rotate(state, k)
    return None


def worst_case(plan=PLAN):
    """Most moves the plan needs over every start and every run of rotations."""
    worst = 0
    for start in STATES:
        for rots in product(range(N), repeat=len(plan)):
            used = play(start, plan, rots)
            if used is None:
                return None
            worst = max(worst, used)
    return worst


def shapes(belief):
    return sorted({shape(s) for s in belief}, key=["ONE", "ADJACENT", "DIAGONAL"].index)


if __name__ == "__main__":
    print("Plan:", " ".join(PLAN), "(D = two opposite, A = two neighbours, S = one coin)")
    for i, b in enumerate(run(START, PLAN)):
        label = "start" if i == 0 else f"after {i} {PLAN[i - 1]}"
        print(f"  {label:<11} still possible: {', '.join(shapes(b)) or 'nothing: always won'}")
    print("Worst case over every start and every rotation:", worst_case(), "moves")
    print("Shortest plan found by search:", min_moves(), "moves")
