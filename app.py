import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------------- TOP BAR: TITLE + TOGGLE ----------------
top_col1, top_col2 = st.columns([5, 1])

with top_col2:
    # Built-in toggle (this is what we visually restyle)
    dark_mode = st.toggle("Dark mode", value=True, key="theme_toggle")

# ---------------- THEME SETTINGS ----------------
if dark_mode:
    bg_color = "#0e1117"
    text_color = "#FFFFFF"
    plotly_template = "plotly_dark"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    plotly_template = "plotly_white"

# ---------------- GLOBAL THEME + FONT + TOGGLE CSS ----------------
st.markdown(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <style>
    * {{
        font-family: 'Poppins', sans-serif !important;
    }}

    .stApp {{
        background-color: {bg_color} !important;
        color: {text_color} !important;
    }}

    h1, h2, h3, h4, h5, h6, p, span, div, label {{
        color: {text_color} !important;
    }}

    /* --- Custom toggle styled like your examples --- */

    /* Position our specific toggle in top-right */
    div[data-testid="stToggle"][aria-label="Dark mode"] {{
        position: fixed;
        top: 16px;
        right: 24px;
        z-index: 1000;
    }}

    /* Hide the "Dark mode" text label */
    div[data-testid="stToggle"][aria-label="Dark mode"] label > div:first-child {{
        display: none !important;
    }}

    /* Use the label as the .switch container */
    div[data-testid="stToggle"][aria-label="Dark mode"] > label {{
        --width-of-switch: 3.5em;
        --height-of-switch: 2em;
        --size-of-icon: 1.4em;
        --slider-offset: 0.3em;
        position: relative;
        width: var(--width-of-switch);
        height: var(--height-of-switch);
        padding: 0 !important;
        display: block;
    }}

    /* Hide the native checkbox */
    div[data-testid="stToggle"][aria-label="Dark mode"] input {{
        opacity: 0;
        width: 0;
        height: 0;
    }}

    /* Track = .slider */
    div[data-testid="stToggle"][aria-label="Dark mode"] input + div {{
        position: absolute;
        cursor: pointer;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: #f4f4f5;    /* light mode track */
        transition: .4s;
        border-radius: 30px;
    }}

    /* Knob = .slider:before */
    div[data-testid="stToggle"][aria-label="Dark mode"] input + div::before {{
        position: absolute;
        content: "";
        height: var(--size-of-icon);
        width: var(--size-of-icon);
        border-radius: 20px;
        left: var(--slider-offset);
        top: 50%;
        transform: translateY(-50%);
        background: linear-gradient(40deg,#ff0080,#ff8c00 70%);  /* sun gradient */
        transition: .4s;
    }}

    /* Checked: dark mode → moon style (first image) */
    div[data-testid="stToggle"][aria-label="Dark mode"] input:checked + div {{
        background-color: #303136;    /* dark track */
    }}

    div[data-testid="stToggle"][aria-label="Dark mode"] input:checked + div::before {{
        left: calc(100% - (var(--size-of-icon) + var(--slider-offset)));
        background: #303136;
        /* inner highlights = moon craters */
        box-shadow:
            inset -3px -2px 5px -2px #8983f7,
            inset -10px -4px 0 0 #a3dafb;
    }}

    /* Ensure widget text (if any other) keeps font & color */
    .stTextInput input,
    .stSelectbox div,
    .stMultiSelect div,
    .stCheckbox label,
    .stToggle label {{
        font-family: 'Poppins', sans-serif !important;
        color: {text_color} !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- TITLE (CENTERED) ----------------
with top_col1:
    st.markdown(
        "<h1 style='text-align:center; margin-top:10px;'>Air Aware</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center; font-size:18px; margin-top:-5px;'>"
        "PM2.5 Air Quality Dashboard"
        "</p>",
        unsafe_allow_html=True,
    )

# ---------------- LOAD DATA ----------------
DATA_PATH = os.path.join("data", "cleaned_air_data.csv")

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    # Parse timestamp
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Standardize PM2.5 column name
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
    f"<p style='font-size:18px; text-align:center; margin-bottom:20px;'>"
    f"<b>Total Records:</b> {len(df):,}</p>",
    unsafe_allow_html=True,
)

# ---------------- PLOT STYLING HELPER ----------------
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
                        labels={"PM2.5": "PM2.5 (µg/m³)"}, color="City")
    st.plotly_chart(style_fig(fig2), use_container_width=True)

# ---------------- PIE CHART ----------------
def categorize(pm):
    if pd.isna(pm):
        return None
    if pm <= 30:
        return "Good"
    elif pm <= 60:
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

st.subheader("Air Quality Categories")
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
