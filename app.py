import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ================== CUSTOM TOGGLE CSS (CodePen-inspired) ==================
st.markdown(
    """
    <style>
    /* Position container in top-right */
    .theme-toggle-wrapper {
        position: fixed;
        top: 15px;
        right: 25px;
        z-index: 1000;
    }

    /* Target the built-in Streamlit toggle */
    .theme-toggle-wrapper [data-testid="stToggle"] {
        padding: 0 !important;
    }

    .theme-toggle-wrapper [data-testid="stToggle"] > label {
        position: relative;
        display: inline-block;
        width: 70px;
        height: 38px;
        cursor: pointer;
    }

    /* Hide Streamlit's default label text */
    .theme-toggle-wrapper [data-testid="stToggle"] > label > div:nth-child(1) {
        display: none;
    }

    /* Hide the default checkbox visually, keep it clickable */
    .theme-toggle-wrapper [data-testid="stToggle"] input {
        opacity: 0;
        width: 0;
        height: 0;
        position: absolute;
    }

    /* Slider background (day/night track) */
    .theme-toggle-wrapper .slider-track {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        border-radius: 34px;
        background: linear-gradient(120deg, #4a90e2, #87cefa);
        transition: background 0.4s ease;
        overflow: hidden;
    }

    /* Sun/Moon knob */
    .theme-toggle-wrapper .slider-knob {
        position: absolute;
        height: 28px;
        width: 28px;
        left: 5px;
        top: 5px;
        border-radius: 50%;
        background: #ffe066;
        box-shadow: 0 0 10px rgba(255,255,255,0.7);
        transition: transform 0.4s ease, background 0.4s ease, box-shadow 0.4s ease;
    }

    /* dots = craters on moon */
    .theme-toggle-wrapper .slider-knob::bef
