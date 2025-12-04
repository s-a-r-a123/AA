import streamlit as st
import pandas as pd
import plotly.express as px
import os
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Air Aware", layout="wide")

#FONT
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

/* Adjust body text so it doesn’t look too large */
p, span, div {
    font-size: 15px !important;
}

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

#THEME MEMORY
if "theme" not in st.session_state:
    st.session_state.theme = "Dark" 

# Theme BEFORE
is_dark_now = st.session_state.theme == "Dark"

#TOP BAR
header_left, header_right = st.columns([5, 2])

with header_left:
    st.markdown("<div class='header-title'>Air Aware</div>", unsafe_allow_html=True)

with header_right:
    
    unselected_bg = "#000000" if is_dark_now else "#FFFFFF"
    unselected_border = "#FFFFFF" if is_dark_now else "#000000"
    unselected_text = "#FFFFFF" if is_dark_now else "#000000"

    selected_bg = "#FFFFFF" if is_dark_now else "#000000"
    selected_text = "#000000" if is_dark_now else "#FFFFFF"
    selected_border = selected_text

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

#THEME
if dark_mode:
    bg_color = "#000000"          
    text_color = "#FFFFFF"        
    plotly_template = "plotly_dark"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    plotly_template = "plotly_white"

#CSS
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

/* Top bar*/
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

/* Let option_menu inline styles control pill colors; we only shape them */
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

#LOAD DATA
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

#PLOT STYLE
def style_fig(fig):
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
    )
    
    fig.update_xaxes(color=text_color, title_font_color=text_color, tickfont_color=text_color)
    fig.update_yaxes(color=text_color, title_font_color=text_color, tickfont_color=text_color)
    return fig

#VISUALS

#PM2.5 Trend
st.subheader("PM2.5 Trend")
fig1 = px.line(
    df,
    x="Timestamp",
    y="PM2.5",
    color="City",
    labels={"PM2.5": "PM2.5 (µg/m³)"}
)
st.plotly_chart(style_fig(fig1), use_container_width=True)

#PM2.5 Distribution
st.subheader("PM2.5 Distribution")
fig2 = px.histogram(
    df,
    x="PM2.5",
    color="City",
    nbins=30,
    labels={"PM2.5": "PM2.5 (µg/m³)"}
)
st.plotly_chart(style_fig(fig2), use_container_width=True)

#Air Quality Classification
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

# Pastel color palette
pastel_colors = {
    "Good":     "#A3E4D7",  # mint 
    "Moderate": "#FAD7A0",  # peach
    "Poor":     "#F5B7B1",  # light rose
}

st.subheader("Air Quality Classification")

fig3 = px.pie(
    cat_counts,
    names="Category",
    values="Count",
    hole=0.25,
    color="Category",
    color_discrete_map=pastel_colors
)

# Text + slight lift
fig3.update_traces(
    textinfo="label+percent",
    textfont_size=16,
    pull=[0.03] * cat_counts.shape[0]  
)

#transition
fig3.update_layout(
    transition=dict(
        duration=600,          
        easing="cubic-in-out"  
    )
)

st.plotly_chart(style_fig(fig3), use_container_width=True)

