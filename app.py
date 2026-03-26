import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import joblib
import time

# --- Configuration & Styling ---
st.set_page_config(page_title="Eco-Scale Dashboard", page_icon="🍃", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for Eco-Dark theme
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    .css-1d391kg {
        background-color: #161b22;
    }
    .metric-card {
        background-color: #21262d;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        border-left: 5px solid #2ea043;
    }
    .metric-value {
        font-size: 36px;
        font-weight: bold;
        color: #2ea043;
    }
    .metric-title {
        font-size: 14px;
        color: #8b949e;
        text-transform: uppercase;
    }
    h1, h2, h3 {
        color: #58a6ff;
    }
    .unique-feature {
        background: linear-gradient(135deg, #13233a 0%, #0d1117 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 25px;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Data Loading ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("server_telemetry.csv")
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except FileNotFoundError:
        # Fallback empty dataframe if not generated yet
        return pd.DataFrame(columns=['timestamp', 'machine_id', 'cpu_utilization', 'memory_utilization', 'is_underutilized'])

@st.cache_resource
def load_model():
    try:
        return joblib.load("logistic_model.pkl")
    except FileNotFoundError:
        return None

df = load_data()
model = load_model()

# --- Sidebar ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3063/3063124.png", width=60) # Eco icon
st.sidebar.title("Eco-Scale Control")
st.sidebar.markdown("Predictive Energy Optimization for Cloud Infrastructure.")

st.sidebar.header("Simulator Settings")
# Interactive settings for the ROI / Carbon simulator
cluster_size = st.sidebar.slider("Total Servers in Cluster", min_value=100, max_value=10000, value=1000, step=100)
power_per_server = st.sidebar.number_input("Avg Power per Server (Watts)", value=400)
electricity_cost = st.sidebar.number_input("Electricity Cost ($/kWh)", value=0.12)
carbon_intensity = st.sidebar.number_input("Carbon Intensity (kg CO2/kWh)", value=0.45) # Global avg

st.sidebar.markdown("---")
st.sidebar.info("Developed for international level competition. 🏆")

# --- Main Dashboard ---
st.title("🍃 Eco-Scale Predictive Dashboard")
st.markdown("Monitor live telemetry, forecast underutilization using AI, and calculate environmental impact.")

if df.empty or model is None:
    st.warning("Data or model not found. Please run the ML pipeline first.")
    st.stop()

# --- Top Metrics Row ---
# Calculate simulation metrics based on user input
latest_data = df[df['timestamp'] == df['timestamp'].max()]
underutilized_ratio = latest_data['is_underutilized'].mean() if not latest_data.empty else 0.35

consolidation_potential = int(cluster_size * underutilized_ratio)
power_saved_kw = (consolidation_potential * power_per_server) / 1000
daily_savings_kwh = power_saved_kw * 24
monthly_money_saved = daily_savings_kwh * 30 * electricity_cost
monthly_co2_saved_kg = daily_savings_kwh * 30 * carbon_intensity

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Servers Online</div><div class="metric-value">{cluster_size}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Predicted Idle</div><div class="metric-value">{consolidation_potential}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-title">Est. Savings/Month</div><div class="metric-value">${monthly_money_saved:,.0f}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-title">CO₂ Avoided/Month</div><div class="metric-value">{monthly_co2_saved_kg/1000:,.1f} Tons</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- Charts ---
st.subheader("📊 Infrastructure Telemetry Forecast")

# Aggregate data for charting
agg_df = df.groupby('timestamp').agg(
    avg_cpu=('cpu_utilization', 'mean'),
    idle_count=('is_underutilized', 'sum')
).reset_index()

# Interactive Plotly Chart
fig = go.Figure()

# Add CPU Line
fig.add_trace(go.Scatter(
    x=agg_df['timestamp'], 
    y=agg_df['avg_cpu'], 
    mode='lines', 
    name='Avg CPU Load (%)', 
    line=dict(color='#58a6ff', width=3)
))

# Calculate the safe consolidation zone
safe_upper_bound = 100 - agg_df['avg_cpu'] 

# Create the beautiful filled area for wasted energy
fig.add_trace(go.Scatter(
    x=pd.concat([agg_df['timestamp'], agg_df['timestamp'][::-1]]),
    y=pd.concat([agg_df['avg_cpu'], pd.Series([100]*len(agg_df))]),
    fill='toself',
    fillcolor='rgba(255, 69, 58, 0.1)',
    line=dict(color='rgba(255,255,255,0)'),
    hoverinfo="skip",
    showlegend=True,
    name='Wasted Energy Potential'
))

fig.update_layout(
    plot_bgcolor='#0d1117',
    paper_bgcolor='#0d1117',
    font_color='#c9d1d9',
    yaxis=dict(title='CPU Load (%)', range=[0, 100], gridcolor='#30363d'),
    xaxis=dict(gridcolor='#30363d'),
    hovermode="x unified",
    margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
)
st.plotly_chart(fig, use_container_width=True)

# --- Unique Feature: Interactive AI Action Center ---
st.markdown("---")
st.subheader("🔮 AI Action Center: Real-Time Prediction")
st.markdown("Enter simulated current metrics for a specific machine to ping the ML API layer and get a consolidation recommendation.")

col_a, col_b, col_c = st.columns([1, 1, 2])
with col_a:
    sim_cpu = st.slider("Current CPU (%)", 0, 100, 15)
with col_b:
    sim_mem = st.slider("Current Memory (%)", 0, 100, 45)

with col_c:
    st.markdown('<div class="unique-feature">', unsafe_allow_html=True)
    if st.button("Query ML Model", use_container_width=True):
        with st.spinner("Analyzing telemetry..."):
            time.sleep(0.5) # Simulate API latency
            
            # Predict
            features = pd.DataFrame({'cpu_utilization': [sim_cpu], 'memory_utilization': [sim_mem]})
            pred = model.predict(features)[0]
            prob = model.predict_proba(features)[0][1]
            
            if pred == 1:
                st.success(f"**Action Recommended:** SAFELY POWER DOWN (Confidence: {prob:.1%})")
                st.write("This machine is forecasted to remain vastly underutilized. Workloads can be migrated.")
            else:
                st.error(f"**Action Recommended:** KEEP ACTIVE (Confidence: {1-prob:.1%})")
                st.write("This machine is operating within necessary bounds or is forecasted to spike.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- Footer ---
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #8b949e; font-size: 12px;'>"
    "Data Source: Simulated Alibaba Cluster Trace | Algorithm: Logistic Regression | Built for Global Hackathon Series"
    "</div>", 
    unsafe_allow_html=True
)
