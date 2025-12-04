import streamlit as st
import pandas as pd
import plotly.express as px
import os
from streamlit_option_menu import option_menu

# ---------------- PAGE CONFIG ---------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------------- SESSION STATE FOR THEME ----------------
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"  # default

# Whether currently dark mode
dark_mode = st.session_state.theme == "Dark"

# Navbar dynamic color
navbar_bg = "#111827" if dark_mode else "#F3F4F6"  # near-black or soft gray
navbar_text = "#FFFFFF" if dark_mode else "#111827"

# ---------------- NAVBAR ----------------
st.markdown(
    f"""
    <style>
        .navbar {{
            width: 100%;
            height: 65px;
            background-color: {navbar_bg};
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0 25px;
            border-radius: 10px;
            margin-bottom: 25px;
            box-shadow: 0px 2px 8px rgba(0,0,0,0.15);
        }}
        .navbar-title {{
            font-size: 26px;
            font-weight: 600;
            color: {navbar_text};
            font-family: 'Poppins', sans-serif;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ------- Render Navbar --------
navbar_cols = st.columns([6, 4])

with navbar_cols[0]:
    st.markdown(
        f"<div class='navbar'><span class='navbar-title'>Air Aware</span>",
        unsafe_allow_html=True
    )

with navbar_cols[1]:
    st.markdown("<div style='display:flex; justify-content:flex-end;'>", unsafe_allow_html=True)

    selected_theme = option_menu(
        menu_title=None,
        options=["Light", "Dark"],
        icons=["sun", "moon"],
        orientation="horizontal",
        default_index=1 if st.session_state.theme == "Dark" else 0,
        key="theme_option",
        styles={
            "container": {
                "padding": "0px",
                "background-color": "rgba(0,0,0,0)",
                "border-radius": "999px",
            },
            "nav-link": {
                "font-size": "0.9rem",
                "padding": "6px 22px",
                "margin": "0 2px",
                "border-radius": "999px",
                "color": "#9CA3AF",
                "background-color": "#374151" if dark_mode else "#E5E7EB",
                "transition": "all 0.2s ease-in-out",
            },
            "nav-link-selected": {
                "background-color": "#6366F1",
                "color": "white",
                "font-weight": "600",
                "border-radius": "999px",
            },
        },
    )

    st.markdown("</div></div>", unsafe_allow_html=True)

# Update theme
st.session_state.theme = selected_theme
dark_mode = st.session_state.theme == "Dark"

# ---------------- THEME COLORS ----------------
if dark_mode:
    bg_color = "#0e1117"
    text_color = "#FFFFFF"
    plotly_template = "plotly_dark"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    plotly_template = "plotly_white"

# ---------------- GLOBAL STYLE + FONT ----------------
st.markdown(
    f"""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <style>
        * {{ font-family: 'Poppins', sans-serif !important; }}
        .stApp {{
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        h1, h2, h3, h4, h5, h6, p, span, div, label {{
            color: {text_color} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)
