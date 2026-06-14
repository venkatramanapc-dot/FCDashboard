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

bull_now = 0
bear_now = 0

continuation_bull = 0
continuation_bear = 0

reversal_bull = 0
reversal_bear = 0

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

    pct = ((curr_close - curr_open) / curr_open) * 100

    strengths[name] = pct

    if pct > 0:
        bull_now += 1
    elif pct < 0:
        bear_now += 1

    if prev_color == "🟢" and curr_color == "🟢":
        continuation_bull += 1

    if prev_color == "🔴" and curr_color == "🔴":
        continuation_bear += 1

    if prev_color == "🔴" and curr_color == "🟢":
        reversal_bull += 1

    if prev_color == "🟢" and curr_color == "🔴":
        reversal_bear += 1

    st.markdown(
        f"### {name}   {prev_color} → {curr_color}   ({pct:+.2f}%)"
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

st.caption(
    "Previous Candle → Current Candle | Current candle % movement"
)