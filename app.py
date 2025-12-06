import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Air Aware", layout="wide")

# FONT
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Rubik+Mono+One&display=swap');

/* Apply Rubik Mono One Everywhere */
* {
    font-family: "Rubik Mono One", sans-serif !important;
    letter-spacing: 1px;
}

/* Title sizes */
h1 { font-size: 38px !important; }
h2 { font-size: 26px !important; }
h3 { font-size: 20px !important; }

/* Widgets (input, select, button, toggle) */
.stButton > button,
.stTextInput > div > input,
.stSelectbox div,
.stRadio label,
.stCheckbox label {
    font-family: "Rubik Mono One", sans-serif !important;
    font-size: 14px !important;
}

/* Plotly chart font override */
.plotly .main-svg text {
    font-family: "Rubik Mono One", sans-serif !important;
}

</style>
""", unsafe_allow_html=True)

# THEME MEMORY
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# Top bar layout
header_left, header_right = st.columns([5, 2])

with header_left:
    st.markdown("<div class='header-title'>Air Aware</div>", unsafe_allow_html=True)

with header_right:
    # simple radio as theme toggle
    selected_theme = st.radio(
        "Theme",
        options=["Light", "Dark"],
        index=1 if st.session_state.theme == "Dark" else 0,
        horizontal=True,
        key="theme_toggle",
        label_visibility="collapsed",
    )

# Update stored theme
st.session_state.theme = selected_theme
dark_mode = st.session_state.theme == "Dark"

# THEME COLORS
if dark_mode:
    bg_color = "#000000"
    text_color = "#FFFFFF"
    plotly_template = "plotly_dark"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    plotly_template = "plotly_white"

# CSS
st.markdown(
    f"""
<style>

* {{
    font-family: 'Acme', sans-serif !important;
}}

.stApp {{
    background-color: {bg_color} !important;
    color: {text_color} !important;
}}

h1, h2, h3, h4, h5, h6, p, span, div, label {{
    color: {text_color} !important;
}}

/* Top bar */
div[data-testid="stHorizontalBlock"]:first-of-type {{
    background-color: #FF3C3C !important;
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

</style>
""",
    unsafe_allow_html=True,
)

# LOAD DATA
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
    st.error("❌ Missing required dataset: data/cleaned_air_data.csv")
    st.stop()

df = load_data(DATA_PATH)

# PLOT STYLE
def style_fig(fig):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
    )

    fig.update_xaxes(
        color=text_color,
        title_font_color=text_color,
        tickfont_color=text_color
    )
    fig.update_yaxes(
        color=text_color,
        title_font_color=text_color,
        tickfont_color=text_color
    )
    return fig

# VISUALS

# PM2.5 Trend
st.subheader("PM2.5 Trend")
fig1 = px.line(
    df,
    x="Timestamp",
    y="PM2.5",
    color="City",
    labels={"PM2.5": "PM2.5 (µg/m³)"}
)
st.plotly_chart(style_fig(fig1), use_container_width=True)

# PM2.5 Distribution
st.subheader("PM2.5 Distribution")
fig2 = px.histogram(
    df,
    x="PM2.5",
    color="City",
    nbins=30,
    labels={"PM2.5": "PM2.5 (µg/m³)"}
)
st.plotly_chart(style_fig(fig2), use_container_width=True)

# Air Quality Classification
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

pastel_colors = {
    "Good":     "#0080FF",  # DARK BLUE
    "Moderate": "#99CCFF",  # LIGHT BLUE
    "Poor":     "#FF3C3C",  # RED
}

st.subheader("Air Quality Classification")

import plotly.graph_objects as go

fig3 = px.pie(
    cat_counts,
    names="Category",
    values="Count",
    hole=0.25,
    color="Category",
    color_discrete_map=pastel_colors
)

fig3.update_traces(
    textinfo="label+percent",
    textfont_size=16,
    pull=[0.03] * cat_counts.shape[0]
)

fig3.update_layout(
    transition=dict(
        duration=600,
        easing="cubic-in-out"
    )
)

st.plotly_chart(style_fig(fig3), use_container_width=True)
