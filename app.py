import streamlit as st
import pandas as pd
import plotly.express as px
import os
from streamlit_option_menu import option_menu

# ---------------- PAGE CONFIG ---------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------------- TOP BAR: TITLE (LEFT) + THEME PILL TOGGLE (RIGHT) ----------------
top_col1, top_col2 = st.columns([5, 2])

# --- Maintain theme in session state ---
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"  # default

with top_col2:
    # Decide unselected pill colors based on current theme
    is_dark_now = st.session_state.theme == "Dark"
    nav_bg = "#111827" if is_dark_now else "#E5E7EB"     # dark grey / light grey
    nav_text = "#9CA3AF" if is_dark_now else "#4B5563"   # muted text

    # Wrap option_menu in a right-aligned container
    st.markdown(
        "<div style='display:flex; justify-content:flex-end;'>",
        unsafe_allow_html=True,
    )

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
                "color": nav_text,
                "background-color": nav_bg,
                "transition": "all 0.2s ease-in-out",
            },
            "nav-link-selec
