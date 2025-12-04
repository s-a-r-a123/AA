import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------------- THEME TOGGLE (TOP RIGHT, STYLED) ----------------
toggle_css = """
<style>
/* Move toggle to right corner */
.theme-toggle-container {
    position: fixed;
    top: 18px;
    right: 25px;
    z-index: 9999;
}

/* Hide text label */
.theme-toggle-container label span {
    display: none !important;
}

/* Make toggle bigger and outlined */
.theme-toggle-container [data-testid="stToggle"] > label {
    width: 55px !important;
    height: 30px !important;
    padding: 0 !important;
}

/* Track (border changes based on theme) */
.theme-toggle-container [data-testid="stToggle"] input + div {
    width: 55px !important;
    height: 28px !important;
    border-radius: 20px !important;
    border: 2px solid VAR_BORDER_COLOR;
    background-color: transparent !important;
}

/* Thumb styling (circle) */
.theme-toggle-container [data-testid="stToggle"] input + div::before {
    width: 22px !important;
    height: 22px !important;
    top: 3px !important;
    left: 3px !important;
    border-radius: 50% !important;
    background-color: VAR_THUMB_BG;
    border: 2px solid VAR_THUMB_BORDER;
}

/* Move thumb on check */
.theme-toggle-container [data-testid="stToggle"] input:checked + div::before {
    transform: translateX(25px) !important;
}
</style>
"""

# Inject CSS placeholder that we will replace dynamically
st.markdown(toggle_css.replace("VAR_BORDER_COLOR", "#000000")
                        .replace("VAR_THUMB_BG", "#000000")
                        .replace("VAR_THUMB_BORDER", "#000000"),
            unsafe_allow_html=True)

# Render toggle container
st.markdown('<div class="theme-toggle-container">', unsafe_allow_html=True)
dark_mode = st.toggle(label="", value=True)
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- APPLY THEME COLORS ----------------
if dark_mode:
    bg_color = "#0e1117"
    text_color = "#FFFFFF"
    border_color = "#FFFFFF"
    thumb_bg = "#FFFFFF"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    border_color = "#000000"
    thumb_bg = "#000000"

# Update CSS live based on toggle state
st.markdown(
    f"""
    <style>
    .theme-toggle-container [data-testid="stToggle"] input + div {{
        border-color: {border_color} !important;
    }}
    .theme-toggle-container [data-testid="stToggle"] input + div::before {{
        background-color: {thumb_bg} !important;
        border-color: {border_color} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

plotly_template = "plotly_dark" if dark_mode else "plotly_white"

# Background + Text Theme
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

# ---------------- TITLE ----------------
st.markdown(
    "<h1 style='text-align:center; margin-top:20px;'>Air Aware</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align:center; font-size:18px; margin-top:-10px;'>A simple dashboard tracking PM2.5 levels and air quality status.</p>",
    unsafe_allow_html=True,
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

# ---------------- RECORD COUNT ----------------
st.markdown(f"<p style='font-size:18px; text-align:center;'><b>Total Records:</b> {len(df):,}</p>", unsafe_allow_html=True)

# ---------------- CHART HELPER ----------------
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
    fig1 = px.line(df, x="Timestamp", y="PM2.5", color="City")
    st.plotly_chart(style_fig(fig1), use_container_width=True)

with col2:
    st.subheader("PM2.5 Histogram")
    fig2 = px.histogram(df, x="PM2.5", nbins=30)
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
cat_counts = df["Category"].value_counts().reset_index()
cat_counts.columns = ["Category", "Count"]

st.subheader("Air Quality Category (PM2.5)")
fig3 = px.pie(cat_counts, names="Category", values="Count",
               color="Category", hole=0.25)
fig3.update_traces(textinfo="percent+label")
st.plotly_chart(style_fig(fig3), use_container_width=True)
