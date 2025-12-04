import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------------- TOP BAR (TITLE + TOGGLE ON RIGHT) ----------------
title_col, toggle_col = st.columns([6, 2])

with toggle_col:
    st.markdown(
        "<div style='text-align:right; font-weight:600; margin-bottom:0.3rem;'>Theme</div>",
        unsafe_allow_html=True,
    )
    dark_mode = st.toggle("Dark mode", value=True)

# ---------------- THEME SETTINGS ----------------
if dark_mode:
    bg_color = "#0e1117"
    text_color = "#FFFFFF"
    plotly_template = "plotly_dark"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    plotly_template = "plotly_white"

# Global page + text color
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        h1, h2, h3, h4, h5, h6, p, label, span, div {{
            color: {text_color} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- TITLE ----------------
with title_col:
    st.markdown(
        "<h1 style='text-align: center;'>Air Aware</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; font-size:18px;'>A simple dashboard tracking PM2.5 levels and air quality status.</p>",
        unsafe_allow_html=True,
    )

# ---------------- LOAD DATA ----------------
DATA_PATH = os.path.join("data", "cleaned_air_data.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # standardize PM2.5 column
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

# ---------------- CHARTS ----------------
col1, col2 = st.columns((2, 1))

# Helper to apply axis / legend colors
def style_fig(fig):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        legend=dict(font=dict(color=text_color)),
    )
    fig.update_xaxes(
        title_font_color=text_color,
        tickfont_color=text_color,
    )
    fig.update_yaxes(
        title_font_color=text_color,
        tickfont_color=text_color,
    )
    return fig

# ---- Line Chart ----
with col1:
    st.subheader("PM2.5 Trend")
    fig1 = px.line(df, x="Timestamp", y="PM2.5", color="City",
                   labels={"PM2.5": "PM2.5 (µg/m³)"})
    fig1 = style_fig(fig1)
    st.plotly_chart(fig1, use_container_width=True)

# ---- Histogram ----
with col2:
    st.subheader("PM2.5 Histogram")
    fig2 = px.histogram(df, x="PM2.5", nbins=30,
                        labels={"PM2.5": "PM2.5 (µg/m³)"})
    fig2 = style_fig(fig2)
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- PIE CHART ----------------
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
    hole=0.25,
)
fig3 = style_fig(fig3)
fig3.update_traces(textinfo="percent+label")
st.plotly_chart(fig3, use_container_width=True)
