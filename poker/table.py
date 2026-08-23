import random
from enum import Enum
from typing import List, Optional, Set

from poker.card import Card
from poker.deck import Deck
from poker.player import Action, Player


class BettingRound(Enum):
    PREFLOP = 1
    FLOP = 2
    TURN = 3
    RIVER = 4
    SHOWDOWN = 5


class Table(object):
    def __init__(self, players: List[Player], small_blind: int, big_blind: int,
                 rng: Optional[random.Random] = None):
        self.players = players  # type: List[Player]
        self.small_blind = small_blind  # type: int
        self.big_blind = big_blind  # type: int
        self.rng = rng if rng is not None else random.Random()  # type: random.Random
        self.deck = Deck(rng=self.rng)  # type: Deck
        self.community_cards = []  # type: List[Card]
        self.pot = 0  # type: int
        self.button_index = 0  # type: int
        self.current_round = None  # type: Optional[BettingRound]
        self.current_bet = 0  # type: int
        self.next_to_act_index = None  # type: Optional[int]
        self._acted_this_round = set()  # type: Set[Player]
        pass

    def start_hand(self) -> None:
        self.deck = Deck(rng=self.rng)
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.current_round = BettingRound.PREFLOP
        for player in self.players:
            player.hole_cards = []
            player.current_bet = 0
            player.folded = False
            player.all_in = False
        pass

    def _order_from(self, start_index: int) -> List[Player]:
        n = len(self.players)
        return [self.players[(start_index + i) % n] for i in range(n)]

    def deal_hole_cards(self) -> None:
        order = self._order_from((self.button_index + 1) % len(self.players))
        for _ in range(2):
            for player in order:
                player.hole_cards.extend(self.deck.draw(1))
        pass

    def _reset_bets_for_new_round(self) -> None:
        self.current_bet = 0
        for player in self.players:
            player.current_bet = 0
        pass

    def deal_flop(self) -> None:
        self.deck.burn()
        self.community_cards.extend(self.deck.draw(3))
        self.current_round = BettingRound.FLOP
        self._reset_bets_for_new_round()
        pass

    def deal_turn(self) -> None:
        self.deck.burn()
        self.community_cards.extend(self.deck.draw(1))
        self.current_round = BettingRound.TURN
        self._reset_bets_for_new_round()
        pass

    def deal_river(self) -> None:
        self.deck.burn()
        self.community_cards.extend(self.deck.draw(1))
        self.current_round = BettingRound.RIVER
        self._reset_bets_for_new_round()
        pass

    def known_cards_for(self, viewer: Player) -> List[Card]:
        known = list(self.community_cards)
        known.extend(viewer.hole_cards)
        if self.current_round == BettingRound.SHOWDOWN:
            for player in self.players:
                if player is not viewer and not player.folded:
                    known.extend(player.hole_cards)
        return known

    def active_players(self) -> List[Player]:
        return [player for player in self.players if not player.folded]

    def _contribute(self, player: Player, amount: int) -> None:
        amount = min(amount, player.stack)
        player.stack -= amount
        player.current_bet += amount
        self.pot += amount
        if player.stack == 0:
            player.all_in = True
        pass

    def post_blinds(self) -> None:
        n = len(self.players)
        small_blind_player = self.players[(self.button_index + 1) % n]
        big_blind_player = self.players[(self.button_index + 2) % n]
        self._contribute(small_blind_player, self.small_blind)
        self._contribute(big_blind_player, self.big_blind)
        self.current_bet = self.big_blind
        pass

    def call_amount(self, player: Player) -> int:
        return max(0, self.current_bet - player.current_bet)

    def legal_actions(self, player: Player) -> List[Action]:
        if player.stack <= 0:
            return []
        to_call = self.call_amount(player)
        actions = []
        if to_call == 0:
            actions.append(Action.CHECK)
            actions.append(Action.BET)
        else:
            actions.append(Action.FOLD)
            actions.append(Action.CALL)
            if player.stack > to_call:
                actions.append(Action.RAISE)
        actions.append(Action.ALL_IN)
        return actions

    def _next_live_index(self, from_index: int) -> Optional[int]:
        n = len(self.players)
        for i in range(n):
            idx = (from_index + i) % n
            player = self.players[idx]
            if not player.folded and not player.all_in:
                return idx
        return None

    def start_betting_round(self, first_to_act_index: Optional[int] = None) -> None:
        self._acted_this_round = set()
        if first_to_act_index is None:
            first_to_act_index = (self.button_index + 1) % len(self.players)
        self.next_to_act_index = self._next_live_index(first_to_act_index)
        pass

    def current_actor(self) -> Optional[Player]:
        if self.next_to_act_index is None:
            return None
        return self.players[self.next_to_act_index]

    def apply_action(self, player: Player, action: Action, amount: int = 0) -> None:
        is_raise = False
        if action == Action.FOLD:
            player.folded = True
        elif action == Action.CHECK:
            pass
        elif action == Action.CALL:
            self._contribute(player, self.call_amount(player))
        elif action == Action.BET:
            if amount <= 0:
                raise ValueError('bet amount must be positive')
            self._contribute(player, amount)
            self.current_bet = player.current_bet
            is_raise = True
        elif action == Action.RAISE:
            total = self.call_amount(player) + amount
            self._contribute(player, total)
            self.current_bet = player.current_bet
            is_raise = True
        elif action == Action.ALL_IN:
            self._contribute(player, player.stack)
            if player.current_bet > self.current_bet:
                self.current_bet = player.current_bet
                is_raise = True
        else:
            raise NotImplementedError

        if is_raise:
            self._acted_this_round = {player}
        else:
            self._acted_this_round.add(player)

        self.next_to_act_index = self._next_live_index(self.next_to_act_index + 1) \
            if self.next_to_act_index is not None else None
        pass

    def is_betting_round_complete(self) -> bool:
        live = self.active_players()
        if len(live) <= 1:
            return True
        needs_to_act = [player for player in live if not player.all_in]
        if not needs_to_act:
            return True
        return all(player in self._acted_this_round and player.current_bet == self.current_bet
                   for player in needs_to_act)

    pass
