import streamlit as st
import pandas as pd
import plotly.express as px
import os
from streamlit_option_menu import option_menu

# ---------------- PAGE CONFIG ---------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------------- THEME MEMORY ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"  # default mode

# Theme value BEFORE user clicks toggle (from previous run)
is_dark_now = st.session_state.theme == "Dark"

# ---------------- TOP BAR: TITLE + TOGGLE ----------------
header_left, header_right = st.columns([5, 2])

with header_left:
    st.markdown("<div class='header-title'>Air Aware</div>", unsafe_allow_html=True)

with header_right:
    # Pill colors depend on current theme (is_dark_now)
    unselected_bg = "#000000" if is_dark_now else "#FFFFFF"
    unselected_border = "#FFFFFF" if is_dark_now else "#000000"
    unselected_text = "#FFFFFF" if is_dark_now else "#000000"

        # Active pill = pink, text black
    selected_bg = "#ff99ff"
    selected_text = "#000000"
    selected_border = "#000000"


    selected_theme = option_menu(
        menu_title=None,
        options=["Light", "Dark"],
        icons=["sun", "moon"],
        orientation="horizontal",
        default_index=1 if st.session_state.theme == "Dark" else 0,
        key="theme_toggle",
        styles={
            "container": {"padding": "0px", "background": "transparent"},
            "nav-link": {
                "font-size": "0.9rem",
                "padding": "6px 22px",
                "margin": "0 2px",
                "border-radius": "999px",
                "transition": "0.25s",
                "background-color": unselected_bg,
                "color": unselected_text,
                "border": f"2px solid {unselected_border}",
            },
            "nav-link-selected": {
                "background-color": selected_bg,
                "color": selected_text,
                "border-radius": "999px",
                "font-weight": "600",
                "border": f"2px solid {selected_border}",
            },
            "icon": {"font-size": "1rem"},
        },
    )

# Update stored theme AFTER click
st.session_state.theme = selected_theme
dark_mode = st.session_state.theme == "Dark"

# ---------------- THEME RULES ----------------
if dark_mode:
    bg_color = "#000000"          # everything black
    text_color = "#FFFFFF"        # text white
    plotly_template = "plotly_dark"
else:
    bg_color = "#FFFFFF"          # everything white
    text_color = "#000000"        # text black
    plotly_template = "plotly_white"

# ---------------- GLOBAL UI CSS ----------------
st.markdown(
    f"""
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

/* Top Bar Color Fixed to Pink */
div[data-testid="stHorizontalBlock"]:first-of-type {{
    background-color: #ff99ff !important;
    padding: 18px 24px;
    border-radius: 12px;
    border: 2px solid {text_color};
    margin-bottom: 28px;
}}

.header-title {{
    font-size: 26px;
    font-weight: 600;
    margin-top: 4px;
}}

/* Let inline styles from option_menu control colors.
   We only force shape & spacing here. */
ul {{
    list-style: none;
    padding-left: 0;
}}

.nav-link, .nav-link-selected {{
    border-radius: 999px !important;
}}

</style>
""",
    unsafe_allow_html=True,
)

# ---------------- LOAD DATA ----------------
DATA_PATH = os.path.join("data", "cleaned_air_data.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="ignore")

    # Normalize PM2.5 column naming
    for col in df.columns:
        if "pm2" in col.lower():
            df.rename(columns={col: "PM2.5"}, inplace=True)
            break

    df["PM2.5"] = pd.to_numeric(df["PM2.5"], errors="coerce")
    return df

if not os.path.exists(DATA_PATH):
    st.error("❌ Missing required dataset: cleaned_air_data.csv")
    st.stop()

df = load_data(DATA_PATH)

# ---------------- PLOT STYLE FUNCTION ----------------
def style_fig(fig):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
    )
    fig.update_xaxes(color=text_color)
    fig.update_yaxes(color=text_color)
    return fig

# ---------------- VISUALS ----------------
col1, col2 = st.columns((2, 1))

with col1:
    st.subheader("PM2.5 Trend")
    fig1 = px.line(
        df,
        x="Timestamp",
        y="PM2.5",
        labels={"PM2.5": "PM2.5 (µg/m³)"}
    )
    # Single line color based on theme
    line_color = "#FFFFFF" if dark_mode else "#000000"
    fig1.update_traces(line=dict(color=line_color))
    st.plotly_chart(style_fig(fig1), use_container_width=True)
    
with col2:
    st.subheader("PM2.5 Distribution")
    fig2 = px.histogram(df, x="PM2.5", nbins=30)
    bar_color = "#FFFFFF" if dark_mode else "#000000"
    fig2.update_traces(marker_color=bar_color)
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

st.subheader("Air Quality Classification")
fig3 = px.pie(cat_counts, names="Category", values="Count", hole=0.25)
fig3.update_traces(textinfo="percent+label")
st.plotly_chart(style_fig(fig3), use_container_width=True)
