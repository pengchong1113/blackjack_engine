"""Tests for Hand class."""

import pytest

from blackjack_engine.card import Card, Suit
from blackjack_engine.hand import Hand


class TestHandBasics:
    def test_hand_initialization(self):
        """Test that a new hand is empty."""
        hand = Hand()
        assert hand.cards == []
        assert hand.value() == 0

    def test_add_single_card(self):
        """Test adding a single card to hand."""
        hand = Hand()
        card = Card("5", Suit.HEARTS)
        hand.add_card(card)
        assert len(hand.cards) == 1
        assert hand.cards[0] == card

    def test_add_multiple_cards(self):
        """Test adding multiple cards to hand."""
        hand = Hand()
        card1 = Card("K", Suit.HEARTS)
        card2 = Card("Q", Suit.DIAMONDS)
        card3 = Card("5", Suit.CLUBS)
        hand.add_card(card1)
        hand.add_card(card2)
        hand.add_card(card3)
        assert len(hand.cards) == 3


class TestHandValue:
    def test_numeric_cards_value(self):
        """Test value calculation with numeric cards."""
        hand = Hand()
        hand.add_card(Card("5", Suit.HEARTS))
        hand.add_card(Card("7", Suit.DIAMONDS))
        assert hand.value() == 12

    def test_face_cards_value(self):
        """Test that face cards are worth 10."""
        hand = Hand()
        hand.add_card(Card("K", Suit.HEARTS))
        hand.add_card(Card("Q", Suit.DIAMONDS))
        hand.add_card(Card("J", Suit.CLUBS))
        assert hand.value() == 30

    def test_ace_as_11(self):
        """Test ace counting as 11 when total <= 21."""
        hand = Hand()
        hand.add_card(Card("A", Suit.HEARTS))
        hand.add_card(Card("K", Suit.DIAMONDS))
        assert hand.value() == 21

    def test_ace_as_1_when_needed(self):
        """Test ace counting as 1 when total would bust as 11."""
        hand = Hand()
        hand.add_card(Card("A", Suit.HEARTS))
        hand.add_card(Card("K", Suit.DIAMONDS))
        hand.add_card(Card("Q", Suit.CLUBS))
        assert hand.value() == 21  # A(1) + K(10) + Q(10)

    def test_multiple_aces(self):
        """Test that multiple aces are handled correctly."""
        hand = Hand()
        hand.add_card(Card("A", Suit.HEARTS))
        hand.add_card(Card("A", Suit.DIAMONDS))
        hand.add_card(Card("9", Suit.CLUBS))
        # One ace as 11, one as 1: 11 + 1 + 9 = 21
        assert hand.value() == 21

    def test_multiple_aces_with_high_cards(self):
        """Test multiple aces with high cards all count as 1."""
        hand = Hand()
        hand.add_card(Card("A", Suit.HEARTS))
        hand.add_card(Card("A", Suit.DIAMONDS))
        hand.add_card(Card("K", Suit.CLUBS))
        # A(1) + A(1) + K(10) = 12
        assert hand.value() == 12


class TestHandBust:
    def test_not_bust_at_21(self):
        """Test that hand with value 21 is not bust."""
        hand = Hand()
        hand.add_card(Card("K", Suit.HEARTS))
        hand.add_card(Card("Q", Suit.DIAMONDS))
        hand.add_card(Card("A", Suit.CLUBS))
        assert hand.value() == 21
        assert not hand.is_bust()

    def test_not_bust_below_21(self):
        """Test that hand with value < 21 is not bust."""
        hand = Hand()
        hand.add_card(Card("5", Suit.HEARTS))
        hand.add_card(Card("7", Suit.DIAMONDS))
        assert hand.value() == 12
        assert not hand.is_bust()

    def test_bust_above_21(self):
        """Test that hand with value > 21 is bust."""
        hand = Hand()
        hand.add_card(Card("K", Suit.HEARTS))
        hand.add_card(Card("Q", Suit.DIAMONDS))
        hand.add_card(Card("5", Suit.CLUBS))
        assert hand.value() == 25
        assert hand.is_bust()

    def test_bust_at_22(self):
        """Test bust at exactly 22."""
        hand = Hand()
        hand.add_card(Card("K", Suit.HEARTS))
        hand.add_card(Card("9", Suit.DIAMONDS))
        hand.add_card(Card("3", Suit.CLUBS))
        assert hand.value() == 22
        assert hand.is_bust()


class TestHandRepresentation:
    def test_hand_repr(self):
        """Test hand string representation."""
        hand = Hand()
        hand.add_card(Card("K", Suit.HEARTS))
        hand.add_card(Card("A", Suit.DIAMONDS))
        repr_str = repr(hand)
        assert "Hand" in repr_str
        assert "K of Hearts" in repr_str
        assert "A of Diamonds" in repr_str
