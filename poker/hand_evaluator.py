from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
from itertools import combinations
from typing import List, Tuple

from poker.card import Card


class HandCategory(IntEnum):
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9


@dataclass(order=True)
class HandRank(object):
    category: HandCategory
    tiebreakers: Tuple[int, ...]


def _detect_straight(distinct_ranks_desc: List[int]) -> Tuple[bool, int]:
    if len(distinct_ranks_desc) != 5:
        return False, 0
    if distinct_ranks_desc[0] - distinct_ranks_desc[4] == 4:
        return True, distinct_ranks_desc[0]
    if distinct_ranks_desc == [14, 5, 4, 3, 2]:
        return True, 5
    return False, 0


def _evaluate_five(cards: Tuple[Card, ...]) -> HandRank:
    ranks = sorted((card.rank.value for card in cards), reverse=True)
    is_flush = len({card.suit for card in cards}) == 1
    is_straight, straight_high = _detect_straight(sorted(set(ranks), reverse=True))

    counts = Counter(ranks)
    by_count_then_rank = sorted(counts.items(), key=lambda item: (item[1], item[0]), reverse=True)
    count_pattern = tuple(count for _, count in by_count_then_rank)
    ranks_by_count = tuple(rank for rank, _ in by_count_then_rank)

    if is_straight and is_flush:
        return HandRank(HandCategory.STRAIGHT_FLUSH, (straight_high,))
    if count_pattern[0] == 4:
        return HandRank(HandCategory.FOUR_OF_A_KIND, ranks_by_count)
    if count_pattern[:2] == (3, 2):
        return HandRank(HandCategory.FULL_HOUSE, ranks_by_count)
    if is_flush:
        return HandRank(HandCategory.FLUSH, tuple(ranks))
    if is_straight:
        return HandRank(HandCategory.STRAIGHT, (straight_high,))
    if count_pattern[0] == 3:
        return HandRank(HandCategory.THREE_OF_A_KIND, ranks_by_count)
    if count_pattern[:2] == (2, 2):
        return HandRank(HandCategory.TWO_PAIR, ranks_by_count)
    if count_pattern[0] == 2:
        return HandRank(HandCategory.PAIR, ranks_by_count)
    return HandRank(HandCategory.HIGH_CARD, tuple(ranks))


class HandEvaluator(object):
    @staticmethod
    def evaluate(cards: List[Card]) -> HandRank:
        if len(cards) < 5:
            raise ValueError('need at least 5 cards to evaluate a hand, got %d' % len(cards))
        return max(_evaluate_five(combo) for combo in combinations(cards, 5))
