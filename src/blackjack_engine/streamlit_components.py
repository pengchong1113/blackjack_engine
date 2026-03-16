import streamlit as st
import base64, os
from blackjack_engine.player import Player
from blackjack_engine.game import BlackjackGame

st.set_page_config(page_title="Blackjack", layout="wide")

# Load background image
bg_path = os.path.join(os.path.dirname(__file__), "bg.png")
with open(bg_path, "rb") as f:
    bg_data = base64.b64encode(f.read()).decode()

# Compact CSS + background
st.markdown(f"""<style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_data}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(255,255,255,0.85);
        z-index: 0;
    }}
    .block-container {{padding-top:3rem;padding-bottom:0rem;position:relative;z-index:1;}}
    h1 {{margin-bottom:0 !important;}}
    .stImage {{margin-bottom:0 !important;}}
    div[data-testid="stHorizontalBlock"] {{gap:0.3rem;}}
    div[data-testid="column"] {{padding:0 0.2rem;}}
</style>""", unsafe_allow_html=True)

CARD_W = 80


def init_session_state():
    defaults = {
        "game": None,
        "player": Player("You", 100.0),
        "game_started": False,
        "round_active": False,
        "showing_result": False,
        "current_hand": 0,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def render_header():
    h1, h2, h3 = st.columns([3, 2, 1])
    h1.title("🃏 Blackjack")
    h2.metric("Balance", f"${st.session_state.player.bank:.2f}", label_visibility="visible")
    h2.caption(f"Player: {st.session_state.player.name}")
    if h3.button("New Game", use_container_width=True):
        st.session_state.player = Player("You", 100.0)
        st.session_state.game = BlackjackGame(st.session_state.player)
        st.session_state.game_started = True
        st.session_state.round_active = False
        st.session_state.showing_result = False
        st.session_state.current_hand = 0
        st.rerun()
    st.divider()


def render_bet_controls(game: BlackjackGame, player: Player):
    if st.session_state.round_active or st.session_state.showing_result:
        return

    if player.bank <= 0:
        st.error("You are out of money. Click 'New Game' to start over.")
        return

    c1, c2, c3 = st.columns([2, 1, 1])
    bet = c1.number_input(
        "Bet:",
        min_value=0.0,
        max_value=player.bank,
        step=1.0,
        label_visibility="collapsed",
    )
    place_bet = c2.button("Place Bet", use_container_width=True)
    all_in = c3.button("All In", use_container_width=True)
    if place_bet or all_in:
        try:
            game.new_round()
            st.session_state.current_hand = 0
            player.place_bet(player.bank if all_in else bet)
            game.deal_initial()
            st.session_state.round_active = True
            st.rerun()
        except ValueError as e:
            st.error(str(e))


def render_round(game: BlackjackGame, player: Player):
    if not st.session_state.round_active:
        return

    hi = st.session_state.current_hand
    num_hands = len(player.hands)

    dealer_col, _ = st.columns([3, 1])
    show_cards_inline(dealer_col, [game.dealer_upcard] if game.dealer_upcard else [], "Dealer")
    dealer_col.write(f"**Value:** {game.dealer_upcard.value() if game.dealer_upcard else '?'}")

    st.divider()

    for i, hand in enumerate(player.hands):
        is_current = i == hi
        label = f"Hand {i + 1}" if num_hands > 1 else "Your Hand"
        if is_current and num_hands > 1:
            label += "  ◀"

        hand_col, btn_col = st.columns([3, 1])
        show_cards_inline(hand_col, hand.cards, label)
        hand_col.write(f"**Value:** {hand.value()}")

        if is_current and not hand.is_bust():
            is_first_action = len(hand.cards) == 2
            can_double = is_first_action and player.bets[i] is not None and player.bank >= player.bets[i]
            can_split = is_first_action and num_hands == 1 and player.can_split()

            with btn_col:
                st.markdown("&nbsp;", unsafe_allow_html=True)
                if st.button("Hit", use_container_width=True, key=f"hit_{i}"):
                    game.hit_player(i)
                    if hand.is_bust():
                        if hi + 1 < num_hands:
                            st.session_state.current_hand = hi + 1
                        else:
                            game.stand_player()
                            st.session_state.round_active = False
                            st.session_state.showing_result = True
                    st.rerun()

                if st.button("Stand", use_container_width=True, key=f"stand_{i}"):
                    if hi + 1 < num_hands:
                        st.session_state.current_hand = hi + 1
                    else:
                        game.stand_player()
                        st.session_state.round_active = False
                        st.session_state.showing_result = True
                    st.rerun()

                if can_double and st.button("Double", use_container_width=True, key=f"dbl_{i}"):
                    game.double_down(i)
                    if hi + 1 < num_hands:
                        st.session_state.current_hand = hi + 1
                    else:
                        game.stand_player()
                        st.session_state.round_active = False
                        st.session_state.showing_result = True
                    st.rerun()

                if can_split and st.button("Split", use_container_width=True, key=f"split_{i}"):
                    game.split_player()
                    st.session_state.current_hand = 0
                    st.rerun()

        if i < num_hands - 1:
            st.divider()


def render_results(game: BlackjackGame, player: Player):
    if not st.session_state.showing_result:
        return

    show_cards_inline(st.container(), game.dealer.hand.cards, "Dealer Hand")
    st.write(f"**Value:** {game.dealer.hand.value()}")
    st.divider()

    num_hands = len(player.hands)
    for i, hand in enumerate(player.hands):
        label = f"Hand {i + 1}" if num_hands > 1 else "Your Hand"
        res_hand_col, res_btn_col = st.columns([3, 1])
        show_cards_inline(res_hand_col, hand.cards, label)
        res_hand_col.write(f"**Value:** {hand.value()}")

        result = game.get_result(i)
        msg = {
            "bust": ("Busted!", "error"),
            "win": ("Win!", "success"),
            "push": ("Push!", "info"),
        }.get(result, ("Lose!", "error"))

        with res_hand_col:
            getattr(st, msg[1])(msg[0])

        if i == num_hands - 1:
            with res_btn_col:
                st.markdown("&nbsp;", unsafe_allow_html=True)
                if st.button("Continue to Next Round", use_container_width=True):
                    st.session_state.showing_result = False
                    st.rerun()

def show_cards_inline(container, cards, label=""):
    with container:
        if label:
            st.markdown(f"**{label}**")
        if cards:
            cols = st.columns(min(len(cards), 8))
            for col, card in zip(cols, cards):
                col.image(card.image_path(), width=CARD_W)

def st_blackjack_dashboard():
    init_session_state()
    render_header()

    if st.session_state.game_started:
        game = st.session_state.game
        player = st.session_state.player
        render_bet_controls(game, player)
        render_round(game, player)
        render_results(game, player)

# we call the function
# st_blackjack_dashboard()
