import random
from typing import List, Optional

from poker.card import Card, Rank, Suit


class Deck(object):
    def __init__(self, rng: Optional[random.Random] = None):
        self.rng = rng if rng is not None else random.Random()  # type: random.Random
        self.cards = [Card(rank, suit) for suit in Suit for rank in Rank]  # type: List[Card]

    @property
    def cards_remaining(self) -> int:
        return len(self.cards)

    def shuffle(self) -> None:
        self.rng.shuffle(self.cards)

    def draw(self, n: int = 1) -> List[Card]:
        if n > len(self.cards):
            raise ValueError('cannot draw %d cards, only %d remain' % (n, len(self.cards)))
        drawn, self.cards = self.cards[:n], self.cards[n:]
        return drawn

    def burn(self) -> Card:
        return self.draw(1)[0]
