"""Tests for Card class."""

import pytest

from blackjack_engine.card import Card, Suit


class TestCardCreation:
    def test_card_valid_numeric_ranks(self):
        """Test creating cards with valid numeric ranks."""
        for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10"]:
            card = Card(rank, Suit.HEARTS)
            assert card.rank == rank

    def test_card_valid_face_ranks(self):
        """Test creating cards with face ranks."""
        for rank in ["J", "Q", "K", "A"]:
            card = Card(rank, Suit.HEARTS)
            assert card.rank == rank

    def test_card_all_suits(self):
        """Test creating cards with all suits."""
        for suit in [Suit.HEARTS, Suit.DIAMONDS, Suit.CLUBS, Suit.SPADES]:
            card = Card("A", suit)
            assert card.suit == suit

    def test_invalid_rank(self):
        """Test that invalid ranks raise ValueError."""
        with pytest.raises(ValueError, match="Invalid rank"):
            Card("Z", Suit.HEARTS)

    def test_invalid_suit_type(self):
        """Test that non-Suit objects raise TypeError."""
        with pytest.raises(TypeError, match="Suit must be a Suit enum"):
            Card("A", "HEARTS")

    def test_invalid_rank_int(self):
        """Test that integer rank raises ValueError."""
        with pytest.raises(ValueError):
            Card(1, Suit.HEARTS)


class TestCardValue:
    def test_numeric_card_values(self):
        """Test that numeric cards have correct values."""
        assert Card("2", Suit.HEARTS).value() == 2
        assert Card("5", Suit.HEARTS).value() == 5
        assert Card("9", Suit.HEARTS).value() == 9
        assert Card("10", Suit.HEARTS).value() == 10

    def test_face_card_values(self):
        """Test that face cards have value 10."""
        assert Card("J", Suit.HEARTS).value() == 10
        assert Card("Q", Suit.HEARTS).value() == 10
        assert Card("K", Suit.HEARTS).value() == 10

    def test_ace_value(self):
        """Test that aces have value 11 in card.value()."""
        assert Card("A", Suit.HEARTS).value() == 11


class TestCardEquality:
    def test_card_equality_same(self):
        """Test that identical cards are equal."""
        c1 = Card("A", Suit.SPADES)
        c2 = Card("A", Suit.SPADES)
        assert c1 == c2

    def test_card_inequality_different_rank(self):
        """Test that cards with different ranks are not equal."""
        c1 = Card("A", Suit.SPADES)
        c2 = Card("K", Suit.SPADES)
        assert c1 != c2

    def test_card_inequality_different_suit(self):
        """Test that cards with different suits are not equal."""
        c1 = Card("A", Suit.SPADES)
        c2 = Card("A", Suit.HEARTS)
        assert c1 != c2

    def test_card_not_equal_to_other_types(self):
        """Test that card is not equal to other types."""
        card = Card("A", Suit.SPADES)
        assert card != "A♠"
        assert card != 11
        assert card != None


class TestCardHash:
    def test_card_hash_equality(self):
        """Test that equal cards have equal hash values."""
        c1 = Card("A", Suit.SPADES)
        c2 = Card("A", Suit.SPADES)
        assert hash(c1) == hash(c2)

    def test_card_hash_inequality(self):
        """Test that different cards have different hash values."""
        c1 = Card("A", Suit.SPADES)
        c2 = Card("K", Suit.SPADES)
        assert hash(c1) != hash(c2)

    def test_card_in_set(self):
        """Test that cards can be used in sets."""
        c1 = Card("A", Suit.SPADES)
        c2 = Card("A", Suit.SPADES)
        c3 = Card("K", Suit.HEARTS)
        card_set = {c1, c2, c3}
        assert len(card_set) == 2  # c1 and c2 are the same

    def test_card_as_dict_key(self):
        """Test that cards can be used as dictionary keys."""
        c1 = Card("A", Suit.SPADES)
        c2 = Card("A", Suit.SPADES)
        card_dict = {c1: "ace of spades"}
        assert card_dict[c2] == "ace of spades"


class TestCardDisplay:
    def test_display_numeric_cards(self):
        """Test display format for numeric cards."""
        card = Card("5", Suit.HEARTS)
        display = card.display()
        assert display == "5♥"

    def test_display_face_cards(self):
        """Test display format for face cards."""
        assert Card("J", Suit.HEARTS).display() == "J♥"
        assert Card("Q", Suit.DIAMONDS).display() == "Q♦"
        assert Card("K", Suit.CLUBS).display() == "K♣"

    def test_display_ace(self):
        """Test display format for ace."""
        card = Card("A", Suit.SPADES)
        assert card.display() == "A♠"

    def test_display_all_suits(self):
        """Test display symbols for all suits."""
        hearts = Card("2", Suit.HEARTS).display()
        diamonds = Card("2", Suit.DIAMONDS).display()
        clubs = Card("2", Suit.CLUBS).display()
        spades = Card("2", Suit.SPADES).display()
        assert "♥" in hearts
        assert "♦" in diamonds
        assert "♣" in clubs
        assert "♠" in spades


class TestCardImagePath:
    def test_image_path_format(self):
        """Test that image path follows correct format."""
        card = Card("5", Suit.HEARTS)
        path = card.image_path()
        assert "hearts_5.png" in path
        assert "cards" in path

    def test_image_path_all_suits(self):
        """Test image paths for all suits."""
        assert "hearts_A.png" in Card("A", Suit.HEARTS).image_path()
        assert "diamonds_K.png" in Card("K", Suit.DIAMONDS).image_path()
        assert "clubs_Q.png" in Card("Q", Suit.CLUBS).image_path()
        assert "spades_J.png" in Card("J", Suit.SPADES).image_path()

    def test_image_path_all_ranks(self):
        """Test image paths for all ranks."""
        for rank in ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]:
            card = Card(rank, Suit.HEARTS)
            path = card.image_path()
            assert f"hearts_{rank}.png" in path


class TestCardRepresentation:
    def test_card_repr(self):
        """Test string representation of card."""
        card = Card("A", Suit.SPADES)
        repr_str = repr(card)
        assert "Card" in repr_str
        assert "A" in repr_str
        assert "Spades" in repr_str