import time
import pandas as pd
import plotly.express as px
import requests
import streamlit as st

st.set_page_config(page_title="Denver Weather", page_icon="🌡️", layout="wide")
st.markdown("""
    <style>
      [data-testid="stPlotlyChart"], .stPlotlyChart, .stElementContainer {
        transition: none !important;
        opacity: 1 !important;
      }
    </style>
""", unsafe_allow_html=True)

st.title("🌡️ Denver Temperature Over Time (Open-Meteo)")
st.caption("Cached API calls + a rolling history kept in session state.")

lat, lon = 39.7392, -104.9903  # Denver
wurl = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={lat}&longitude={lon}&current=temperature_2m,wind_speed_10m"
)
MAX_POINTS = 50


@st.cache_data(ttl=600, show_spinner=False)
def get_weather():
    """Return (df, error_message). Never raises."""
    try:
        r = requests.get(wurl, timeout=10)
        r.raise_for_status()
        j = r.json()["current"]
        df = pd.DataFrame([{
            "time": pd.to_datetime(j["time"]),
            "temperature": j["temperature_2m"],
            "wind": j["wind_speed_10m"],
        }])
        return df, None
    except (requests.RequestException, KeyError) as e:
        return None, f"Network/API error: {e}"


# ---- Controls ----
refresh_sec = st.slider("Refresh every (sec)", 10, 120, 30)
auto_refresh = st.toggle("Enable auto-refresh", value=False)
if st.button("Refresh now"):
    get_weather.clear()
st.caption(f"Last refreshed at: {time.strftime('%H:%M:%S')}")

# ---- Fetch ----
df, err = get_weather()
if err:
    st.error(err)
    st.stop()

# ---- History in session state (skip duplicate readings from the cache) ----
if "weather_history" not in st.session_state:
    st.session_state.weather_history = []

latest = df.iloc[0].to_dict()
hist_list = st.session_state.weather_history
if not hist_list or hist_list[-1]["time"] != latest["time"]:
    hist_list.append(latest)
st.session_state.weather_history = hist_list[-MAX_POINTS:]

hist = pd.DataFrame(st.session_state.weather_history)

# ---- Metrics + chart ----
c1, c2 = st.columns(2)
c1.metric("Temperature (°C)", f"{latest['temperature']:.1f}")
c2.metric("Wind (km/h)", f"{latest['wind']:.1f}")

fig = px.line(hist, x="time", y="temperature", markers=True,
              title="Denver temperature (°C)",
              labels={"time": "Time", "temperature": "Temperature (°C)"})
st.plotly_chart(fig, use_container_width=True)
st.dataframe(hist, use_container_width=True)

if auto_refresh:
    time.sleep(refresh_sec)
    get_weather.clear()
    st.rerun()
