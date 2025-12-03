# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Config ---
st.set_page_config(page_title="Air Aware", layout="wide", initial_sidebar_state="auto")

# Title / header
st.title("Air Aware")
st.markdown("Simple interactive dashboard for PM2.5 and air quality overview.")

# Load data
DATA_PATH = os.path.join("data", "cleaned_air_data.csv")
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    # Ensure timestamp column exists & parsed
    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    else:
        # try to find a datetime like column
        for c in df.columns:
            if "time" in c.lower():
                df["Timestamp"] = pd.to_datetime(df[c], errors="coerce")
                break
    # pick a pm column
    pm_col = None
    for c in df.columns:
        if "pm2" in c.lower():
            pm_col = c
            break
    df.rename(columns={pm_col: "PM2.5"}, inplace=True)
    df["PM2.5"] = pd.to_numeric(df["PM2.5"], errors="coerce")
    return df

if not os.path.exists(DATA_PATH):
    st.error(f"Data file not found at {DATA_PATH}. Put cleaned_air_data.csv in the data/ folder.")
    st.stop()

df = load_data(DATA_PATH)

# Sidebar filters
st.sidebar.header("Filters")
cities = df["City"].dropna().unique().tolist()
selected_cities = st.sidebar.multiselect("Select city (one or more):", options=cities, default=cities)

min_date = df["Timestamp"].min()
max_date = df["Timestamp"].max()
date_range = st.sidebar.date_input("Date range:", [min_date.date(), max_date.date()])

# Filter data based on sidebar
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
mask = df["City"].isin(selected_cities) & (df["Timestamp"] >= start_date) & (df["Timestamp"] <= end_date)
df_f = df.loc[mask].copy()

# Small info
st.markdown(f"**Records shown:** {len(df_f):,}")

# Layout: left big plot and right smaller visuals
col1, col2 = st.columns((2,1))

# Time series (PM2.5 over time)
with col1:
    st.subheader("PM2.5 Over Time")
    if df_f.empty:
        st.info("No data for selected filters.")
    else:
        fig_ts = px.line(df_f, x="Timestamp", y="PM2.5", color="City", labels={"PM2.5":"PM2.5 (µg/m³)"})
        fig_ts.update_layout(legend_title_text="City", height=450)
        st.plotly_chart(fig_ts, use_container_width=True)

# Right column: histogram + pie
with col2:
    st.subheader("PM2.5 Histogram")
    if df_f.empty:
        st.info("No data for selected filters.")
    else:
        fig_hist = px.histogram(df_f, x="PM2.5", nbins=30, marginal="box", labels={"PM2.5":"PM2.5 (µg/m³)"})
        fig_hist.update_layout(height=300)
        st.plotly_chart(fig_hist, use_container_width=True)

    # Pie chart by category
    st.subheader("Air Quality Category (PM2.5)")
    def categorize_pm25(x):
        if pd.isna(x):
            return "Unknown"
        if x <= 30:
            return "Good"
        elif x <= 60:
            return "Moderate"
        else:
            return "Poor"

    df_f["PM2.5 Category"] = df_f["PM2.5"].apply(categorize_pm25)
    cat_counts = df_f["PM2.5 Category"].value_counts().reset_index()
    cat_counts.columns = ["Category","Count"]

    # custom color mapping
    color_map = {"Good":"#69C86D", "Moderate":"#FFFF07", "Poor":"#F65F54", "Unknown":"#9E9E9E"}
    fig_pie = px.pie(cat_counts, names="Category", values="Count", color="Category",
                     color_discrete_map=color_map, hole=0.25)
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(height=350)
    st.plotly_chart(fig_pie, use_container_width=True)

# Show sample table and download
st.subheader("Sample data")
st.dataframe(df_f.head(200))

# Provide download button for filtered data
@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(df_f)
st.download_button("Download filtered data (CSV)", data=csv_data, file_name="air_filtered.csv", mime="text/csv")
