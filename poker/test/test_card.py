from unittest import TestCase

from poker.card import Card, Rank, Suit


class TestCard(TestCase):
    def setUp(self) -> None:
        self.ace_spades = Card(Rank.ACE, Suit.SPADES)
        self.ace_spades_dup = Card(Rank.ACE, Suit.SPADES)
        self.king_hearts = Card(Rank.KING, Suit.HEARTS)
        pass

    def test_equality(self):
        self.assertEqual(self.ace_spades, self.ace_spades_dup)
        self.assertNotEqual(self.ace_spades, self.king_hearts)
        pass

    def test_hashable(self):
        cards = {self.ace_spades, self.ace_spades_dup, self.king_hearts}
        self.assertEqual(len(cards), 2)
        pass

    def test_ordering(self):
        self.assertTrue(self.king_hearts < self.ace_spades)
        pass

    def test_str(self):
        self.assertEqual(str(self.ace_spades), 'AS')
        self.assertEqual(str(self.king_hearts), 'KH')
        pass
