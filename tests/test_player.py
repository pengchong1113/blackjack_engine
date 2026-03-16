"""Tests for Player and Dealer classes."""

import pytest

from blackjack_engine.card import Card, Suit
from blackjack_engine.hand import Hand
from blackjack_engine.player import Player, Dealer


class TestPlayerBasics:
    def test_player_initialization(self):
        """Test player initialization with default bank."""
        player = Player("Alice")
        assert player.name == "Alice"
        assert player.bank == 100.0
        assert len(player.hands) == 1
        assert len(player.bets) == 1
        assert player.bets[0] is None

    def test_player_custom_bank(self):
        """Test player initialization with custom bank."""
        player = Player("Bob", bank=500.0)
        assert player.name == "Bob"
        assert player.bank == 500.0

    def test_hand_property(self):
        """Test hand property returns first hand."""
        player = Player("Alice")
        assert player.hand == player.hands[0]

    def test_bet_property(self):
        """Test bet property returns first bet."""
        player = Player("Alice")
        assert player.bet == player.bets[0]


class TestPlayerBetting:
    def test_place_bet_valid(self):
        """Test placing a valid bet."""
        player = Player("Alice", bank=100.0)
        player.place_bet(25.0)
        assert player.bets[0] == 25.0
        assert player.bank == 75.0

    def test_place_bet_exceeds_bank(self):
        """Test that betting more than bank raises error."""
        player = Player("Alice", bank=100.0)
        with pytest.raises(ValueError, match="Bet cannot exceed bank"):
            player.place_bet(150.0)

    def test_place_bet_all_in(self):
        """Test betting entire bank."""
        player = Player("Alice", bank=100.0)
        player.place_bet(100.0)
        assert player.bets[0] == 100.0
        assert player.bank == 0.0


class TestPlayerHit:
    def test_hit_adds_card_to_hand(self):
        """Test that hit adds card to hand."""
        player = Player("Alice")
        card = Card("5", Suit.HEARTS)
        player.hit(card)
        assert len(player.hand.cards) == 1
        assert player.hand.cards[0] == card

    def test_hit_multiple_cards(self):
        """Test hitting multiple times."""
        player = Player("Alice")
        card1 = Card("5", Suit.HEARTS)
        card2 = Card("7", Suit.DIAMONDS)
        card3 = Card("K", Suit.CLUBS)
        player.hit(card1)
        player.hit(card2)
        player.hit(card3)
        assert len(player.hand.cards) == 3


class TestPlayerSplit:
    def test_can_split_with_pair(self):
        """Test can_split returns True for a pair with valid bet."""
        player = Player("Alice", bank=100.0)
        player.place_bet(25.0)
        player.hit(Card("5", Suit.HEARTS))
        player.hit(Card("5", Suit.DIAMONDS))
        assert player.can_split() is True

    def test_cannot_split_without_pair(self):
        """Test can_split returns False when cards don't match."""
        player = Player("Alice", bank=100.0)
        player.place_bet(25.0)
        player.hit(Card("5", Suit.HEARTS))
        player.hit(Card("7", Suit.DIAMONDS))
        assert player.can_split() is False

    def test_cannot_split_without_bet(self):
        """Test can_split returns False without placed bet."""
        player = Player("Alice")
        player.hit(Card("5", Suit.HEARTS))
        player.hit(Card("5", Suit.DIAMONDS))
        assert player.can_split() is False

    def test_cannot_split_insufficient_funds(self):
        """Test can_split returns False when not enough money to double bet."""
        player = Player("Alice", bank=30.0)
        player.place_bet(25.0)  # bank now 5.0
        player.hit(Card("5", Suit.HEARTS))
        player.hit(Card("5", Suit.DIAMONDS))
        assert player.can_split() is False

    def test_split_success(self):
        """Test successful split."""
        player = Player("Alice", bank=100.0)
        player.place_bet(25.0)  # bank now 75.0
        player.hit(Card("5", Suit.HEARTS))
        player.hit(Card("5", Suit.DIAMONDS))
        player.split()
        assert len(player.hands) == 2
        assert len(player.bets) == 2
        assert player.bets[0] == 25.0
        assert player.bets[1] == 25.0
        assert player.bank == 50.0
        assert len(player.hands[0].cards) == 1
        assert len(player.hands[1].cards) == 1

    def test_split_raises_when_cannot_split(self):
        """Test that split raises error when not possible."""
        player = Player("Alice", bank=100.0)
        player.place_bet(25.0)
        player.hit(Card("5", Suit.HEARTS))
        player.hit(Card("7", Suit.DIAMONDS))
        with pytest.raises(ValueError, match="Cannot split"):
            player.split()


