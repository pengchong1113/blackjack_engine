"""Tests for Deck class."""

import pytest

from blackjack_engine.deck import Deck
from blackjack_engine.card import Card, Suit


class TestDeckInitialization:
    def test_deck_creation(self):
        """Test that a new deck is created with 52 cards."""
        deck = Deck()
        assert len(deck) == 52

    def test_deck_contains_all_cards(self):
        """Test that deck contains all 52 unique cards."""
        deck = Deck()
        cards = set(deck._cards)
        assert len(cards) == 52

    def test_deck_has_correct_suits(self):
        """Test that deck has cards from all suits."""
        deck = Deck()
        suits = {card.suit for card in deck._cards}
        assert len(suits) == 4
        assert Suit.HEARTS in suits
        assert Suit.DIAMONDS in suits
        assert Suit.CLUBS in suits
        assert Suit.SPADES in suits

    def test_deck_has_correct_ranks(self):
        """Test that deck has all ranks."""
        deck = Deck()
        ranks = {card.rank for card in deck._cards}
        expected_ranks = set(Card.RANKS)
        assert ranks == expected_ranks


class TestDeckDraw:
    def test_draw_single_card(self):
        """Test drawing a single card from deck."""
        deck = Deck()
        card = deck.draw()
        assert isinstance(card, Card)
        assert len(deck) == 51

    def test_draw_multiple_cards(self):
        """Test drawing multiple cards decreases deck size."""
        deck = Deck()
        initial_size = len(deck)
        for i in range(10):
            card = deck.draw()
            assert isinstance(card, Card)
            assert len(deck) == initial_size - (i + 1)

    def test_draw_returns_different_cards(self):
        """Test that drawing multiple times returns different cards."""
        deck = Deck()
        cards = [deck.draw() for _ in range(5)]
        assert len(set(cards)) == 5  # All cards should be unique

    def test_draw_all_cards(self):
        """Test drawing all cards from deck."""
        deck = Deck()
        cards = []
        while len(deck) > 0:
            cards.append(deck.draw())
        assert len(cards) == 52
        assert len(set(cards)) == 52


class TestDeckReset:
    def test_reset_restores_full_deck(self):
        """Test that reset restores the deck to 52 cards."""
        deck = Deck()
        # Draw some cards
        for _ in range(20):
            deck.draw()
        assert len(deck) == 32
        # Reset
        deck.reset()
        assert len(deck) == 52

    def test_reset_contains_all_cards(self):
        """Test that reset deck contains all 52 unique cards."""
        deck = Deck()
        for _ in range(10):
            deck.draw()
        deck.reset()
        cards = set(deck._cards)
        assert len(cards) == 52

    def test_reset_multiple_times(self):
        """Test that deck can be reset multiple times."""
        deck = Deck()
        for attempt in range(3):
            for _ in range(15):
                deck.draw()
            assert len(deck) == 37
            deck.reset()
            assert len(deck) == 52


class TestDeckShuffle:
    def test_shuffle_changes_order(self):
        """Test that shuffle changes card order (with high probability)."""
        deck1 = Deck()
        original_order = [card for card in deck1._cards]
        deck1.shuffle()
        shuffled_order = [card for card in deck1._cards]
        # It's extremely unlikely (but technically possible) for shuffle to produce the same order
        assert original_order != shuffled_order

    def test_shuffle_preserves_cards(self):
        """Test that shuffle doesn't add or remove cards."""
        deck = Deck()
        original_cards = set(deck._cards)
        deck.shuffle()
        shuffled_cards = set(deck._cards)
        assert original_cards == shuffled_cards
        assert len(deck) == 52

    def test_shuffle_after_draw(self):
        """Test shuffling after drawing some cards."""
        deck = Deck()
        for _ in range(5):
            deck.draw()
        assert len(deck) == 47
        deck.shuffle()
        assert len(deck) == 47

    def test_multiple_shuffles(self):
        """Test that multiple shuffles work correctly."""
        deck = Deck()
        for _ in range(5):
            deck.shuffle()
        assert len(deck) == 52
        original_cards = set(deck._cards)
        deck.shuffle()
        shuffled_cards = set(deck._cards)
        assert original_cards == shuffled_cards


class TestDeckLength:
    def test_deck_length_after_operations(self):
        """Test that len() works correctly after various operations."""
        deck = Deck()
        assert len(deck) == 52
        deck.draw()
        assert len(deck) == 51
        deck.draw()
        assert len(deck) == 50
        deck.reset()
        assert len(deck) == 52


class TestDeckIntegration:
    def test_draw_reset_shuffle_cycle(self):
        """Test a complete cycle of drawing, resetting, and shuffling."""
        deck = Deck()
        # Draw some cards
        drawn1 = [deck.draw() for _ in range(10)]
        assert len(deck) == 42
        # Shuffle
        deck.shuffle()
        assert len(deck) == 42
        # Reset
        deck.reset()
        assert len(deck) == 52
        # Shuffle again
        deck.shuffle()
        assert len(deck) == 52
        # Draw the whole deck
        cards = [deck.draw() for _ in range(52)]
        assert len(deck) == 0