import random
from typing import List, Optional, Tuple

from poker.card import Card, Rank, Suit
from poker.hand_evaluator import HandEvaluator
from poker.player import Action, Player
from poker.table import Table


def simulate_equity(hole_cards: List[Card], community_cards: List[Card], num_opponents: int,
                     num_simulations: int, rng: random.Random) -> float:
    full_deck = [Card(rank, suit) for suit in Suit for rank in Rank]
    known = set(hole_cards) | set(community_cards)
    unseen = [card for card in full_deck if card not in known]
    cards_to_come = 5 - len(community_cards)

    wins = 0.0
    for _ in range(num_simulations):
        sample = rng.sample(unseen, num_opponents * 2 + cards_to_come)
        opponents_hole = [sample[i * 2:i * 2 + 2] for i in range(num_opponents)]
        board = community_cards + sample[num_opponents * 2:]
        my_rank = HandEvaluator.evaluate(hole_cards + board)
        opponents_rank = [HandEvaluator.evaluate(hole + board) for hole in opponents_hole]
        best_opponent = max(opponents_rank) if opponents_rank else None
        if best_opponent is None or my_rank > best_opponent:
            wins += 1.0
        elif my_rank == best_opponent:
            wins += 0.5
    return wins / num_simulations


class Strategy(object):
    def decide(self, player: Player, table: Table) -> Tuple[Action, int]:
        raise NotImplementedError

    pass


class MonteCarloStrategy(Strategy):
    def __init__(self, num_simulations: int = 500, rng: Optional[random.Random] = None,
                 fold_threshold: float = 0.08, raise_threshold: float = 0.65):
        self.num_simulations = num_simulations  # type: int
        self.rng = rng if rng is not None else random.Random()  # type: random.Random
        self.fold_threshold = fold_threshold  # type: float
        self.raise_threshold = raise_threshold  # type: float
        pass

    def estimate_equity(self, hole_cards: List[Card], community_cards: List[Card],
                         num_opponents: int) -> float:
        return simulate_equity(hole_cards, community_cards, num_opponents,
                                self.num_simulations, self.rng)

    def decide(self, player: Player, table: Table) -> Tuple[Action, int]:
        opponents = [other for other in table.active_players() if other is not player]
        equity = self.estimate_equity(player.hole_cards, table.community_cards, len(opponents))
        to_call = table.call_amount(player)
        pot_odds = to_call / (table.pot + to_call) if to_call > 0 else 0.0
        legal = table.legal_actions(player)

        if to_call == 0:
            if equity > self.raise_threshold and Action.BET in legal:
                return Action.BET, max(table.big_blind, int(table.pot * 0.5))
            return Action.CHECK, 0

        if equity < pot_odds - self.fold_threshold:
            return Action.FOLD, 0
        if equity > self.raise_threshold and Action.RAISE in legal:
            return Action.RAISE, max(table.big_blind, int(table.pot * 0.5))
        return Action.CALL, 0

    pass
