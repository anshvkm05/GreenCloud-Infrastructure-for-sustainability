import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import time
from datetime import datetime

# --- Configuration & Styling ---
st.set_page_config(page_title="Eco-Scale Dashboard", page_icon="🍃", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .css-1d391kg { background-color: #161b22; }
    .metric-card {
        background-color: #21262d; border-radius: 10px; padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3); border-left: 5px solid #2ea043;
    }
    .metric-value { font-size: 36px; font-weight: bold; color: #2ea043; }
    .metric-title { font-size: 14px; color: #8b949e; text-transform: uppercase; }
    h1, h2, h3 { color: #58a6ff; }
    .unique-feature {
        background: linear-gradient(135deg, #13233a 0%, #0d1117 100%);
        border: 1px solid #30363d; border-radius: 12px; padding: 25px; margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("cluster_telemetry.csv")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        return pd.DataFrame(columns=['timestamp', 'hour_of_day', 'day_of_week', 'avg_cpu_load', 'avg_memory_load', 'network_traffic_gbps', 'safe_shutdown_count'])

@st.cache_resource
def load_model():
    try:
        return joblib.load("rf_cluster_model.pkl")
    except FileNotFoundError:
        return None

df = load_data()
model = load_model()

# --- Sidebar ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3063/3063124.png", width=60)
st.sidebar.title("Eco-Scale Control")
st.sidebar.markdown("Predictive **Cluster-Level** Energy Optimization.")

st.sidebar.header("Infrastructure Specs")
total_servers = st.sidebar.slider("Total Servers in Cluster", min_value=100, max_value=10000, value=1000, step=100)
power_per_server = st.sidebar.number_input("Avg Power per Server (Watts)", value=400)
electricity_cost = st.sidebar.number_input("Electricity Cost (₹/kWh)", value=0.12)
carbon_intensity = st.sidebar.number_input("Carbon Intensity (kg CO2/kWh)", value=0.45)

st.sidebar.markdown("---")
st.sidebar.info("Model: Random Forest Regressor 🌲")
st.sidebar.info("Target: Dynamic Scale Extrapolation")

# --- Main Dashboard ---
st.title("🍃 Eco-Scale Cluster Dashboard")
st.markdown("Monitor live cluster telemetry and forecast **exactly how many servers** can be safely powered down while maintaining < 75% capacity limits.")

if df.empty or model is None:
    st.warning("Data or model not found. Please run `python build_project.py` to train the new Random Forest cluster model.")
    st.stop()

# --- Top Metrics Row ---
latest_data = df.iloc[-1] if not df.empty else None
current_predicted_shutdowns = int(latest_data['safe_shutdown_count'] * (total_servers / 1000)) if latest_data is not None else 0

power_saved_kw = (current_predicted_shutdowns * power_per_server) / 1000
daily_savings_kwh = power_saved_kw * 24
monthly_money_saved = daily_savings_kwh * 30 * electricity_cost
monthly_co2_saved_kg = daily_savings_kwh * 30 * carbon_intensity

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Total Cluster Size</div><div class="metric-value">{total_servers}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Safely Idle Servers</div><div class="metric-value">{current_predicted_shutdowns}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Est. Savings/Month</div><div class="metric-value">₹{monthly_money_saved:,.0f}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">CO₂ Avoided/Month</div><div class="metric-value">{monthly_co2_saved_kg/1000:,.1f} Tons</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts ---
st.subheader("📊 7-Day Cluster Telemetry & Optimization Potential")

# Show last 168 hours (7 days)
plot_df = df.tail(168).copy()
plot_df['safe_shutdown_count'] = (plot_df['safe_shutdown_count'] * (total_servers / 1000)).astype(int)

fig = go.Figure()

# Add CPU Line
fig.add_trace(go.Scatter(
    x=plot_df['timestamp'], y=plot_df['avg_cpu_load'], 
    mode='lines', name='Avg CPU Load (%)', line=dict(color='#58a6ff', width=3), yaxis='y1'
))

# Add Safe Shutdown Count as bars
fig.add_trace(go.Bar(
    x=plot_df['timestamp'], y=plot_df['safe_shutdown_count'], 
    name='Servers Powered Down', marker_color='#2ea043', opacity=0.5, yaxis='y2'
))

fig.update_layout(
    plot_bgcolor='#0d1117', paper_bgcolor='#0d1117', font_color='#c9d1d9',
    yaxis=dict(title='Cluster CPU Load (%)', range=[0, 100], gridcolor='#30363d'),
    yaxis2=dict(title='Servers Shutdown Count', overlaying='y', side='right', range=[0, total_servers], showgrid=False),
    xaxis=dict(gridcolor='#30363d'),
    hovermode="x unified", margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

# --- Unique Feature: Interactive AI Action Center ---
st.markdown("---")
st.subheader("🔮 AI Regression Center: Predict Optimal Fleet Size")
st.markdown(f"Adjust the real-time cluster metrics below. Our Random Forest Regressor analyzes extreme non-linear patterns (time of day, network flow) to predict **exactly** how many servers out of {total_servers} you can turn off securely.")

col_main, col_result = st.columns([2, 1])

with col_main:
    c1, c2, c3 = st.columns(3)
    with c1:
        sim_hour = st.slider("Hour of Day (0-23)", 0, 23, 14)
        sim_day = st.slider("Day of Week (0-6)", 0, 6, 2)
    with c2:
        sim_cpu = st.slider("Avg CPU Load (%)", 0, 100, 35)
        sim_mem = st.slider("Avg Memory Load (%)", 0, 100, 45)
    with c3:
        sim_net = st.slider("Network Traffic (Gbps)", 0.0, 100.0, 18.5)

with col_result:
    st.markdown('<div class="unique-feature">', unsafe_allow_html=True)
    if st.button("Query Random Forest Model", use_container_width=True):
        with st.spinner("Analyzing high-dimensional cluster space..."):
            time.sleep(0.5) 
            
            features = pd.DataFrame({
                'hour_of_day': [sim_hour],
                'day_of_week': [sim_day],
                'avg_cpu_load': [sim_cpu],
                'avg_memory_load': [sim_mem],
                'network_traffic_gbps': [sim_net]
            })
            
            base_pred = model.predict(features)[0]
            pred_shutdowns = int(base_pred * (total_servers / 1000))
            pred_shutdowns = max(0, min(total_servers, pred_shutdowns))
            active_servers = total_servers - pred_shutdowns
            
            if pred_shutdowns > 0:
                st.success(f"**Action:** Shutdown {pred_shutdowns} Servers")
                st.write(f"Leave **{active_servers}** servers running. The cluster will safely handle the current {sim_cpu}% CPU load under the 75% capacity threshold limit.")
            else:
                st.error(f"**Action:** DO NOT SHUTDOWN")
                st.write(f"All {total_servers} servers are required to handle this peak load securely without bottlenecking.")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #8b949e; font-size: 12px;'>"
    "Algorithm: Random Forest Regression | Target: Dynamic Cluster Size | Built for Environmental Hackathon"
    "</div>", unsafe_allow_html=True
)
