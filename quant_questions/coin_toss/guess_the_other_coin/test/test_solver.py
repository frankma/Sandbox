from itertools import product
import random
from unittest import TestCase

from guess_the_other_coin.solver import (
    COIN, STRATEGIES, guaranteed, outcomes, play, random_guessing_rate, simulate, win_rate, win_table,
)


class TestGuessTheOtherCoin(TestCase):
    def test_same_opposite_wins_every_toss(self):
        for coin_a, coin_b in product(COIN, COIN):
            self.assertTrue(play("same", "opposite", coin_a, coin_b)[2])

    def test_exactly_one_guess_right(self):
        for a_right, b_right, _ in outcomes("same", "opposite").values():
            self.assertEqual(a_right + b_right, 1)

    def test_only_two_guaranteed_pairs(self):
        self.assertEqual(sorted(guaranteed()), [("opposite", "same"), ("same", "opposite")])

    def test_each_guess_right_half_the_time(self):
        # B's coin is independent of A's, so any plan of A's is right in 2 of 4 tosses.
        for a, b in product(STRATEGIES, STRATEGIES):
            res = outcomes(a, b).values()
            self.assertEqual(sum(r[0] for r in res), 2)
            self.assertEqual(sum(r[1] for r in res), 2)

    def test_win_rates(self):
        self.assertEqual(win_rate("same", "same"), 0.5)
        self.assertEqual(win_rate("heads", "heads"), 0.75)
        self.assertEqual(min(win_table().values()), 0.5)

    def test_random_guessing(self):
        self.assertEqual(random_guessing_rate(), 0.75)

    def test_simulation(self):
        self.assertEqual(simulate("same", "opposite", 1000, random.Random(1)), 1000)
        wins = simulate("same", "same", 20000, random.Random(2))
        self.assertAlmostEqual(wins / 20000, 0.5, delta=0.02)
