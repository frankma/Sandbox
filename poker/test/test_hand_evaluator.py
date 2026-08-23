from unittest import TestCase

from poker.card import Card, Rank, Suit
from poker.hand_evaluator import HandCategory, HandEvaluator


def cards(*specs) -> list:
    return [Card(Rank[rank], Suit[suit]) for rank, suit in specs]


class TestHandEvaluator(TestCase):
    def test_high_card(self):
        hand = cards(('ACE', 'SPADES'), ('KING', 'HEARTS'), ('NINE', 'CLUBS'),
                     ('FIVE', 'DIAMONDS'), ('TWO', 'SPADES'))
        self.assertEqual(HandEvaluator.evaluate(hand).category, HandCategory.HIGH_CARD)
        pass

    def test_pair(self):
        hand = cards(('ACE', 'SPADES'), ('ACE', 'HEARTS'), ('NINE', 'CLUBS'),
                     ('FIVE', 'DIAMONDS'), ('TWO', 'SPADES'))
        self.assertEqual(HandEvaluator.evaluate(hand).category, HandCategory.PAIR)
        pass

    def test_two_pair(self):
        hand = cards(('ACE', 'SPADES'), ('ACE', 'HEARTS'), ('NINE', 'CLUBS'),
                     ('NINE', 'DIAMONDS'), ('TWO', 'SPADES'))
        self.assertEqual(HandEvaluator.evaluate(hand).category, HandCategory.TWO_PAIR)
        pass

    def test_three_of_a_kind(self):
        hand = cards(('ACE', 'SPADES'), ('ACE', 'HEARTS'), ('ACE', 'CLUBS'),
                     ('FIVE', 'DIAMONDS'), ('TWO', 'SPADES'))
        self.assertEqual(HandEvaluator.evaluate(hand).category, HandCategory.THREE_OF_A_KIND)
        pass

    def test_straight(self):
        hand = cards(('SIX', 'SPADES'), ('FIVE', 'HEARTS'), ('FOUR', 'CLUBS'),
                     ('THREE', 'DIAMONDS'), ('TWO', 'SPADES'))
        rank = HandEvaluator.evaluate(hand)
        self.assertEqual(rank.category, HandCategory.STRAIGHT)
        self.assertEqual(rank.tiebreakers, (6,))
        pass

    def test_wheel_straight_ace_plays_low(self):
        hand = cards(('ACE', 'SPADES'), ('FIVE', 'HEARTS'), ('FOUR', 'CLUBS'),
                     ('THREE', 'DIAMONDS'), ('TWO', 'SPADES'))
        rank = HandEvaluator.evaluate(hand)
        self.assertEqual(rank.category, HandCategory.STRAIGHT)
        self.assertEqual(rank.tiebreakers, (5,))
        pass

    def test_flush(self):
        hand = cards(('ACE', 'SPADES'), ('NINE', 'SPADES'), ('SEVEN', 'SPADES'),
                     ('FIVE', 'SPADES'), ('TWO', 'SPADES'))
        self.assertEqual(HandEvaluator.evaluate(hand).category, HandCategory.FLUSH)
        pass

    def test_full_house(self):
        hand = cards(('ACE', 'SPADES'), ('ACE', 'HEARTS'), ('ACE', 'CLUBS'),
                     ('FIVE', 'DIAMONDS'), ('FIVE', 'SPADES'))
        self.assertEqual(HandEvaluator.evaluate(hand).category, HandCategory.FULL_HOUSE)
        pass

    def test_four_of_a_kind(self):
        hand = cards(('ACE', 'SPADES'), ('ACE', 'HEARTS'), ('ACE', 'CLUBS'),
                     ('ACE', 'DIAMONDS'), ('TWO', 'SPADES'))
        self.assertEqual(HandEvaluator.evaluate(hand).category, HandCategory.FOUR_OF_A_KIND)
        pass

    def test_straight_flush(self):
        hand = cards(('SIX', 'SPADES'), ('FIVE', 'SPADES'), ('FOUR', 'SPADES'),
                     ('THREE', 'SPADES'), ('TWO', 'SPADES'))
        self.assertEqual(HandEvaluator.evaluate(hand).category, HandCategory.STRAIGHT_FLUSH)
        pass

    def test_kicker_breaks_tie_between_pairs(self):
        weaker = cards(('ACE', 'SPADES'), ('ACE', 'HEARTS'), ('NINE', 'CLUBS'),
                        ('FIVE', 'DIAMONDS'), ('TWO', 'SPADES'))
        stronger = cards(('ACE', 'CLUBS'), ('ACE', 'DIAMONDS'), ('KING', 'CLUBS'),
                          ('FIVE', 'HEARTS'), ('TWO', 'HEARTS'))
        self.assertTrue(HandEvaluator.evaluate(stronger) > HandEvaluator.evaluate(weaker))
        pass

    def test_best_five_of_seven_selected(self):
        seven_cards = cards(
            ('ACE', 'SPADES'), ('ACE', 'HEARTS'), ('ACE', 'CLUBS'), ('ACE', 'DIAMONDS'),
            ('KING', 'SPADES'), ('TWO', 'HEARTS'), ('THREE', 'CLUBS'),
        )
        rank = HandEvaluator.evaluate(seven_cards)
        self.assertEqual(rank.category, HandCategory.FOUR_OF_A_KIND)
        self.assertEqual(rank.tiebreakers, (14, 13))
        pass

    def test_evaluate_requires_at_least_five_cards(self):
        self.assertRaises(ValueError, HandEvaluator.evaluate, cards(('ACE', 'SPADES')))
        pass
