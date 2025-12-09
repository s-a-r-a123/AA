import streamlit as st
import pandas as pd
import plotly.express as px
import os
from streamlit_option_menu import option_menu

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------------- GLOBAL FONT (Rubik Mono One) ----------------
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Rubik+Mono+One&display=swap');

/* Apply Font */
* {
    font-family: "Rubik Mono One", sans-serif !important;
    letter-spacing: 0.5px;
}

/* Title — reduce size */
.header-title {
    font-size: 22px !important;
}

/* Subheaders */
h1 { font-size: 26px !important; }
h2 { font-size: 20px !important; }
h3 { font-size: 18px !important; }

/* Body text size */
p, span, div, label {
    font-size: 12px !important;
}

/* Plotly Axis + Tooltip */
.plotly .main-svg text {
    font-size: 11px !important;
}

/* Buttons + Toggle */
.stButton > button,
.stSelectbox div,
.stTextInput input,
.stCheckbox label {
    font-size: 12px !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------- THEME MEMORY ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# Toggle placement
header_left, header_right = st.columns([5, 2])

with header_left:
    st.markdown("<div class='header-title'>AIR AWARE</div>", unsafe_allow_html=True)

with header_right:
    selected_theme = option_menu(
        None,
        ["Light", "Dark"],
        icons=["sun", "moon"],
        orientation="horizontal",
        default_index=1 if st.session_state.theme == "Dark" else 0,
        key="theme_toggle",
        styles={
            "container": {"padding": "0px", "background": "transparent"},
            "nav-link": {
                "padding": "6px 22px",
                "margin": "2px",
                "border-radius": "999px",
                "border": "3px solid black",
                "color": "black",
                "background": "#FFFFFF",
            },
            "nav-link-selected": {
                "background": "black",
                "color": "white",
                "border-radius": "999px",
                "border": "3px solid white",
            },
        },
    )

st.session_state.theme = selected_theme
dark_mode = st.session_state.theme == "Dark"

bg_color = "#000000" if dark_mode else "#FFFFFF"
text_color = "#FFFFFF" if dark_mode else "#000000"
plotly_template = "plotly_dark" if dark_mode else "plotly_white"


# ---------------- LOAD DATA ----------------
DATA_PATH = os.path.join("data", "cleaned_air_data.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="ignore")

    for col in df.columns:
        if "pm2" in col.lower():
            df.rename(columns={col: "PM2.5"}, inplace=True)

    df["PM2.5"] = pd.to_numeric(df["PM2.5"], errors="coerce")
    return df

if not os.path.exists(DATA_PATH):
    st.error("❌ Missing dataset: cleaned_air_data.csv")
    st.stop()

df = load_data(DATA_PATH)

# ---------------- STYLE FIG ----------------
def style_fig(fig):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color)
    )
    fig.update_xaxes(color=text_color)
    fig.update_yaxes(color=text_color)
    return fig


# ---------------- RECORD COUNT ----------------
st.markdown(
    f"<p style='text-align:center; font-size:20px;'>Total Records: <b>{len(df):,}</b></p>",
    unsafe_allow_html=True,
)


# ---------------- GRAPH 1: PM2.5 TREND ----------------
st.subheader("PM2.5 Trend")
fig1 = px.line(df, x="Timestamp", y="PM2.5", color="City")
st.plotly_chart(style_fig(fig1), use_container_width=True)


# ---------------- GRAPH 2: HISTOGRAM ----------------
st.subheader("PM2.5 Distribution")
fig2 = px.histogram(df, x="PM2.5", nbins=30, color="City")
st.plotly_chart(style_fig(fig2), use_container_width=True)


# ---------------- GRAPH 3: PIE CHART ----------------
def categorize(x):
    if pd.isna(x): return None
    return "Good" if x <= 30 else "Moderate" if x <= 60 else "Poor"

df["Category"] = df["PM2.5"].apply(categorize)
cat_counts = df["Category"].value_counts().reset_index()
cat_counts.columns = ["Category", "Count"]

# Pastel animated pie
st.subheader("Air Quality Classification")
fig3 = px.pie(
    cat_counts,
    names="Category",
    values="Count",
    hole=0.25,
    color_discrete_sequence=["#A3E4D7", "#FAD7A0", "#F5B7B1"]
)
fig3.update_traces(textinfo="percent+label", pull=[0.04]*3)
fig3.update_layout(transition=dict(duration=600, easing="cubic-in-out"))

st.plotly_chart(style_fig(fig3), use_container_width=True)
