"""Player and dealer abstractions for blackjack."""

from typing import List, Optional

from .hand import Hand


class Player:
    def __init__(self, name: str, bank: float = 100.0):
        self.name = name
        self.bank = bank
        self.hands: List[Hand] = [Hand()]
        self.bets: List[Optional[float]] = [None]

    @property
    def hand(self) -> Hand:
        return self.hands[0]

    @property
    def bet(self) -> Optional[float]:
        return self.bets[0]

    def place_bet(self, amount: float):
        if amount > self.bank:
            raise ValueError("Bet cannot exceed bank")
        self.bets[0] = amount
        self.bank -= amount

    def hit(self, card, hand_idx: int = 0):
        self.hands[hand_idx].add_card(card)

    def can_split(self) -> bool:
        return (len(self.hands) == 1
                and len(self.hands[0].cards) == 2
                and self.hands[0].cards[0].value() == self.hands[0].cards[1].value()
                and self.bets[0] is not None
                and self.bank >= self.bets[0])

    def split(self):
        if not self.can_split():
            raise ValueError("Cannot split")
        card1 = self.hands[0].cards[0]
        card2 = self.hands[0].cards[1]
        self.hands = [Hand(), Hand()]
        self.hands[0].add_card(card1)
        self.hands[1].add_card(card2)
        original_bet = self.bets[0]
        self.bets = [original_bet, original_bet]
        self.bank -= original_bet

    def double_down(self, hand_idx: int = 0):
        """Double the bet on a specific hand."""
        bet = self.bets[hand_idx]
        if bet is None:
            raise ValueError("No bet placed yet")
        if bet > self.bank:
            raise ValueError("Not enough money to double down")
        self.bank -= bet
        self.bets[hand_idx] = bet * 2

    def reset_hand(self):
        self.hands = [Hand()]
        self.bets = [None]

    def __repr__(self):
        return f"Player({self.name}, bank={self.bank})"


class Dealer(Player):
    """Dealer follows fixed rules. Inherits from Player."""

    def __init__(self):
        super().__init__(name="Dealer", bank=0)

    def should_hit(self) -> bool:
        return self.hand.value() < 17