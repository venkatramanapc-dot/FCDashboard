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