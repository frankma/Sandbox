import random
from unittest import TestCase
from unittest.mock import patch

from poker.player import Action, HumanPlayer, MachinePlayer, Player
from poker.strategy import Strategy
from poker.table import Table


class AlwaysCallStrategy(Strategy):
    def decide(self, player, table):
        return Action.CALL, 0

    pass


class TestPlayer(TestCase):
    def test_base_player_act_not_implemented(self):
        player = Player('A', 100)
        self.assertRaises(NotImplementedError, player.act, None)
        pass

    def test_is_live(self):
        player = Player('A', 100)
        self.assertTrue(player.is_live())
        player.folded = True
        self.assertFalse(player.is_live())
        pass


class TestMachinePlayer(TestCase):
    def test_act_delegates_to_strategy(self):
        table = Table([Player('A', 100), MachinePlayer('B', 100, AlwaysCallStrategy())],
                       small_blind=1, big_blind=2, rng=random.Random(1))
        table.start_hand()
        table.post_blinds()
        machine = table.players[1]
        action, amount = machine.act(table)
        self.assertEqual(action, Action.CALL)
        pass


class TestHumanPlayer(TestCase):
    def test_act_reads_legal_action_from_input(self):
        table = Table([HumanPlayer('A', 100), Player('B', 100)],
                       small_blind=1, big_blind=2, rng=random.Random(1))
        table.start_hand()
        table.deal_hole_cards()
        table.post_blinds()
        table.start_betting_round()
        human = table.players[0]
        # heads-up: button posts big blind, so human (players[0]) faces no bet and CHECK is legal
        self.assertEqual(table.call_amount(human), 0)
        with patch('builtins.input', return_value='check'):
            action, amount = human.act(table)
        self.assertEqual(action, Action.CHECK)
        pass

    def test_act_reprompts_on_illegal_action(self):
        table = Table([HumanPlayer('A', 100), Player('B', 100)],
                       small_blind=1, big_blind=2, rng=random.Random(1))
        table.start_hand()
        table.deal_hole_cards()
        table.post_blinds()
        table.start_betting_round()
        human = table.players[0]
        # CALL is illegal here (nothing to call); should be rejected and reprompted
        with patch('builtins.input', side_effect=['call', 'check']):
            action, amount = human.act(table)
        self.assertEqual(action, Action.CHECK)
        pass

    def test_act_reprompts_when_bet_has_no_amount(self):
        table = Table([HumanPlayer('A', 100), Player('B', 100)],
                       small_blind=1, big_blind=2, rng=random.Random(1))
        table.start_hand()
        table.deal_hole_cards()
        table.post_blinds()
        table.start_betting_round()
        human = table.players[0]
        with patch('builtins.input', side_effect=['bet', 'bet 0', 'bet 10']):
            action, amount = human.act(table)
        self.assertEqual((action, amount), (Action.BET, 10))
        pass

    def test_act_reprompts_when_amount_is_not_a_number(self):
        table = Table([HumanPlayer('A', 100), Player('B', 100)],
                       small_blind=1, big_blind=2, rng=random.Random(1))
        table.start_hand()
        table.deal_hole_cards()
        table.post_blinds()
        table.start_betting_round()
        human = table.players[0]
        with patch('builtins.input', side_effect=['bet abc', 'check']):
            action, amount = human.act(table)
        self.assertEqual(action, Action.CHECK)
        pass
