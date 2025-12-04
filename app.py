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
    .theme-toggle-wrapper .slider-knob::before,
    .theme-toggle-wrapper .slider-knob::after {
        content: "";
        position: absolute;
        border-radius: 50%;
        background: rgba(0,0,0,0.2);
        opacity: 0;
        transition: opacity 0.4s ease;
    }

    .theme-toggle-wrapper .slider-knob::before {
        width: 6px;
        height: 6px;
        top: 6px;
        left: 7px;
    }

    .theme-toggle-wrapper .slider-knob::after {
        width: 4px;
        height: 4px;
        bottom: 6px;
        right: 7px;
    }

    /* Tiny stars in background (visible in dark mode) */
    .theme-toggle-wrapper .slider-track::before,
    .theme-toggle-wrapper .slider-track::after {
        content: "✦";
        position: absolute;
        color: rgba(255,255,255,0.0);
        font-size: 10px;
        transition: color 0.4s ease, transform 1.5s ease-in-out;
    }

    .theme-toggle-wrapper .slider-track::before {
        top: 6px;
        left: 38px;
    }

    .theme-toggle-wrapper .slider-track::after {
        bottom: 8px;
        right: 10px;
    }

    /* Checked (dark mode) styles:
       - background darker
       - knob slides right and turns "moon"
       - craters + stars appear
    */
    .theme-toggle-wrapper [data-testid="stToggle"] input:checked + div .slider-track {
        background: linear-gradient(120deg, #1b2735, #090a0f);
    }

    .theme-toggle-wrapper [data-testid="stToggle"] input:checked + div .slider-knob {
        transform: translateX(30px);
        background: #f5f5f5;
        box-shadow: 0 0 12px rgba(255,255,255,0.9);
    }

    .theme-toggle-wrapper [data-testid="stToggle"] input:checked + div .slider-knob::before,
    .theme-toggle-wrapper [data-testid="stToggle"] input:checked + div .slider-knob::after {
        opacity: 1;
    }

    .theme-toggle-wrapper [data-testid="stToggle"] input:checked + div .slider-track::before,
    .theme-toggle-wrapper [data-testid="stToggle"] input:checked + div .slider-track::after {
        color: rgba(255,255,255,0.8);
        transform: scale(1.1);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------- THEME TOGGLE WIDGET (FUNCTIONAL) ----------------
# We render the toggle inside a wrapper, then inject the custom parts using HTML
with st.container():
    st.markdown('<div class="theme-toggle-wrapper">', unsafe_allow_html=True)
    # label="" so no text; we just use toggle's checkbox
    dark_mode = st.toggle("", value=True, key="theme_toggle")
    # add our track + knob right after the checkbox+internal div
    st.markdown(
        """
        <script>
        // This script just restructures the DOM of the toggle created by Streamlit
        // and adds our custom slider elements inside the label.
        const wrappers = window.parent.document.querySelectorAll('.theme-toggle-wrapper [data-testid="stToggle"] > label');
        wrappers.forEach(w => {
          if (!w.querySelector('.slider-track')) {
            const box = w.querySelector('div:nth-of-type(2)');
            if (box) {
              box.style.display = 'none'; // hide default visual box
            }
            const track = document.createElement('div');
            track.className = 'slider-track';
            const knob = document.createElement('div');
            knob.className = 'slider-knob';
            w.appendChild(track);
            w.appendChild(knob);
          }
        });
        </script>
        """,
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

# NOTE: In many Streamlit deployments <script> inside markdown is stripped.
# If your deployment strips this, you'll still have a normal toggle instead of the fancy one,
# but the theme logic below will continue to work.

# ---------------- THEME COLORS ----------------
if dark_mode:
    bg_color = "#0e1117"
    text_color = "#FFFFFF"
    plotly_template = "plotly_dark"
else:
    bg_color = "#FFFFFF"
    text_color = "#000000"
    plotly_template = "plotly_white"

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
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
    "<p style='text-align:center; font-size:18px; margin-top:-10px;'>"
    "A simple dashboard tracking PM2.5 levels and air quality status."
    "</p>",
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
cat_counts = df["Category"].value_counts().reset_index()
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
