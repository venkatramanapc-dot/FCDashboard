import streamlit as st
import yfinance as yf
import requests
from streamlit_autorefresh import st_autorefresh

# ==========================
# PAGE CONFIG
# ==========================

st.set_page_config(
    page_title="LCC Dashboard",
    layout="centered"
)

st_autorefresh(interval=5000, key="refresh")

st.title("LCC Dashboard")

# ==========================
# TELEGRAM SETTINGS
# ==========================

BOT_TOKEN = "8679603347:AAG2aWK6d8vrgrEjpnJ08_BX1v9Q9ZKYs6c"
CHAT_ID = "8851923121"

def send_telegram_alert(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)

# ==========================
# THREE INDEX BASKET
# ==========================

symbols = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN"
}

# ==========================
# STRENGTH ICON
# ==========================

def strength_icon(move):

    move = abs(move)

    if move >= 0.20:
        return "🔥"

    elif move >= 0.10:
        return "💪"

    elif move >= 0.05:
        return "🟡"

    else:
        return "⚪"

# ==========================
# VARIABLES
# ==========================

bull_now = 0
bear_now = 0

continuation_bull = 0
continuation_bear = 0

reversal_bull = 0
reversal_bear = 0

basket_strength = 0

strengths = {}

# ==========================
# DATA COLLECTION
# ==========================

for name, symbol in symbols.items():

    try:

        data = yf.Ticker(symbol).history(
            period="1d",
            interval="5m"
        )

        if len(data) < 3:
            continue

        previous = data.iloc[-2]
        current = data.iloc[-1]

        prev_open = previous["Open"]
        prev_close = previous["Close"]

        curr_open = current["Open"]
        curr_close = current["Close"]

        prev_color = "🟢" if prev_close > prev_open else "🔴"
        curr_color = "🟢" if curr_close > curr_open else "🔴"

        prev_pct = (
            (prev_close - prev_open)
            / prev_open
        ) * 100

        curr_pct = (
            (curr_close - curr_open)
            / curr_open
        ) * 100

        strengths[name] = prev_pct

        force = abs(prev_pct)

        # Basket Strength Score

        if force >= 0.20:
            basket_strength += 3

        elif force >= 0.10:
            basket_strength += 2

        elif force >= 0.05:
            basket_strength += 1

        # Live Direction

        if curr_pct > 0:
            bull_now += 1

        elif curr_pct < 0:
            bear_now += 1

        # Continuation

        if prev_color == "🟢" and curr_color == "🟢":
            continuation_bull += 1

        if prev_color == "🔴" and curr_color == "🔴":
            continuation_bear += 1

        # Reversal

        if prev_color == "🔴" and curr_color == "🟢":
            reversal_bull += 1

        if prev_color == "🟢" and curr_color == "🔴":
            reversal_bear += 1

        # Display

        st.markdown(
            f"### {name} {prev_color} → {curr_color}"
        )

        st.write(
            f"💪 Force: {prev_pct:+.2f}% {strength_icon(prev_pct)}"
        )

        st.write(
            f"📈 Live: {curr_pct:+.2f}%"
        )

    except:
        st.warning(f"{name} data unavailable")

# ==========================
# SAFETY CHECK
# ==========================

if len(strengths) == 0:

    st.error("No market data available")

    st.stop()

# ==========================
# LEADER
# ==========================

leader = max(
    strengths,
    key=lambda x: abs(strengths[x])
)

leader_force = abs(
    strengths[leader]
)

# ==========================
# MARKET STATUS
# ==========================

st.divider()

if continuation_bull == 3:

    st.success(
        "🟢 CONTINUATION BULL SYNC 3/3"
    )

elif continuation_bear == 3:

    st.error(
        "🔴 CONTINUATION BEAR SYNC 3/3"
    )

elif reversal_bull == 3:

    st.success(
        "🚀 REVERSAL TO BULL SYNC 3/3"
    )

elif reversal_bear == 3:

    st.error(
        "⚠️ REVERSAL TO BEAR SYNC 3/3"
    )

elif bull_now == 3:

    st.success(
        "🟢 CURRENT BULLISH SYNC 3/3"
    )

elif bear_now == 3:

    st.error(
        "🔴 CURRENT BEARISH SYNC 3/3"
    )

else:

    st.warning(
        f"Mixed Market | Bulls: {bull_now}/3 | Bears: {bear_now}/3"
    )

