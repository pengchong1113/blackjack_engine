"""Hand management with scoring logic."""

from typing import List

from .card import Card


class Hand:
    def __init__(self):
        self.cards: List[Card] = []

    def add_card(self, card: Card):
        self.cards.append(card)

    def value(self) -> int:
        """Compute the blackjack value of the hand.

        Aces count as 11 unless that would bust, in which case they're 1.
        """
        total = 0
        aces = 0
        
        for c in self.cards:
            v = c.value()
            total += v
            if c.rank == "A":
                aces += 1
        
        while total > 21 and aces > 0:
            total -= 10  # count one ace as 1 instead of 11
            aces -= 1
        
        return total

    def is_bust(self) -> bool:
        return self.value() > 21

    def __repr__(self):
        return f"Hand({self.cards})"
