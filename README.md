# blackjack_engine

A Python library that provides a complete blackjack game engine.

The library models all the core elements of a blackjack game — cards, deck, hand scoring, player actions (hit, stand, split, double down), dealer behavior, and round resolution — as importable Python classes. It also ships a Streamlit UI component for browser-based play.

## Installation

Install from TestPyPI:

```bash
pip install -i https://test.pypi.org/simple/ blackjack-engine
```

## API Reference

### `Suit`

An `Enum` with four members: `HEARTS`, `DIAMONDS`, `CLUBS`, `SPADES`. Used to identify the suit of a `Card`.

### `Card`

Represents a single immutable playing card. Cards are hashable and support equality comparison, so they can be stored in sets or used as dict keys.

| Method | Description |
|---|---|
| `value()` | Blackjack point value — number cards face value, J/Q/K = 10, Ace = 11 |
| `display()` | Short display string with suit symbol, e.g. `A♠`, `10♦` |
| `image_path()` | Absolute path to the card's PNG image file |

### `Deck`

A standard 52-card deck (all ranks × all suits).

| Method | Description |
|---|---|
| `reset()` | Refills the deck with all 52 cards |
| `shuffle()` | Shuffles the deck in place |
| `draw()` | Removes and returns the top card |
| `len(deck)` | Number of cards remaining |

### `Hand`

Tracks the cards in one hand and computes the blackjack score with correct soft/hard ace logic.

| Method | Description |
|---|---|
| `add_card(card)` | Adds a `Card` to the hand |
| `value()` | Best score <= 21; aces automatically counted as 1 or 11 |
| `is_bust()` | `True` if hand value exceeds 21 |

### `Player`

A human player with a name, a bank balance, and one or more hands (multiple hands arise after a split).

| Method / Property | Description |
|---|---|
| `place_bet(amount)` | Deducts `amount` from the bank and records the bet |
| `hit(card, hand_idx=0)` | Adds a card to the specified hand |
| `can_split()` | `True` when the first two cards have equal value and there is enough bank balance |
| `split()` | Splits the hand into two, placing a second equal bet from the bank |
| `double_down(hand_idx=0)` | Doubles the bet for the given hand |
| `reset_hand()` | Clears all hands and bets ready for the next round |
| `hand` *(property)* | Shortcut to `hands[0]` |
| `bet` *(property)* | Shortcut to `bets[0]` |

### `Dealer`

Subclass of `Player` that enforces the standard house rule.

| Method | Description |
|---|---|
| `should_hit()` | `True` while hand value is below 17 |

### `BlackjackGame`

Orchestrates a complete round: dealing, player actions, dealer play, and bet settlement.

| Method | Description |
|---|---|
| `deal_initial()` | Deals two cards to the player and two to the dealer (one face-up) |
| `hit_player()` | Draws a card for the player |
| `stand_player()` | Ends the player's turn and runs the dealer's hand to completion |
| `double_down()` | Doubles the player's bet and draws exactly one more card |
| `split_player()` | Splits the player's pair into two independent hands |
| `get_result()` | Returns the round outcome: `"blackjack"`, `"win"`, `"lose"`, or `"push"` |
| `new_round()` | Resets player and dealer hands for the next round |

## Usage Example

The example below plays a full round programmatically: deal, inspect hands, take an action, then resolve.

```python
from blackjack_engine.player import Player
from blackjack_engine.game import BlackjackGame

player = Player("Alice", bank=100.0)
game = BlackjackGame(player)

# --- Round start ---
player.place_bet(10.0)
game.deal_initial()

print(f"Dealer shows : {game.dealer_upcard.display()}")
print(f"Your hand    : {[c.display() for c in player.hand.cards]}  (value: {player.hand.value()})")

# --- Player action ---
if player.hand.value() <= 16:
    game.hit_player()
    print(f"Hit! New hand : {[c.display() for c in player.hand.cards]}  (value: {player.hand.value()})")

if player.hand.is_bust():
    print("Bust! You lose.")
else:
    game.stand_player()
    dealer_hand = game.dealer.hand
    print(f"Dealer final : {[c.display() for c in dealer_hand.cards]}  (value: {dealer_hand.value()})")
    print(f"Result       : {game.get_result()}")
    print(f"Bank balance : ${player.bank:.2f}")
```

Example output:

```
Dealer shows : 7♣
Your hand    : ['K♠', '9♦']  (value: 19)
Dealer final : ['7♣', 'Q♥']  (value: 17)
Result       : win
Bank balance : $110.00
```
This is a minimal example to demonstrate the core API. In practice you can build on top of these classes in many ways — for example, adding a command-line interface with `input()` to let a real player choose hit/stand/double/split each turn, or building a full browser-based UI with Streamlit using the included `streamlit_components` module. The engine handles all game logic; the presentation layer is entirely up to you.
## Project Layout

```text
blackjack_engine/
├── pyproject.toml
├── uv.lock
├── README.md
├── src/
│   └── blackjack_engine/
│       ├── __init__.py
│       ├── card.py
│       ├── deck.py
│       ├── hand.py
│       ├── player.py
│       ├── game.py
│       ├── streamlit_components.py
│       ├── bg.png
│       ├── cards/
│       └── py.typed
└── tests/
    ├── test_card.py
    ├── test_deck.py
    ├── test_hand.py
    ├── test_player.py
    └── test_game.py
```

## Development

This section is for contributors who want to work on the library locally.

Requirements: Python 3.9+, [uv](https://docs.astral.sh/uv/)

### Setup

Clone the repository and install all dependencies (including dev dependencies such as pytest) into an isolated virtual environment:

```bash
git clone https://github.com/pengchong1113/blackjack_engine.git
cd blackjack_engine
uv venv
uv sync
```

`uv sync` reads `uv.lock` and installs every dependency at the exact pinned version, ensuring a reproducible environment across machines.

### Run Tests

Run the full test suite (96 tests):

```bash
uv run pytest -q
```

To run a single test file:

```bash
uv run pytest tests/test_game.py -v
```

Tests are organised by module under `tests/` and cover all public classes and edge cases such as soft-ace scoring, splitting, double-down, and bust resolution.

### Run Streamlit UI

Launch the built-in Streamlit UI for manual play in a browser:

```bash
uv run streamlit run src/blackjack_engine/streamlit_components.py
```

This starts a local dev server (default: http://localhost:8501) and hot-reloads on file changes, which is useful when iterating on the UI.

