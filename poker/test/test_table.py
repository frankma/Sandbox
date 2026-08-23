import random
from unittest import TestCase

from poker.player import Action, Player
from poker.table import BettingRound, Table


class TestTableDealing(TestCase):
    def setUp(self) -> None:
        self.players = [Player('A', 100), Player('B', 100), Player('C', 100)]
        self.table = Table(self.players, small_blind=1, big_blind=2, rng=random.Random(1))
        self.table.start_hand()
        pass

    def test_deal_hole_cards_gives_two_cards_each_no_duplicates(self):
        self.table.deal_hole_cards()
        all_dealt = []
        for player in self.players:
            self.assertEqual(len(player.hole_cards), 2)
            all_dealt.extend(player.hole_cards)
        self.assertEqual(len(set(all_dealt)), 6)
        pass

    def test_deal_flop_turn_river_sequence(self):
        self.table.deal_hole_cards()
        self.table.deal_flop()
        self.assertEqual(len(self.table.community_cards), 3)
        self.assertEqual(self.table.current_round, BettingRound.FLOP)
        self.table.deal_turn()
        self.assertEqual(len(self.table.community_cards), 4)
        self.assertEqual(self.table.current_round, BettingRound.TURN)
        self.table.deal_river()
        self.assertEqual(len(self.table.community_cards), 5)
        self.assertEqual(self.table.current_round, BettingRound.RIVER)
        pass

    def test_dealing_consumes_deck_including_burns(self):
        self.table.deal_hole_cards()
        self.table.deal_flop()
        self.table.deal_turn()
        self.table.deal_river()
        # 52 - 6 hole cards - (1 burn + 3 flop) - (1 burn + 1 turn) - (1 burn + 1 river)
        self.assertEqual(self.table.deck.cards_remaining, 52 - 6 - 4 - 2 - 2)
        pass

    def test_known_cards_hides_opponent_hole_cards_before_showdown(self):
        self.table.deal_hole_cards()
        self.table.deal_flop()
        viewer, opponent = self.players[0], self.players[1]
        known = self.table.known_cards_for(viewer)
        self.assertEqual(set(known), set(self.table.community_cards) | set(viewer.hole_cards))
        for card in opponent.hole_cards:
            self.assertNotIn(card, known)
        pass

    def test_known_cards_reveals_non_folded_opponents_at_showdown(self):
        self.table.deal_hole_cards()
        self.table.current_round = BettingRound.SHOWDOWN
        viewer, opponent, folded = self.players[0], self.players[1], self.players[2]
        folded.folded = True
        known = self.table.known_cards_for(viewer)
        for card in opponent.hole_cards:
            self.assertIn(card, known)
        for card in folded.hole_cards:
            self.assertNotIn(card, known)
        pass


class TestTableBetting(TestCase):
    def setUp(self) -> None:
        self.players = [Player('A', 100), Player('B', 100), Player('C', 100)]
        self.table = Table(self.players, small_blind=1, big_blind=2, rng=random.Random(1))
        self.table.start_hand()
        self.table.post_blinds()
        pass

    def test_post_blinds_charges_small_and_big_blind(self):
        # button=0 -> small blind is players[1], big blind is players[2]
        self.assertEqual(self.players[1].current_bet, 1)
        self.assertEqual(self.players[2].current_bet, 2)
        self.assertEqual(self.table.pot, 3)
        self.assertEqual(self.table.current_bet, 2)
        pass

    def test_fold_removes_player_from_active(self):
        self.table.start_betting_round()
        actor = self.table.current_actor()
        self.table.apply_action(actor, Action.FOLD)
        self.assertTrue(actor.folded)
        self.assertNotIn(actor, self.table.active_players())
        pass

    def test_raise_reopens_action_for_other_players(self):
        self.table.start_betting_round()
        first = self.table.current_actor()
        self.table.apply_action(first, Action.CALL)
        second = self.table.current_actor()
        self.table.apply_action(second, Action.RAISE, 5)
        self.assertFalse(self.table.is_betting_round_complete())
        third = self.table.current_actor()
        self.table.apply_action(third, Action.CALL)
        self.assertFalse(self.table.is_betting_round_complete())
        self.table.apply_action(first, Action.CALL)
        self.assertTrue(self.table.is_betting_round_complete())
        pass

    def test_betting_round_complete_when_one_player_remains(self):
        self.table.start_betting_round()
        first = self.table.current_actor()
        self.table.apply_action(first, Action.FOLD)
        second = self.table.current_actor()
        self.table.apply_action(second, Action.FOLD)
        self.assertTrue(self.table.is_betting_round_complete())
        pass

    def test_turn_order_skips_folded_and_all_in_players(self):
        self.table.start_betting_round()
        first = self.table.current_actor()
        self.table.apply_action(first, Action.FOLD)
        second = self.table.current_actor()
        self.assertNotEqual(second, first)
        self.assertFalse(second.folded)
        pass
