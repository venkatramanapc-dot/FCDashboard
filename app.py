import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="FC Basket Dashboard",
    layout="centered"
)

# Refresh every 5 seconds
st_autorefresh(interval=5000, key="refresh")

st.title("FC Basket Dashboard")

symbols = {
    "NIFTY": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "SENSEX": "^BSESN",
    "MIDCAP50": "^NSEMDCP50"
}


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


bull_now = 0
bear_now = 0

continuation_bull = 0
continuation_bear = 0

reversal_bull = 0
reversal_bear = 0

fc_score = 0

strengths = {}

for name, symbol in symbols.items():

    data = yf.Ticker(symbol).history(
        period="1d",
        interval="5m"
    )

    if len(data) < 3:
        continue

    previous = data.iloc[-2]
    current = data.iloc[-1]

    # Previous candle
    prev_open = previous["Open"]
    prev_close = previous["Close"]

    # Current candle
    curr_open = current["Open"]
    curr_close = current["Close"]

    prev_color = "🟢" if prev_close > prev_open else "🔴"
    curr_color = "🟢" if curr_close > curr_open else "🔴"

    # Previous candle force
    prev_pct = ((prev_close - prev_open) / prev_open) * 100

    # Live candle movement
    curr_pct = ((curr_close - curr_open) / curr_open) * 100

    strengths[name] = prev_pct

    # FC Score based on previous candle force
    force = abs(prev_pct)

    if force >= 0.20:
        fc_score += 3
    elif force >= 0.10:
        fc_score += 2
    elif force >= 0.05:
        fc_score += 1

    # Current candle direction counts
    if curr_pct > 0:
        bull_now += 1
    elif curr_pct < 0:
        bear_now += 1

    # Sync calculations
    if prev_color == "🟢" and curr_color == "🟢":
        continuation_bull += 1

    if prev_color == "🔴" and curr_color == "🔴":
        continuation_bear += 1

    if prev_color == "🔴" and curr_color == "🟢":
        reversal_bull += 1

    if prev_color == "🟢" and curr_color == "🔴":
        reversal_bear += 1

    st.markdown(
        f"### {name}  {prev_color} → {curr_color}"
    )

    st.write(
        f"💪 Force: {prev_pct:+.2f}% {strength_icon(prev_pct)}"
    )

    st.write(
        f"📈 Live: {curr_pct:+.2f}%"
    )

st.divider()

leader = max(strengths, key=lambda x: abs(strengths[x]))

if continuation_bull == 4:
    st.success("🟢 CONTINUATION BULL SYNC 4/4")

elif continuation_bear == 4:
    st.error("🔴 CONTINUATION BEAR SYNC 4/4")

elif reversal_bull == 4:
    st.success("🚀 REVERSAL TO BULL SYNC 4/4")

elif reversal_bear == 4:
    st.error("⚠️ REVERSAL TO BEAR SYNC 4/4")

elif bull_now == 4:
    st.success("🟢 CURRENT BULLISH SYNC 4/4")

elif bear_now == 4:
    st.error("🔴 CURRENT BEARISH SYNC 4/4")

else:
    st.warning(
        f"Mixed Market | Bulls: {bull_now}/4 | Bears: {bear_now}/4"
    )

st.subheader(
    f"Leader: {leader} ({strengths[leader]:+.2f}%)"
)

st.subheader(
    f"FC Score: {fc_score}/12"
)

if fc_score >= 8:
    st.success("🟢 STRONG FC")

elif fc_score >= 5:
    st.warning("🟡 MODERATE FC")

else:
    st.error("🔴 WEAK FC")

st.caption(
    "Force = Previous Candle % Movement | Live = Current Candle % Movement"
)
import requests

BOT_TOKEN = "8679603347:AAG2aWK6d8vrgrEjpnJ08_BX1v9Q9ZKYs6c"
CHAT_ID = "8851923121"

def send_telegram_alert(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)


if st.button("Send Test Alert"):
    send_telegram_alert(
        "🎯 TEST ALERT\nLCC Engine Connected"
    )
    st.success("Alert Sent")
    import requests

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
# ALERT MEMORY
# ==========================

if "lcc_alert_sent" not in st.session_state:
    st.session_state.lcc_alert_sent = False


# ==========================
# LCC CONDITIONS
# ==========================

leader_force = abs(strengths[leader])

lcc_signal = (
    fc_score > 6
    and (
        continuation_bull >= 3
        or continuation_bear >= 3
    )
    and leader_force >= 0.10
)

# ==========================
# TELEGRAM ALERT
# ==========================

if lcc_signal and not st.session_state.lcc_alert_sent:

    if continuation_bull >= 3:

        send_telegram_alert(
            f"""
🎯 LCC LONG READY

FC Score: {fc_score}/12
Leader: {leader}
Force: {strengths[leader]:+.2f}%
Bull Sync: {continuation_bull}/4
"""
        )

    elif continuation_bear >= 3:

        send_telegram_alert(
            f"""
🎯 LCC SHORT READY

FC Score: {fc_score}/12
Leader: {leader}
Force: {strengths[leader]:+.2f}%
Bear Sync: {continuation_bear}/4
"""
        )

    st.session_state.lcc_alert_sent = True

    st.success("🎯 Telegram Alert Sent")

# ==========================
# RESET
# ==========================

if not lcc_signal:

    st.session_state.lcc_alert_sent = False

    st.info("Waiting for next LCC setup")
    st.subheader("LCC Status")

if fc_score <= 6:
    st.warning("❌ FC below threshold")

elif abs(strengths[leader]) < 0.10:
    st.warning("❌ Leader not strong enough")

elif continuation_bull >= 3:
    st.success("🟢 LCC LONG READY")

elif continuation_bear >= 3:
    st.success("🔴 LCC SHORT READY")

else:
    st.info("⏳ Waiting for continuation sync")