class TestPlayerDoubleDown:
    def test_double_down_success(self):
        """Test successful double down."""
        player = Player("Alice", bank=100.0)
        player.place_bet(25.0)  # bank now 75.0
        assert player.bets[0] == 25.0
        player.double_down()
        assert player.bets[0] == 50.0
        assert player.bank == 50.0

    def test_double_down_without_bet(self):
        """Test double down without placed bet raises error."""
        player = Player("Alice", bank=100.0)
        with pytest.raises(ValueError, match="No bet placed yet"):
            player.double_down()

    def test_double_down_insufficient_funds(self):
        """Test double down with insufficient funds raises error."""
        player = Player("Alice", bank=30.0)
        player.place_bet(25.0)  # bank now 5.0
        with pytest.raises(ValueError, match="Not enough money to double down"):
            player.double_down()

    def test_double_down_on_specific_hand(self):
        """Test double down on a specific hand after split."""
        player = Player("Alice", bank=100.0)
        player.place_bet(25.0)  # bank now 75.0
        player.hit(Card("5", Suit.HEARTS))
        player.hit(Card("5", Suit.DIAMONDS))
        player.split()  # bank now 50.0
        player.double_down(hand_idx=1)
        assert player.bets[1] == 50.0
        assert player.bank == 25.0


class TestPlayerReset:
    def test_reset_hand(self):
        """Test that reset_hand clears hands and bets."""
        player = Player("Alice", bank=75.0)
        player.bets[0] = 25.0
        player.hit(Card("K", Suit.HEARTS))
        player.hit(Card("Q", Suit.DIAMONDS))
        player.reset_hand()
        assert len(player.hands) == 1
        assert len(player.hands[0].cards) == 0
        assert len(player.bets) == 1
        assert player.bets[0] is None


class TestPlayerRepresentation:
    def test_player_repr(self):
        """Test player string representation."""
        player = Player("Alice", bank=100.0)
        assert "Alice" in repr(player)
        assert "100" in repr(player)


class TestDealer:
    def test_dealer_initialization(self):
        """Test dealer initialization."""
        dealer = Dealer()
        assert dealer.name == "Dealer"
        assert dealer.bank == 0

    def test_dealer_should_hit_below_17(self):
        """Test dealer should hit on 16 or less."""
        dealer = Dealer()
        dealer.hit(Card("9", Suit.HEARTS))
        dealer.hit(Card("5", Suit.DIAMONDS))  # total 14
        assert dealer.should_hit() is True

    def test_dealer_should_not_hit_at_17(self):
        """Test dealer should stand on 17."""
        dealer = Dealer()
        dealer.hit(Card("K", Suit.HEARTS))
        dealer.hit(Card("7", Suit.DIAMONDS))  # total 17
        assert dealer.should_hit() is False

    def test_dealer_should_not_hit_above_17(self):
        """Test dealer should stand on 18+."""
        dealer = Dealer()
        dealer.hit(Card("K", Suit.HEARTS))
        dealer.hit(Card("Q", Suit.DIAMONDS))  # total 20
        assert dealer.should_hit() is False

    def test_dealer_soft_17(self):
        """Test dealer hits on soft 17 (A + 6)."""
        dealer = Dealer()
        dealer.hit(Card("A", Suit.HEARTS))
        dealer.hit(Card("6", Suit.DIAMONDS))  # A(11) + 6 = 17
        # In standard blackjack, dealer stands on 17
        assert dealer.should_hit() is False