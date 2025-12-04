import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------------- LOAD CUSTOM CSS (Toggle Styling) ----------------
if os.path.exists("styles/toggle.css"):
    with open("styles/toggle.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
else:
    st.warning("⚠️ toggle.css not found in /styles folder")


# ---------------- HTML TOGGLE BUTTON ----------------
toggle_html = """
<div class="theme-toggle-wrapper" style="position:fixed; top:18px; right:22px; z-index:9999;">
<label class="switch">
  <input id="toggle-darkmode" type="checkbox">
  <span class="slider round"></span>
</label>
</div>

<script>
const checkbox = document.getElementById("toggle-darkmode");

checkbox.addEventListener('change', function() {
    window.parent.postMessage(
        {toggle: checkbox.checked},
        "*"
    );
});
</script>
"""

st.markdown(toggle_html, unsafe_allow_html=True)


# ---------------- STREAMLIT THEME STATE ----------------
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True  # default mode


# Listen to toggle from JavaScript
event = st.experimental_get_query_params()
# no page reload toggle here, handled by UI


# Theme switching behavior
dark_mode = st.session_state.dark_mode
bg_color = "#0E1117" if dark_mode else "#FFFFFF"
text_color = "#FFFFFF" if dark_mode else "#000000"
plotly_theme = "plotly_dark" if dark_mode else "plotly_white"


# ---------------- APPLY THEME ----------------
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
    "<h1 style='text-align:center; margin-top:25px;'>Air Aware</h1>",
    unsafe_allow_html=True,
)

st.markdown(
    "<p style='text-align:center; font-size:18px;'>PM2.5 Air Quality Dashboard</p>",
    unsafe_allow_html=True,
)


# ---------------- LOAD DATA ----------------
DATA_PATH = "data/cleaned_air_data.csv"

@st.cache_data
def get_data():
    df = pd.read_csv(DATA_PATH)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df.rename(columns={col: "PM2.5" for col in df.columns if "pm2" in col.lower()}, inplace=True)
    return df

if not os.path.exists(DATA_PATH):
    st.error(f"❌ Missing required file: `{DATA_PATH}`")
    st.stop()

df = get_data()


# ---------------- RECORD TOTAL ----------------
st.markdown(
    f"<p style='text-align:center; font-size:18px;'><b>Total Records:</b> {len(df):,}</p>",
    unsafe_allow_html=True,
)



# ---------------- CHART COLORS ----------------
def apply_style(fig):
    fig.update_layout(
        template=plotly_theme,
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=text_color),
        legend=dict(font=dict(color=text_color))
    )
    fig.update_xaxes(color=text_color)
    fig.update_yaxes(color=text_color)
    return fig


# ---------------- CHARTS ----------------
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("PM2.5 Trend")
    fig1 = px.line(df, x="Timestamp", y="PM2.5", color="City")
    st.plotly_chart(apply_style(fig1), use_container_width=True)

with col2:
    st.subheader("PM2.5 Histogram")
    fig2 = px.histogram(df, x="PM2.5", nbins=30, color="City")
    st.plotly_chart(apply_style(fig2), use_container_width=True)


# ---------------- PIE CHART ----------------
def category(value):
    if value <= 30:
        return "Good"
    elif value <= 60:
        return "Moderate"
    return "Poor"

df["Quality"] = df["PM2.5"].apply(category)
pie_data = df["Quality"].value_counts().reset_index()
pie_data.columns = ["Category", "Count"]

colors = {"Good": "#4CAF50", "Moderate": "#FFC107", "Poor": "#F44336"}

st.subheader("Air Quality Categories")

fig3 = px.pie(
    pie_data,
    values="Count",
    names="Category",
    color="Category",
    color_discrete_map=colors,
    hole=0.35
)
fig3.update_traces(textinfo="label+percent")
st.plotly_chart(apply_style(fig3), use_container_width=True)
