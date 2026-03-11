"""Card and suit representation for blackjack game."""

from enum import Enum


class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"


class Card:
    """Immutable playing card with value and suit.

    Implements hashability and comparison for use in sets and dicts.
    """

    __slots__ = ("_rank", "_suit")

    RANKS = [str(n) for n in range(2, 11)] + ["J", "Q", "K", "A"]

    def __init__(self, rank: str, suit: Suit):
        if rank not in Card.RANKS:
            raise ValueError(f"Invalid rank: {rank}")
        if not isinstance(suit, Suit):
            raise TypeError("Suit must be a Suit enum")
        self._rank = rank
        self._suit = suit

    @property
    def rank(self) -> str:
        return self._rank

    @property
    def suit(self) -> Suit:
        return self._suit

    def value(self) -> int:
        """Return blackjack value of the card (Aces count as 11)."""
        if self.rank.isdigit():
            return int(self.rank)
        if self.rank in ("J", "Q", "K"):
            return 10
        return 11  # ace

    def __repr__(self):
        return f"Card({self.rank} of {self.suit.value})"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank and self.suit == other.suit

    def __hash__(self):
        # allows using Card in sets or as dict keys
        return hash((self.rank, self.suit))
