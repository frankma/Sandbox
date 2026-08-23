from enum import Enum
from typing import List, Tuple, TYPE_CHECKING

from poker.card import Card

if TYPE_CHECKING:
    from poker.strategy import Strategy
    from poker.table import Table


class Action(Enum):
    FOLD = 1
    CHECK = 2
    CALL = 3
    BET = 4
    RAISE = 5
    ALL_IN = 6


class Player(object):
    def __init__(self, name: str, stack: int):
        self.name = name  # type: str
        self.stack = stack  # type: int
        self.hole_cards = []  # type: List[Card]
        self.current_bet = 0  # type: int
        self.folded = False  # type: bool
        self.all_in = False  # type: bool
        pass

    def act(self, table: 'Table') -> Tuple[Action, int]:
        raise NotImplementedError

    def is_live(self) -> bool:
        return not self.folded and not self.all_in

    pass


class HumanPlayer(Player):
    def act(self, table: 'Table') -> Tuple[Action, int]:
        legal = table.legal_actions(self)
        to_call = table.call_amount(self)
        print('%s | stack=%d pot=%d to_call=%d hole=%s board=%s' % (
            self.name, self.stack, table.pot, to_call,
            [str(c) for c in self.hole_cards], [str(c) for c in table.community_cards]))
        print('legal actions: %s' % [action.name for action in legal])
        while True:
            raw = input('action (e.g. "call", "raise 20"): ').strip().lower()
            parts = raw.split()
            if not parts:
                continue
            try:
                action = Action[parts[0].upper()]
            except KeyError:
                print('unrecognized action')
                continue
            if action not in legal:
                print('illegal action right now')
                continue
            try:
                amount = int(parts[1]) if len(parts) > 1 else 0
            except ValueError:
                print('amount must be a whole number')
                continue
            if action in (Action.BET, Action.RAISE) and amount <= 0:
                print('%s requires a positive amount, e.g. "%s 10"' % (
                    action.name.lower(), action.name.lower()))
                continue
            return action, amount

    pass


class MachinePlayer(Player):
    def __init__(self, name: str, stack: int, strategy: 'Strategy'):
        super().__init__(name, stack)
        self.strategy = strategy  # type: Strategy
        pass

    def act(self, table: 'Table') -> Tuple[Action, int]:
        return self.strategy.decide(self, table)

    pass
