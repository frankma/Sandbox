from collections import Counter
from itertools import product
import random
from unittest import TestCase

from rotating_table.solver import (
    MOVES, PLAN, START, STATES, min_moves, orbit, play, rotate, run, shape, shapes, shortest_plan, step, won,
    worst_case,
)


def after(move, state):
    """Shapes a single state can become after `move` (before the rotation)."""
    return {shape(state ^ MOVES[move])} | {shape(rotate(state, k) ^ MOVES[move]) for k in range(4)}


class TestRotatingTable(TestCase):
    def test_plan_always_wins(self):
        self.assertEqual(run(START, PLAN)[-1], frozenset())

    def test_worst_case_is_seven(self):
        self.assertEqual(worst_case(), 7)

    def test_seven_is_minimal(self):
        # BFS over all 15 flip masks, not just D/A/S.
        self.assertEqual(min_moves(), 7)
        self.assertEqual(len(shortest_plan()), 7)

    def test_unique_among_three_moves(self):
        ok = ["".join(p) for p in product("DAS", repeat=7) if not run(START, p)[-1]]
        self.assertEqual(ok, ["DADSDAD"])

    def test_no_six_move_plan_of_three_moves(self):
        self.assertFalse(any(not run(START, p)[-1] for p in product("DAS", repeat=6)))

    def test_belief_trace(self):
        expect = [["ONE", "ADJACENT", "DIAGONAL"], ["ONE", "ADJACENT"], ["ONE", "DIAGONAL"], ["ONE"],
                  ["ADJACENT", "DIAGONAL"], ["ADJACENT"], ["DIAGONAL"], []]
        self.assertEqual([shapes(b) for b in run(START, PLAN)], expect)

    def test_shape_transitions(self):
        one, adj, diag = 0b0001, 0b0011, 0b0101
        self.assertEqual(after("D", diag), {"WON"})
        self.assertEqual(after("D", adj), {"ADJACENT"})
        self.assertEqual(after("D", one), {"ONE"})
        self.assertEqual(after("A", adj), {"WON", "DIAGONAL"})
        self.assertEqual(after("A", diag), {"ADJACENT"})
        self.assertEqual(after("S", one), {"WON", "ADJACENT", "DIAGONAL"})
        self.assertEqual(after("S", adj), {"ONE"})

    def test_rotation_and_shapes(self):
        self.assertEqual(rotate(0b0001, 1), 0b0010)
        self.assertEqual(rotate(0b1000, 1), 0b0001)
        self.assertEqual(orbit(0b0101), {0b0101, 0b1010})
        self.assertEqual(Counter(shape(s) for s in STATES), {"WON": 2, "ONE": 8, "ADJACENT": 4, "DIAGONAL": 2})
        self.assertTrue(won(0) and won(15))

    def test_moves_used_are_uniform(self):
        # Over every start and rotation sequence, 0..7 moves each happen 1/8 of the time.
        c = Counter(play(s, PLAN, r) for s in STATES for r in product(range(4), repeat=7))
        self.assertEqual(set(c), set(range(8)))
        self.assertEqual(len(set(c.values())), 1)

    def test_random_games(self):
        rng = random.Random(3)
        for _ in range(2000):
            self.assertIsNotNone(play(rng.randrange(16), PLAN, rng=rng))

    def test_step_drops_wins(self):
        self.assertEqual(step(frozenset({0b0101}), MOVES["D"]), frozenset())
