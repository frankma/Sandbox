import random
from unittest import TestCase

from poker.odds_advisor import OddsAdvisor
from poker.player import Player
from poker.table import BettingRound, Table


class TestOddsAdvisor(TestCase):
    def setUp(self) -> None:
        self.players = [Player('A', 100), Player('B', 100), Player('C', 100)]
        self.table = Table(self.players, small_blind=1, big_blind=2, rng=random.Random(9))
        self.table.start_hand()
        self.table.deal_hole_cards()
        self.table.deal_flop()
        self.human = self.players[0]
        self.advisor = OddsAdvisor(self.table, self.human)
        pass

    def test_known_cards_never_include_hidden_opponent_hole_cards(self):
        known = self.advisor.known_cards()
        for opponent in self.players[1:]:
            for card in opponent.hole_cards:
                self.assertNotIn(card, known)
        pass

    def test_known_cards_include_own_hole_and_community_cards(self):
        known = self.advisor.known_cards()
        for card in self.human.hole_cards:
            self.assertIn(card, known)
        for card in self.table.community_cards:
            self.assertIn(card, known)
        pass

    def test_known_cards_reveal_opponents_at_showdown(self):
        self.table.current_round = BettingRound.SHOWDOWN
        known = self.advisor.known_cards()
        for card in self.players[1].hole_cards:
            self.assertIn(card, known)
        pass

    def test_estimate_equity_returns_a_probability(self):
        equity = self.advisor.estimate_equity(num_simulations=100, rng=random.Random(4))
        self.assertGreaterEqual(equity, 0.0)
        self.assertLessEqual(equity, 1.0)
        pass

    def test_estimate_equity_is_deterministic_with_seeded_rng(self):
        equity_a = self.advisor.estimate_equity(num_simulations=100, rng=random.Random(4))
        equity_b = self.advisor.estimate_equity(num_simulations=100, rng=random.Random(4))
        self.assertEqual(equity_a, equity_b)
        pass
