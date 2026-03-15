"""Tests for BlackjackGame class."""

import pytest

from blackjack_engine.player import Player, Dealer
from blackjack_engine.game import BlackjackGame
from blackjack_engine.card import Card, Suit


class TestGameInitialization:
    def test_game_creation(self):
        """Test that game is created with player and dealer."""
        player = Player("Alice")
        game = BlackjackGame(player)
        assert game.player == player
        assert isinstance(game.dealer, Dealer)
        assert isinstance(game.deck, object)  # Deck object
        assert game.dealer_upcard is None

    def test_game_has_shuffled_deck(self):
        """Test that game deck has 52 cards after initialization."""
        player = Player("Alice")
        game = BlackjackGame(player)
        assert len(game.deck) == 52


class TestGameDealInitial:
    def test_deal_initial_cards_distributed(self):
        """Test that deal_initial distributes correct number of cards."""
        player = Player("Alice")
        game = BlackjackGame(player)
        game.deal_initial()
        # Player gets 2 cards
        assert len(player.hand.cards) == 2
        # Dealer gets 2 cards
        assert len(game.dealer.hand.cards) == 2
        # Deck has 48 cards left
        assert len(game.deck) == 48

    def test_deal_initial_sets_upcard(self):
        """Test that deal_initial sets dealer upcard."""
        player = Player("Alice")
        game = BlackjackGame(player)
        game.deal_initial()
        assert game.dealer_upcard is not None
        assert isinstance(game.dealer_upcard, Card)
        # Upcard should be the last card dealt to dealer
        assert game.dealer_upcard == game.dealer.hand.cards[-1]


class TestGameHitPlayer:
    def test_hit_player_adds_card(self):
        """Test that hit_player adds a card to player's hand."""
        player = Player("Alice")
        game = BlackjackGame(player)
        game.deal_initial()
        initial_cards = len(player.hand.cards)
        card = game.hit_player()
        assert len(player.hand.cards) == initial_cards + 1
        assert isinstance(card, Card)

    def test_hit_player_decreases_deck(self):
        """Test that hit_player decreases deck size."""
        player = Player("Alice")
        game = BlackjackGame(player)
        game.deal_initial()
        initial_deck_size = len(game.deck)
        game.hit_player()
        assert len(game.deck) == initial_deck_size - 1


class TestGameDoubleDown:
    def test_double_down_increases_bet_and_adds_card(self):
        """Test that double_down doubles bet and adds one card."""
        player = Player("Alice", bank=100)
        player.place_bet(25)
        assert player.bet == 25
        assert player.bank == 75
        game = BlackjackGame(player)
        initial_cards = len(player.hand.cards)
        card = game.double_down()
        assert player.bet == 50
        assert player.bank == 50
        assert len(player.hand.cards) == initial_cards + 1


class TestGameSplitPlayer:
    def test_split_player_creates_two_hands(self):
        """Test that split_player creates two hands and deals cards."""
        player = Player("Alice", bank=100)
        player.place_bet(25)
        player.hit(Card("5", Suit.HEARTS))
        player.hit(Card("5", Suit.DIAMONDS))
        game = BlackjackGame(player)
        game.split_player()
        assert len(player.hands) == 2
        assert len(player.hands[0].cards) == 2
        assert len(player.hands[1].cards) == 2


class TestGameGetResult:
    def test_bust_result(self):
        """Test that bust result is returned correctly."""
        player = Player("Alice")
        game = BlackjackGame(player)
        player.hit(Card("K", Suit.HEARTS))
        player.hit(Card("Q", Suit.DIAMONDS))
        player.hit(Card("5", Suit.CLUBS))
        assert game.get_result(0) == "bust"

    def test_win_result_higher_value(self):
        """Test win result when player's hand is higher."""
        player = Player("Alice")
        dealer = Dealer()
        game = BlackjackGame(player)
        game.dealer = dealer
        player.hit(Card("K", Suit.HEARTS))
        player.hit(Card("Q", Suit.DIAMONDS))
        dealer.hit(Card("9", Suit.HEARTS))
        dealer.hit(Card("5", Suit.DIAMONDS))
        assert game.get_result(0) == "win"

    def test_win_result_dealer_bust(self):
        """Test win result when dealer busts."""
        player = Player("Alice")
        dealer = Dealer()
        game = BlackjackGame(player)
        game.dealer = dealer
        player.hit(Card("K", Suit.HEARTS))
        player.hit(Card("9", Suit.DIAMONDS))
        dealer.hit(Card("K", Suit.HEARTS))
        dealer.hit(Card("Q", Suit.DIAMONDS))
        dealer.hit(Card("5", Suit.CLUBS))
        assert game.get_result(0) == "win"

    def test_lose_result(self):
        """Test lose result when dealer's hand is higher."""
        player = Player("Alice")
        dealer = Dealer()
        game = BlackjackGame(player)
        game.dealer = dealer
        player.hit(Card("9", Suit.HEARTS))
        player.hit(Card("5", Suit.DIAMONDS))
        dealer.hit(Card("K", Suit.HEARTS))
        dealer.hit(Card("Q", Suit.DIAMONDS))
        assert game.get_result(0) == "lose"

    def test_push_result(self):
        """Test push result when values are equal."""
        player = Player("Alice")
        dealer = Dealer()
        game = BlackjackGame(player)
        game.dealer = dealer
        player.hit(Card("K", Suit.HEARTS))
        player.hit(Card("Q", Suit.DIAMONDS))
        dealer.hit(Card("J", Suit.HEARTS))
        dealer.hit(Card("10", Suit.DIAMONDS))
        assert game.get_result(0) == "push"


class TestGameNewRound:
    def test_new_round_resets_hands(self):
        """Test that new_round resets hands."""
        player = Player("Alice", bank=100)
        game = BlackjackGame(player)
        player.place_bet(25)
        player.hit(Card("K", Suit.HEARTS))
        game.deal_initial()
        assert len(player.hand.cards) > 0
        game.new_round()
        assert len(player.hand.cards) == 0
        assert player.bet is None
