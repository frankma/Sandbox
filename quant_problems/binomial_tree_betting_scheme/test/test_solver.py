from itertools import product
from unittest import TestCase

from binomial_tree_betting_scheme.solver import bet, betting_tree, simulate, value


class TestBettingScheme(TestCase):
    def test_opening_bet(self):
        self.assertAlmostEqual(bet(0, 0), 31.25)

    def test_every_series_path_hits_target(self):
        # Enumerate all 2^7 result sequences; the series ends after at most 7 games.
        for outcomes in product("WL", repeat=7):
            wins = losses = 0
            for r in outcomes:
                if wins == 4 or losses == 4:
                    break
                wins += r == "W"
                losses += r == "L"
            expected = 100.0 if wins == 4 else -100.0
            self.assertAlmostEqual(simulate(outcomes), expected, places=10)

    def test_value_is_antisymmetric(self):
        for (w, l), (v, b) in betting_tree().items():
            self.assertAlmostEqual(v, -value(l, w))
            self.assertAlmostEqual(b, bet(l, w))

    def test_value_equals_fair_odds_expectation(self):
        # V(w, l) = 100 * (2 P(win series | fair coin) - 1); at 1-0 that P is 21/32.
        self.assertAlmostEqual(value(1, 0), 100 * (2 * 21 / 32 - 1))

    def test_game_seven_bets_everything(self):
        self.assertAlmostEqual(bet(3, 3), 100.0)

    def test_scales_with_payoff_and_series_length(self):
        self.assertAlmostEqual(bet(0, 0, payoff=200.0), 62.5)
        self.assertAlmostEqual(bet(0, 0, wins_needed=1), 100.0)
        self.assertAlmostEqual(bet(0, 0, wins_needed=2), 50.0)
