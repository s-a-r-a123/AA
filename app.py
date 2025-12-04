import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Air Aware", layout="wide")

# ---------- THEME TOGGLE ----------
dark_mode = st.toggle("Dark mode", value=True)

if dark_mode:
    bg_color = "#0e1117"
    text_color = "#ffffff"
    plotly_template = "plotly_dark"
else:
    bg_color = "#ffffff"
    text_color = "#000000"
    plotly_template = "plotly_white"

# Apply simple background + text color
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- HEADER ----------
st.markdown(
    f"<h1 style='text-align: center; color:{text_color};'>Air Aware</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    f"<p style='text-align: center; color:{text_color};'>A simple dashboard tracking PM2.5 levels and air quality status.</p>",
    unsafe_allow_html=True,
)

# ---------- LOAD DATA ----------
DATA_PATH = os.path.join("data", "cleaned_air_data.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    # Timestamp
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # Standardise PM2.5 column name
    pm_col = None
    for c in df.columns:
        if "pm2" in c.lower():
            pm_col = c
            break

    df.rename(columns={pm_col: "PM2.5"}, inplace=True)
    df["PM2.5"] = pd.to_numeric(df["PM2.5"], errors="coerce")

    return df

if not os.path.exists(DATA_PATH):
    st.error(f"❌ Missing file: {DATA_PATH}. Please add cleaned_air_data.csv inside /data folder.")
    st.stop()

df = load_data(DATA_PATH)

# ---------- FILTERS (TOP, NOT SIDEBAR) ----------
st.subheader("Filters")

c1, c2 = st.columns(2)

cities = df["City"].dropna().unique().tolist()

with c1:
    selected_cities = st.multiselect("Select city:", cities, default=cities)

with c2:
    date_range = st.date_input(
        "Select date range:",
        [df["Timestamp"].min(), df["Timestamp"].max()]
    )

start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

mask = (
    df["City"].isin(selected_cities)
    & (df["Timestamp"] >= start_date)
    & (df["Timestamp"] <= end_date)
)
df_f = df.loc[mask].copy()

st.markdown(f"**Records displayed:** {len(df_f):,}")

# ---------- MAIN CHARTS ----------
colA, colB = st.columns((2, 1))

with colA:
    st.subheader("PM2.5 Trend")
    if df_f.empty:
        st.info("No data found for selected filters.")
    else:
        fig_trend = px.line(
            df_f,
            x="Timestamp",
            y="PM2.5",
            color="City",
            labels={"PM2.5": "PM2.5 (µg/m³)"},
            template=plotly_template,
        )
        fig_trend.update_layout(height=400)
        st.plotly_chart(fig_trend, use_container_width=True)

with colB:
    st.subheader("PM2.5 Histogram")
    if df_f.empty:
        st.info("No data found for selected filters.")
    else:
        fig_hist = px.histogram(
            df_f,
            x="PM2.5",
            nbins=30,
            labels={"PM2.5": "PM2.5 (µg/m³)"},
            template=plotly_template,
        )
        fig_hist.update_layout(height=400)
        st.plotly_chart(fig_hist, use_container_width=True)

# ---------- PIE CHART ----------
st.subheader("Air Quality Category (PM2.5)")

def categorize(x):
    if pd.isna(x):
        return "Unknown"
    if x <= 30:
        return "Good"
    elif x <= 60:
        return "Moderate"
    return "Poor"

df_f["Category"] = df_f["PM2.5"].apply(categorize)

cat_counts = df_f["Category"].value_counts().reset_index()
cat_counts.columns = ["Category", "Count"]

color_map = {
    "Good": "#4CAF50",
    "Moderate": "#FFC107",
    "Poor": "#F44336",
    "Unknown": "#9E9E9E",
}

fig_pie = px.pie(
    cat_counts,
    names="Category",
    values="Count",
    color="Category",
    color_discrete_map=color_map,
    template=plotly_template,
    hole=0.25,
)
fig_pie.update_traces(textinfo="percent+label")
st.plotly_chart(fig_pie, use_container_width=True)

# ✅ No raw dataset table and no download button anywhere
