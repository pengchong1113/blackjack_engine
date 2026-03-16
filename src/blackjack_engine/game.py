from .card import Card
from .deck import Deck
from .player import Player, Dealer


class BlackjackGame:
    def __init__(self, player: Player):
        """Initialize a new blackjack game with a shuffled deck, the given
        player, and a fresh dealer. Sets the dealer upcard to None until
        the initial deal.

        Args:
            player (Player): The player participating in this game.

        Returns:
            None
        """
        self.deck = Deck()
        self.deck.shuffle()
        self.player = player
        self.dealer = Dealer()
        self.dealer_upcard = None

    def deal_initial(self):
        """Deal the opening cards for a round of blackjack. The dealer
        receives a hole card (face down), the player receives two cards,
        and the dealer receives an upcard (face up). Stores the dealer's
        upcard for reference.

        Returns:
            None
        """
        # Dealer gets hole card (face down)
        self.dealer.hit(self.deck.draw())
        # Player gets two cards
        self.player.hit(self.deck.draw())
        self.player.hit(self.deck.draw())
        # Dealer gets upcard (face up)
        self.dealer.hit(self.deck.draw())
        self.dealer_upcard = self.dealer.hand.cards[-1]

    # --- Terminal play methods ---

    def _play_hand(self, p, hand_idx, label=""):
        """Play a single hand interactively via terminal input. Prompts the
        player to hit, stand, double down, or split until the hand is
        resolved. Returns "split" if the player chose to split, otherwise
        returns "done".

        Args:
            p (Player): The player whose hand is being played.
            hand_idx (int): Index of the hand to play in the player's
                            hands list.
            label (str): Display prefix for terminal output messages.

        Returns:
            str: "split" if the player split, "done" otherwise.
        """
        hand = p.hands[hand_idx]
        bet = p.bets[hand_idx]
        first_action = True
        while True:
            if hand.is_bust():
                print(f"{label}Busts!")
                break
            can_double = first_action and bet is not None and bet <= p.bank
            can_split_now = (first_action and len(p.hands) == 1
                             and p.can_split())
            options = "Hit, stand"
            if can_double:
                options += ", double"
            if can_split_now:
                options += ", split"
            options += "? "
            action = input(f"""{label}Hand {hand.cards} value {hand.value()}.
                           {options}""")
            a = action.lower()
            if a.startswith("sp") and can_split_now:
                p.split()
                # Deal one card to each split hand
                p.hands[0].add_card(self.deck.draw())
                p.hands[1].add_card(self.deck.draw())
                print(f"""Split! Hand 1: {p.hands[0].cards},
                      Hand 2: {p.hands[1].cards}""")
                return "split"
            elif a.startswith("d") and can_double:
                p.double_down(hand_idx)
                card = self.deck.draw()
                p.hit(card, hand_idx)
                print(f"{label}Doubled down! Drew: {card}")
                if hand.is_bust():
                    print(f"{label}Busts!")
                break
            elif a.startswith("h"):
                card = self.deck.draw()
                p.hit(card, hand_idx)
                print(f"{label}Drew: {card}")
                first_action = False
            else:
                break
        return "done"

    def play_round(self):
        """Execute a full round of blackjack: deal initial cards, let the
        player act on each hand (including splits), then let the dealer
        play if any player hand is still active. Resolves bets at the end.

        Returns:
            None
        """
        self.deal_initial()
        p = self.player
        result = self._play_hand(p, 0, f"{p.name}, ")
        if result == "split":
            for i in range(len(p.hands)):
                print(f"\n--- Hand {i + 1} ---")
                self._play_hand(p, i, f"Hand {i + 1}: ")
        # Dealer plays if any hand is still in
        any_alive = any(not h.is_bust() for h in p.hands)
        if any_alive:
            while self.dealer.should_hit():
                self.dealer.hit(self.deck.draw())
        self.resolve()

    def play_game(self):
        """Run the main game loop, playing rounds until the player chooses
        to quit or runs out of money. Handles betting prompts, deck
        reshuffling when cards run low, and round resets between hands.

        Returns:
            None
        """
        p = self.player
        while True:
            if len(self.deck) < 20:
                self.deck.reset()
                self.deck.shuffle()
                print("Deck reshuffled.")

            if p.bank <= 0:
                print("You are out of money. Game over.")
                break

            while True:
                try:
                    print(f"{p.name}, your balance: ${p.bank:.2f}")
                    bet = float(input("How much do you want to bet? "))
                    p.place_bet(bet)
                    break
                except ValueError as e:
                    print(f"Invalid bet: {e}")

            self.play_round()

            p.reset_hand()
            self.dealer.reset_hand()
            self.dealer_upcard = None

            if input("Play another round? (y/n) ").lower().startswith("n"):
                break

    # --- Step-by-step methods for UI ---

    def hit_player(self, hand_idx: int = 0) -> Card:
        """Draw a card from the deck and add it to the specified player
        hand. Used by UI-driven gameplay for the "hit" action.

        Args:
            hand_idx (int): Index of the hand to hit. Defaults to 0.

        Returns:
            Card: The card that was drawn and added to the hand.
        """
        card = self.deck.draw()
        self.player.hit(card, hand_idx)
        return card

    def double_down(self, hand_idx: int = 0) -> Card:
        """Double the player's bet on the specified hand and deal exactly
        one additional card. The player cannot act further on this hand
        after doubling down.

        Args:
            hand_idx (int): Index of the hand to double down on. Defaults to 0.

        Returns:
            Card: The card that was drawn and added to the hand.
        """
        self.player.double_down(hand_idx)
        card = self.deck.draw()
        self.player.hit(card, hand_idx)
        return card

    def split_player(self):
        """Split the player's current hand into two separate hands and
        deal one additional card to each new hand. The player must have
        a splittable pair for this to be valid.

        Returns:
            None
        """
        self.player.split()
        self.player.hands[0].add_card(self.deck.draw())
        self.player.hands[1].add_card(self.deck.draw())

    def stand_player(self):
        """End the player's turn and execute the dealer's play. The dealer
        draws cards according to house rules if any player hand has not
        busted, then settles all bets.

        Returns:
            None
        """
        any_alive = any(not h.is_bust() for h in self.player.hands)
        if any_alive:
            while self.dealer.should_hit():
                self.dealer.hit(self.deck.draw())
        self._settle_bets()

    def get_result(self, hand_idx: int = 0) -> str:
        """Determine the outcome of a specific player hand compared to the
        dealer's hand. Checks for bust first, then compares hand values
        to decide win, loss, or push.

        Args:
            hand_idx (int): Index of the player hand to evaluate.
            Defaults to 0.

        Returns:
            str: One of "win", "lose", "push", or "bust".
        """
        hand = self.player.hands[hand_idx]
        if hand.is_bust():
            return "bust"
        dealer_value = self.dealer.hand.value()
        player_value = hand.value()
        if dealer_value > 21 or player_value > dealer_value:
            return "win"
        if player_value == dealer_value:
            return "push"
        return "lose"

    def new_round(self):
        """Reset both the player's and dealer's hands and clear the dealer
        upcard. If the deck has fewer than 20 cards remaining, reset and
        reshuffle it to ensure enough cards for the next round.

        Returns:
            None
        """
        self.player.reset_hand()
        self.dealer.reset_hand()
        self.dealer_upcard = None
        if len(self.deck) < 20:
            self.deck.reset()
            self.deck.shuffle()

    def _settle_bets(self):
        """Iterate over all player hands and adjust the player's bank
        based on each hand's result. Wins pay 2x the bet, pushes return
        the original bet, and losses forfeit the bet.

        Returns:
            None
        """
        for i, bet in enumerate(self.player.bets):
            if bet is None:
                continue
            result = self.get_result(i)
            if result == "win":
                self.player.bank += bet * 2
            elif result == "push":
                self.player.bank += bet

    def resolve(self):
        """Resolve the round by comparing each player hand against the
        dealer's hand. Prints results to the terminal and updates the
        player's bank accordingly (wins pay 2x, pushes return the bet).

        Returns:
            None
        """
        dealer_value = self.dealer.hand.value()
        p = self.player
        print(f"Dealer has {self.dealer.hand.cards} value {dealer_value}")
        for i, hand in enumerate(p.hands):
            val = hand.value()
            bet = p.bets[i]
            label = f"Hand {i + 1}: " if len(p.hands) > 1 else ""
            if hand.is_bust():
                pass
            elif dealer_value > 21 or val > dealer_value:
                if bet is not None:
                    print(f"{label}{p.name} wins! +${bet:.2f}")
                else:
                    print(f"{label}{p.name} wins!")
                if bet is not None:
                    p.bank += bet * 2
            elif val == dealer_value:
                if bet is not None:
                    print(f"{label}{p.name} pushes. +${bet:.2f}")
                else:
                    print(f"{label}{p.name} pushes.")
                if bet is not None:
                    p.bank += bet
            else:
                print(f"{label}{p.name} loses.")
