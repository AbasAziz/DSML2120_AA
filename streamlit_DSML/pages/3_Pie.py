from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "pie_demo.csv"

st.title("Programming Language Usage")
df = pd.read_csv(DATA_PATH)

hole = st.slider("Donut hole size", 0.0, 0.8, 0.0, 0.05)
fig = px.pie(df, names="category", values="value", hole=hole,
             title="Share of Time Spent per Language")
st.plotly_chart(fig, use_container_width=True)
