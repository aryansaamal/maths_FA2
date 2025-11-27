import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# =========================================================
# PAGE SETUP - Always Dark Theme
# =========================================================
st.set_page_config(
    page_title="Last Mile Delivery BI Dashboard",
    layout="wide"
)

# Dark Theme Styling
bg_color = "#020617"        # slate-950
card_bg = "#020617"
title_color = "#e5e7eb"
subtitle_color = "#9ca3af"
kpi_value_color = "#f9fafb"
chart_template = "plotly_dark"

st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {bg_color};
    }}
    .block-container {{
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
    }}
    .dashboard-title {{
        font-size: 40px;
        font-weight: 900;
        color: {title_color};
        margin-bottom: -5px;
    }}
    .dashboard-subtitle {{
        font-size: 15px;
        font-weight: 500;
        color: {subtitle_color};
        margin-bottom: 20px;
    }}
    .card {{
        background-color: {card_bg};
        padding: 1rem 1.5rem;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(255,255,255,0.08);
        margin-bottom: 1rem;
        border: 1px solid rgba(148,163,184,0.25);
    }}
    .kpi-title {{
        color: #9ca3af;
        font-size: 12px;
        text-transform: uppercase;
    }}
    .kpi-value {{
        font-size: 28px;
        font-weight: 700;
        color: {kpi_value_color};
    }}
    .kpi-subtext {{
        font-size: 11px;
        color: #6b7280;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# HEADER
# =========================================================
st.markdown('<p class="dashboard-title">Last Mile Delivery Performance Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="dashboard-subtitle">Analyze delivery performance by weather, traffic, vehicle, agent & area.</p>', unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    return pd.read_csv("cleaned_delivery_data.csv")

df = load_data().copy()

# =========================================================
# DATA CLEANING & FEATURES
# =========================================================
cat_cols = ["Weather", "Traffic", "Vehicle", "Area", "Category"]
for col in cat_cols:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown")

if "Agent_Rating" in df.columns:
    df["Agent_Rating"] = df["Agent_Rating"].fillna(df["Agent_Rating"].mean())

if "Agent_Age" in df.columns:
    df["Agent_Age"] = df["Agent_Age"].fillna(df["Agent_Age"].median())

avg_delivery_time = df["Delivery_Time"].mean()
std_delivery_time = df["Delivery_Time"].std()
df["Is_Late"] = df["Delivery_Time"] > (avg_delivery_time + std_delivery_time)
late_percentage = df["Is_Late"].mean() * 100

def age_group(age):
    if age < 25: return "<25"
    elif age <= 40: return "25-40"
    return "40+"

df["Agent_Age_Group"] = df["Agent_Age"].apply(age_group)

# =========================================================
# SIDEBAR FILTERS
# =========================================================
st.sidebar.title("Filters")

def options(series):
    return ["All"] + sorted(series.dropna().unique())

weather_sel = st.sidebar.selectbox("Weather", options(df["Weather"]))
traffic_sel = st.sidebar.selectbox("Traffic", options(df["Traffic"]))
vehicle_sel = st.sidebar.selectbox("Vehicle", options(df["Vehicle"]))
area_sel = st.sidebar.selectbox("Area", options(df["Area"]))
cat_sel = st.sidebar.selectbox("Category", options(df["Category"]))

filtered_df = df.copy()
if weather_sel != "All": filtered_df = filtered_df[filtered_df["Weather"] == weather_sel]
if traffic_sel != "All": filtered_df = filtered_df[filtered_df["Traffic"] == traffic_sel]
if vehicle_sel != "All": filtered_df = filtered_df[filtered_df["Vehicle"] == vehicle_sel]
if area_sel != "All": filtered_df = filtered_df[filtered_df["Area"] == area_sel]
if cat_sel != "All": filtered_df = filtered_df[filtered_df["Category"] == cat_sel]

# =========================================================
# KPI CARDS
# =========================================================
k1, k2, k3 = st.columns(3)

with k1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-title">Average Delivery Time</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-value">{avg_delivery_time:.2f} mins</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-subtext">Mean delivery duration</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with k2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-title">% Late Deliveries</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-value">{late_percentage:.2f}%</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-subtext">Late = > Mean + 1 Std Dev</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with k3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="kpi-title">Records (Filtered)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="kpi-value">{len(filtered_df)}</div>', unsafe_allow_html=True)
    st.markdown('<div class="kpi-subtext">Rows in analysis</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# CHARTS (PLOTLY DARK)
# =========================================================
def chart_card(title, figure):
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader(title)
    st.plotly_chart(figure, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

fig1 = px.bar(
    filtered_df.groupby(["Weather","Traffic"])["Delivery_Time"].mean().reset_index(),
    x="Weather", y="Delivery_Time", color="Traffic",
    title="Avg Time by Weather & Traffic", template=chart_template
)

fig2 = px.bar(
    filtered_df.groupby("Vehicle")["Delivery_Time"].mean().reset_index(),
    x="Vehicle", y="Delivery_Time",
    title="Avg Time by Vehicle", template=chart_template
)

fig3 = px.scatter(
    filtered_df, x="Agent_Rating", y="Delivery_Time",
    color="Agent_Age_Group",
    title="Delivery Time vs Rating", template=chart_template
)

fig4 = px.density_heatmap(
    filtered_df.groupby("Area")["Delivery_Time"].mean().reset_index(),
    x="Area", y="Delivery_Time",
    title="Avg Time by Area", template=chart_template
)

fig5 = px.box(
    filtered_df, x="Category", y="Delivery_Time",
    title="Time Dist. by Category", template=chart_template
)

late_df = filtered_df.groupby("Weather")["Is_Late"].mean().reset_index()
late_df["Late_%"] = late_df["Is_Late"] * 100
fig6 = px.bar(
    late_df, x="Weather", y="Late_%",
    title="% Late Deliveries (Weather)", template=chart_template
)

# =========================================================
# VISUAL LAYOUT (3 ROWS)
# =========================================================
c1, c2 = st.columns(2)
with c1: chart_card("Delay Analyzer", fig1)
with c2: chart_card("Vehicle Comparison", fig2)

c3, c4 = st.columns(2)
with c3: chart_card("Agent Performance", fig3)
with c4: chart_card("Area Heatmap", fig4)

c5, c6 = st.columns(2)
with c5: chart_card("Category Visualizer", fig5)
with c6: chart_card("Late by Weather", fig6)
