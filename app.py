import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------------- TOP BAR ----------------
left, right = st.columns([6, 1])

with right:
    dark_mode = st.toggle("🌙", value=True)

# ---------------- THEME SETTINGS ----------------
if dark_mode:
    bg_color = "#0e1117"
    text_color = "white"
    plotly_template = "plotly_dark"
else:
    bg_color = "white"
    text_color = "black"
    plotly_template = "plotly_white"

# Inject text + background styling
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        h1, h2, h3, h4, h5, h6, p, div, label {{
            color: {text_color} !important;
        }}
        .stPlotlyChart {{
            color: {text_color};
        }}
        .stMarkdown {{
            color: {text_color};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- TITLE ----------------
st.markdown(f"<h1 style='text-align: center;'>{'Air Aware'}</h1>", unsafe_allow_html=True)
st.markdown(
    f"<p style='text-align: center; font-size:18px;'>A simple dashboard tracking PM2.5 levels and air quality status.</p>",
    unsafe_allow_html=True
)

# ---------------- LOAD DATA ----------------
DATA_PATH = os.path.join("data", "cleaned_air_data.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    for c in df.columns:
        if "pm2" in c.lower():
            df.rename(columns={c: "PM2.5"}, inplace=True)
            break

    df["PM2.5"] = pd.to_numeric(df["PM2.5"], errors="coerce")
    return df

if not os.path.exists(DATA_PATH):
    st.error(f"❌ Missing required file: {DATA_PATH}")
    st.stop()

df = load_data(DATA_PATH)

st.markdown(f"**Total Records:** {len(df):,}")

# ---------------- CHART SECTION ----------------
col1, col2 = st.columns((2, 1))

# -------- Line Chart --------
with col1:
    st.subheader("PM2.5 Trend")
    fig1 = px.line(df, x="Timestamp", y="PM2.5", color="City", template=plotly_template)
    fig1.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font_color=text_color,
    )
    st.plotly_chart(fig1, use_container_width=True)

# -------- Histogram --------
with col2:
    st.subheader("PM2.5 Histogram")
    fig2 = px.histogram(df, x="PM2.5", nbins=30, template=plotly_template)
    fig2.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font_color=text_color,
    )
    st.plotly_chart(fig2, use_container_width=True)

# -------- Pie Chart --------
def categorize(x):
    if pd.isna(x):
        return None
    if x <= 30:
        return "Good"
    elif x <= 60:
        return "Moderate"
    return "Poor"

df["Category"] = df["PM2.5"].apply(categorize)
cat_counts = df["Category"].value_counts().reset_index()
cat_counts.columns = ["Category", "Count"]

color_map = {
    "Good": "#4CAF50",
    "Moderate": "#FFC107",
    "Poor": "#F44336",
}

st.subheader("Air Quality Category (PM2.5)")
fig3 = px.pie(
    cat_counts,
    names="Category",
    values="Count",
    color="Category",
    color_discrete_map=color_map,
    template=plotly_template,
    hole=0.25,
)
fig3.update_layout(
    paper_bgcolor=bg_color,
    plot_bgcolor=bg_color,
    font_color=text_color,
)
fig3.update_traces(textinfo="percent+label")
st.plotly_chart(fig3, use_container_width=True)
