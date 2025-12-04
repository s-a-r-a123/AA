import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------------- THEME TOGGLE (SINGLE, WITH KEY) ----------------
# We keep a label ("Dark mode") so we can target it in CSS, then hide the text visually.
dark_mode = st.toggle("Dark mode", value=True, key="theme_toggle")

# ---------------- THEME COLORS ----------------
if dark_mode:
    bg_color = "#0e1117"
    text_color = "#FFFFFF"
    plotly_template = "plotly_dark"
    border_color = "#FFFFFF"
    thumb_bg = "#FFFFFF"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    plotly_template = "plotly_white"
    border_color = "#000000"
    thumb_bg = "#000000"

# ---------------- TOGGLE STYLING (ALWAYS VISIBLE, TOP-RIGHT) ----------------
toggle_css = f"""
<style>
/* Select our toggle by its aria-label (the label text) */
div[data-testid="stToggle"][aria-label="Dark mode"] {{
    position: fixed;
    top: 16px;
    right: 24px;
    z-index: 1000;
}}

/* Hide the textual label next to the toggle */
div[data-testid="stToggle"][aria-label="Dark mode"] label > div:first-child {{
    display: none !important;
}}

/* Make the toggle bigger and pill-shaped */
div[data-testid="stToggle"][aria-label="Dark mode"] > label {{
    padding: 0 !important;
    width: 50px !important;
    height: 26px !important;
}}

/* Track */
div[data-testid="stToggle"][aria-label="Dark mode"] input + div {{
    width: 50px !important;
    height: 26px !important;
    border-radius: 999px !important;
    border: 2px solid {border_color} !important;
    background: transparent !important;
}}

/* Thumb */
div[data-testid="stToggle"][aria-label="Dark mode"] input + div::before {{
    width: 20px !important;
    height: 20px !important;
    top: 2px !important;
    left: 2px !important;
    border-radius: 50% !important;
    background: {thumb_bg} !important;
    border: 2px solid {border_color} !important;
}}

/* Thumb position when checked */
div[data-testid="stToggle"][aria-label="Dark mode"] input:checked + div::before {{
    transform: translateX(22px) !important;
}}
</style>
"""
st.markdown(toggle_css, unsafe_allow_html=True)

# ---------------- APPLY PAGE THEME ----------------
st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        h1, h2, h3, h4, h5, h6, p, span, div {{
            color: {text_color} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- TITLE (CENTERED) ----------------
st.markdown(
    "<h1 style='text-align:center; margin-top:20px;'>Air Aware</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; font-size:18px; margin-top:-10px;'>"
    "A simple dashboard tracking PM2.5 levels and air quality status."
    "</p>",
    unsafe_allow_html=True,
)

# ---------------- LOAD DATA ----------------
DATA_PATH = os.path.join("data", "cleaned_air_data.csv")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # parse timestamp
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # standardise PM2.5 column name
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

# ---------------- RECORD COUNT ----------------
st.markdown(
    f"<p style='font-size:18px; text-align:center;'><b>Total Records:</b> {len(df):,}</p>",
    unsafe_allow_html=True,
)

# ---------------- CHART STYLING HELPER ----------------
def style_fig(fig):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        legend=dict(font=dict(color=text_color)),
    )
    fig.update_xaxes(title_font_color=text_color, tickfont_color=text_color)
    fig.update_yaxes(title_font_color=text_color, tickfont_color=text_color)
    return fig

# ---------------- CHARTS ----------------
col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("PM2.5 Trend")
    fig1 = px.line(df, x="Timestamp", y="PM2.5", color="City",
                   labels={"PM2.5": "PM2.5 (µg/m³)"})
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col2:
    st.subheader("PM2.5 Histogram")
    fig2 = px.histogram(df, x="PM2.5", nbins=30,
                        labels={"PM2.5": "PM2.5 (µg/m³)"})
    st.plotly_chart(style_fig(fig2), use_container_width=True)

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
cat_counts = (
    df["Category"]
    .dropna()
    .value_counts()
    .reset_index()
)
cat_counts.columns = ["Category", "Count"]

color_map = {"Good": "#4CAF50", "Moderate": "#FFC107", "Poor": "#F44336"}

st.subheader("Air Quality Category (PM2.5)")
fig3 = px.pie(
    cat_counts,
    names="Category",
    values="Count",
    color="Category",
    color_discrete_map=color_map,
    hole=0.25,
)
fig3.update_traces(textinfo="percent+label")
st.plotly_chart(style_fig(fig3), use_container_width=True)
