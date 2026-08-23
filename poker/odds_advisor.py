import random
from typing import List, Optional

from poker.card import Card
from poker.player import Player
from poker.strategy import simulate_equity
from poker.table import Table


class OddsAdvisor(object):
    def __init__(self, table: Table, player: Player):
        self.table = table  # type: Table
        self.player = player  # type: Player
        pass

    def known_cards(self) -> List[Card]:
        return self.table.known_cards_for(self.player)

    def estimate_equity(self, num_simulations: int = 1000,
                         rng: Optional[random.Random] = None) -> float:
        rng = rng if rng is not None else random.Random()
        hole_cards = list(self.player.hole_cards)
        community_cards = [card for card in self.known_cards() if card not in hole_cards]
        num_opponents = len([p for p in self.table.active_players() if p is not self.player])
        return simulate_equity(hole_cards, community_cards, num_opponents, num_simulations, rng)

    pass
