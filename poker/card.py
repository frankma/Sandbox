from dataclasses import dataclass
from enum import IntEnum


class Suit(IntEnum):
    CLUBS = 1
    DIAMONDS = 2
    HEARTS = 3
    SPADES = 4


class Rank(IntEnum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14


SUIT_SYMBOLS = {
    Suit.CLUBS: 'C',
    Suit.DIAMONDS: 'D',
    Suit.HEARTS: 'H',
    Suit.SPADES: 'S',
}

RANK_SYMBOLS = {
    Rank.TWO: '2',
    Rank.THREE: '3',
    Rank.FOUR: '4',
    Rank.FIVE: '5',
    Rank.SIX: '6',
    Rank.SEVEN: '7',
    Rank.EIGHT: '8',
    Rank.NINE: '9',
    Rank.TEN: 'T',
    Rank.JACK: 'J',
    Rank.QUEEN: 'Q',
    Rank.KING: 'K',
    Rank.ACE: 'A',
}


@dataclass(frozen=True, order=True)
class Card(object):
    rank: Rank
    suit: Suit

    def __str__(self):
        return RANK_SYMBOLS[self.rank] + SUIT_SYMBOLS[self.suit]
