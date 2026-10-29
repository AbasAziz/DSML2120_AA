import time
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Live API Demo", page_icon="📡", layout="wide")
st.markdown("""
    <style>
      [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer {
        transition: none !important;
        opacity: 1 !important;
      }
    </style>
""", unsafe_allow_html=True)

st.title("📡 Live Data Demo (CoinGecko)")
st.caption("Cached API calls + a rolling history kept in session state.")

# ---- Config ----
COINS = ["bitcoin", "ethereum"]
VS = "usd"
HEADERS = {"User-Agent": "msudenver-dataviz-class/1.0", "Accept": "application/json"}
API_URL = (
    "https://api.coingecko.com/api/v3/simple/price"
    f"?ids={','.join(COINS)}&vs_currencies={VS}"
)
SAMPLE_DF = pd.DataFrame([{"coin": "bitcoin", VS: 68000}, {"coin": "ethereum", VS: 3500}])
MAX_POINTS = 50


# ---- Fetch (cached) ----
@st.cache_data(ttl=300, show_spinner=False)
def fetch_prices(url: str):
    """Return (df, error_message). Never raises."""
    try:
        resp = requests.get(url, timeout=10, headers=HEADERS)
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After", "a bit")
            return None, f"429 Too Many Requests - try again after {retry_after}s"
        resp.raise_for_status()
        df = pd.DataFrame(resp.json()).T.reset_index().rename(columns={"index": "coin"})
        return df, None
    except requests.RequestException as e:
        return None, f"Network/HTTP error: {e}"


# ---- Controls ----
st.subheader("🔁 Auto Refresh Settings")
refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)
auto_refresh = st.toggle("Enable auto-refresh", value=False)
if st.button("Refresh now"):
    fetch_prices.clear()
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# ---- Main view ----
st.subheader("Prices")
df, err = fetch_prices(API_URL)
if err:
    st.warning(f"{err}\nShowing sample data so the demo continues.")
    df = SAMPLE_DF.copy()

st.dataframe(df, use_container_width=True)

cols = st.columns(len(df))
for col, (_, row) in zip(cols, df.iterrows()):
    col.metric(row["coin"].title(), f"${row[VS]:,.2f}")

# ---- History in session state ----
if "history" not in st.session_state:
    st.session_state.history = []

now = pd.Timestamp.now()
for _, row in df.iterrows():
    st.session_state.history.append({"time": now, "coin": row["coin"], VS: row[VS]})
st.session_state.history = st.session_state.history[-MAX_POINTS * len(COINS):]

hist = pd.DataFrame(st.session_state.history)
fig = px.line(hist, x="time", y=VS, color="coin", markers=True,
              title=f"Price history ({VS.upper()})")
st.plotly_chart(fig, use_container_width=True)

# ---- Auto refresh ----
if auto_refresh:
    time.sleep(refresh_sec)
    fetch_prices.clear()
    st.rerun()
