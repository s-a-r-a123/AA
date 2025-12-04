import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Page Setup ---
st.set_page_config(page_title="Air Aware", layout="wide")

# ---- Header ----
st.markdown("<h1 style='text-align: center;'>Air Aware</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>A simple dashboard tracking PM2.5 levels and air quality status.</p>", unsafe_allow_html=True)

# ---- Load Data ----
DATA_PATH = os.path.join("data", "cleaned_air_data.csv")

@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    # ensure timestamp
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    # ensure PM2.5 column name is standardized
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

# ---- Top Filters (Not Sidebar) ----
st.subheader("Filters")

col1, col2 = st.columns(2)

cities = df["City"].dropna().unique().tolist()

with col1:
    selected_cities = st.multiselect("Select city:", cities, default=cities)

with col2:
    date_range = st.date_input(
        "Select date range:",
        [df["Timestamp"].min(), df["Timestamp"].max()]
    )

start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

df_f = df[
    (df["City"].isin(selected_cities)) &
    (df["Timestamp"] >= start_date) & 
    (df["Timestamp"] <= end_date)
]

st.write(f"📌 **Records displayed:** {len(df_f):,}")

# ---- Graphs ----

colA, colB = st.columns((2,1))

with colA:
    st.subheader("PM2.5 Trend")
    if not df_f.empty:
        fig = px.line(df_f, x="Timestamp", y="PM2.5", color="City")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data found for selected filters.")

with colB:
    st.subheader("PM2.5 Distribution")
    if not df_f.empty:
        fig2 = px.histogram(df_f, x="PM2.5", nbins=30)
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)

# ---- Pie Chart ----
st.subheader("Air Quality Category (PM2.5)")

def categorize(x):
    if pd.isna(x): return "Unknown"
    if x <= 30: return "Good"
    elif x <= 60: return "Moderate"
    return "Poor"

df_f["Category"] = df_f["PM2.5"].apply(categorize)

category_counts = df_f["Category"].value_counts().reset_index()
category_counts.columns = ["Category", "Count"]

color_map = {
    "Good": "#4CAF50",
    "Moderate": "#FFC107",
    "Poor": "#F44336",
    "Unknown": "#9E9E9E"
}

fig3 = px.pie(
    category_counts, names="Category", values="Count",
    color="Category", color_discrete_map=color_map, hole=0.25
)
fig3.update_traces(textinfo="percent+label")
st.plotly_chart(fig3, use_container_width=True)

# ---- Sample Table ----
st.subheader("Sample Data")
st.dataframe(df_f.head(100))