# ==========================
# LEADER & STRENGTH
# ==========================

st.subheader(
    f"Leader: {leader} ({strengths[leader]:+.2f}%)"
)

st.subheader(
    f"Basket Strength: {basket_strength}/9"
)

if basket_strength >= 6:

    st.success(
        "🟢 STRONG LCC ENVIRONMENT"
    )

elif basket_strength >= 4:

    st.warning(
        "🟡 MODERATE LCC ENVIRONMENT"
    )

else:

    st.error(
        "🔴 WEAK LCC ENVIRONMENT"
    )

# ==========================
# TEST TELEGRAM ALERT
# ==========================

if st.button("Send Test Alert"):

    send_telegram_alert(
        "🎯 TEST ALERT\nLCC Engine Connected"
    )

    st.success("Alert Sent")

# ==========================
# ALERT MEMORY
# ==========================

# ==========================
# ALERT MEMORY
# ==========================

if "lcc_alert_sent" not in st.session_state:

    st.session_state.lcc_alert_sent = False
    if "last_lcc_alert" not in st.session_state:
     st.session_state.last_lcc_alert = 0
# ==========================
# LCC LEVEL ALERTS
# ==========================

if basket_strength >= 4 and st.session_state.last_lcc_alert < 4:

    send_telegram_alert(
        f"🟡 LCC = 4\n\nLeader: {leader}\nForce: {strengths[leader]:+.2f}%"
    )

    st.session_state.last_lcc_alert = 4

if basket_strength >= 5 and st.session_state.last_lcc_alert < 5:

    send_telegram_alert(
        f"🟠 LCC = 5\n\nLeader: {leader}\nForce: {strengths[leader]:+.2f}%"
    )

    st.session_state.last_lcc_alert = 5

if basket_strength >= 6 and st.session_state.last_lcc_alert < 6:

    send_telegram_alert(
        f"🟢 LCC = 6\n\nLeader: {leader}\nForce: {strengths[leader]:+.2f}%"
    )

    st.session_state.last_lcc_alert = 6

if basket_strength >= 7 and st.session_state.last_lcc_alert < 7:

    send_telegram_alert(
        f"🔥 LCC = 7\n\nLeader: {leader}\nForce: {strengths[leader]:+.2f}%"
    )

    st.session_state.last_lcc_alert = 7
# ==========================
# LCC SIGNAL LOGIC
# ==========================

lcc_signal = (

    basket_strength >= 6

    and

    (
        continuation_bull == 3
        or
        continuation_bear == 3
    )

    and

    leader_force >= 0.10
)

# ==========================
# TELEGRAM ALERTS
# ==========================

if lcc_signal and not st.session_state.lcc_alert_sent:

    if continuation_bull == 3:

        send_telegram_alert(
            f"""
🎯 LCC LONG READY

Basket Strength: {basket_strength}/9

Leader: {leader}

Leader Force: {strengths[leader]:+.2f}%

Bull Continuation Sync: {continuation_bull}/3
"""
        )

    elif continuation_bear == 3:

        send_telegram_alert(
            f"""
🎯 LCC SHORT READY

Basket Strength: {basket_strength}/9

Leader: {leader}

Leader Force: {strengths[leader]:+.2f}%

Bear Continuation Sync: {continuation_bear}/3
"""
        )

    st.session_state.lcc_alert_sent = True

    st.success(
        "🎯 Telegram Alert Sent"
    )

# ==========================
# RESET ALERT
# ==========================

if not lcc_signal:

    st.session_state.lcc_alert_sent = False
# ==========================
# LCC STATUS PANEL
# ==========================

st.divider()

st.subheader("LCC Status")

if basket_strength < 6:

    st.warning(
        "❌ Basket Strength below threshold"
    )

elif leader_force < 0.10:

    st.warning(
        "❌ Leader Force below 0.10%"
    )

elif continuation_bull == 3:

    st.success(
        "🟢 LCC LONG READY"
    )

elif continuation_bear == 3:

    st.success(
        "🔴 LCC SHORT READY"
    )

else:

    st.info(
        "⏳ Waiting for full continuation sync"
    )

# ==========================
# DASHBOARD FOOTER
# ==========================

st.divider()

st.caption(
    "Basket = NIFTY + BANKNIFTY + SENSEX | "
    "Force = Previous Candle % Move | "
    "Live = Current Candle % Move"
)