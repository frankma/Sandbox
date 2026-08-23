import random
from unittest import TestCase
from unittest.mock import patch

from poker.cli import play_hand, remove_busted_players
from poker.player import Action, HumanPlayer, MachinePlayer
from poker.strategy import Strategy
from poker.table import Table


class AlwaysCallStrategy(Strategy):
    def decide(self, player, table):
        return Action.CALL, 0

    pass


class TestPlayHand(TestCase):
    def test_full_hand_reaches_showdown_and_pays_out_pot(self):
        human = HumanPlayer('You', 100)
        bot = MachinePlayer('Bot', 100, AlwaysCallStrategy())
        table = Table([human, bot], small_blind=1, big_blind=2, rng=random.Random(6))
        total_chips_before = human.stack + bot.stack

        # human is prompted once per street (preflop/flop/turn/river): always check
        with patch('builtins.input', return_value='check'):
            play_hand(table)

        self.assertEqual(human.stack + bot.stack, total_chips_before)
        self.assertEqual(table.pot, 0)
        pass

    def test_fold_ends_hand_immediately_and_awards_pot(self):
        human = HumanPlayer('You', 100)
        bot = MachinePlayer('Bot', 100, AlwaysCallStrategy())
        table = Table([human, bot], small_blind=1, big_blind=2, rng=random.Random(6))
        # button=1 makes human the small blind, facing the bot's bigger blind, so
        # human is first to act preflop with an actual bet to fold to (FOLD is only
        # legal when there's a real bet outstanding, not against a free check)
        table.button_index = 1

        with patch('builtins.input', return_value='fold'):
            play_hand(table)

        live = [p for p in table.players if not p.folded]
        self.assertEqual(len(live), 1)
        pass


class TestRemoveBustedPlayers(TestCase):
    def test_removes_zero_stack_players_and_clamps_button(self):
        players = [HumanPlayer('A', 0), MachinePlayer('B', 50, AlwaysCallStrategy()),
                   MachinePlayer('C', 0, AlwaysCallStrategy())]
        table = Table(players, small_blind=1, big_blind=2)
        table.button_index = 2
        remove_busted_players(table)
        self.assertEqual([p.name for p in table.players], ['B'])
        self.assertEqual(table.button_index, 0)
        pass
