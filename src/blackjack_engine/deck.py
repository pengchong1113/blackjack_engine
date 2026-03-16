"""Deck generator and management for blackjack."""

import random

from .card import Card, Suit


class Deck:
    """Standard 52-card deck that can be shuffled and dealt from.

    This is implemented as an iterable generator so that other code can
    consume cards lazily.
    """

    def __init__(self):
        self.reset()

    def reset(self):
        """Populate deck with all card combinations."""
        self._cards = [Card(rank, suit) for suit in Suit for rank in Card.RANKS]

    def shuffle(self):
        random.shuffle(self._cards)

    def draw(self) -> Card:
        """Draw a single card from the top of the deck."""
        return self._cards.pop()

    def __len__(self):
        return len(self._cards)

