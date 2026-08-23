import random
from unittest import TestCase

from poker.card import Card, Rank, Suit
from poker.player import Action, MachinePlayer, Player
from poker.strategy import MonteCarloStrategy
from poker.table import Table


class TestMonteCarloStrategyEquity(TestCase):
    def test_equity_is_deterministic_with_seeded_rng(self):
        strategy_a = MonteCarloStrategy(num_simulations=200, rng=random.Random(3))
        strategy_b = MonteCarloStrategy(num_simulations=200, rng=random.Random(3))
        hole = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)]
        equity_a = strategy_a.estimate_equity(hole, [], num_opponents=1)
        equity_b = strategy_b.estimate_equity(hole, [], num_opponents=1)
        self.assertEqual(equity_a, equity_b)
        pass

    def test_pocket_aces_have_high_preflop_equity_heads_up(self):
        strategy = MonteCarloStrategy(num_simulations=500, rng=random.Random(11))
        hole = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)]
        equity = strategy.estimate_equity(hole, [], num_opponents=1)
        self.assertGreater(equity, 0.7)
        pass

    def test_uncontested_pot_has_full_equity(self):
        strategy = MonteCarloStrategy(num_simulations=50, rng=random.Random(2))
        hole = [Card(Rank.TWO, Suit.SPADES), Card(Rank.SEVEN, Suit.HEARTS)]
        equity = strategy.estimate_equity(hole, [], num_opponents=0)
        self.assertEqual(equity, 1.0)
        pass


class TestMonteCarloStrategyDecide(TestCase):
    def setUp(self) -> None:
        self.strategy = MonteCarloStrategy(num_simulations=200, rng=random.Random(5))
        self.machine = MachinePlayer('M', 100, self.strategy)
        self.table = Table([Player('A', 100), self.machine], small_blind=1, big_blind=2,
                            rng=random.Random(5))
        self.table.start_hand()
        pass

    def test_strong_hand_facing_no_bet_bets_or_checks(self):
        self.machine.hole_cards = [Card(Rank.ACE, Suit.SPADES), Card(Rank.ACE, Suit.HEARTS)]
        self.table.current_bet = 0
        self.machine.current_bet = 0
        action, amount = self.strategy.decide(self.machine, self.table)
        self.assertIn(action, (Action.BET, Action.CHECK))
        pass

    def test_weak_hand_facing_large_bet_folds(self):
        self.machine.hole_cards = [Card(Rank.TWO, Suit.CLUBS), Card(Rank.SEVEN, Suit.DIAMONDS)]
        self.table.community_cards = [
            Card(Rank.ACE, Suit.SPADES), Card(Rank.KING, Suit.HEARTS),
            Card(Rank.QUEEN, Suit.CLUBS), Card(Rank.JACK, Suit.SPADES),
        ]
        self.table.pot = 10
        self.table.current_bet = 100
        self.machine.current_bet = 0
        self.machine.stack = 100
        action, amount = self.strategy.decide(self.machine, self.table)
        self.assertEqual(action, Action.FOLD)
        pass
