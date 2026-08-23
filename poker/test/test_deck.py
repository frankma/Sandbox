import random
from unittest import TestCase

from poker.deck import Deck


class TestDeck(TestCase):
    def setUp(self) -> None:
        self.deck = Deck(rng=random.Random(42))
        pass

    def test_starts_with_52_unique_cards(self):
        self.assertEqual(self.deck.cards_remaining, 52)
        self.assertEqual(len(set(self.deck.cards)), 52)
        pass

    def test_shuffle_is_deterministic_with_seeded_rng(self):
        deck_a = Deck(rng=random.Random(7))
        deck_b = Deck(rng=random.Random(7))
        deck_a.shuffle()
        deck_b.shuffle()
        self.assertEqual(deck_a.cards, deck_b.cards)
        pass

    def test_draw_reduces_remaining_and_returns_requested_count(self):
        drawn = self.deck.draw(3)
        self.assertEqual(len(drawn), 3)
        self.assertEqual(self.deck.cards_remaining, 49)
        pass

    def test_burn_draws_a_single_card(self):
        before = self.deck.cards_remaining
        self.deck.burn()
        self.assertEqual(self.deck.cards_remaining, before - 1)
        pass

    def test_draw_more_than_remaining_raises(self):
        self.assertRaises(ValueError, self.deck.draw, 53)
        pass
