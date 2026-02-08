import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

# ==============================
# CONFIG
# ==============================

st.set_page_config(
    page_title="5G Smart Miner Control Room",
    layout="wide"
)

EDGE_URL = "https://fiveg-smart-miner-rescue.onrender.com/status"

# ==============================
# SESSION STATE INIT
# ==============================

if "history_hr" not in st.session_state:
    st.session_state.history_hr = []

if "history_gas" not in st.session_state:
    st.session_state.history_gas = []

if "history_temp" not in st.session_state:
    st.session_state.history_temp = []

# ==============================
# FETCH EDGE DATA
# ==============================

def fetch_data():
    try:
        response = requests.get(EDGE_URL, timeout=5)

        if response.status_code != 200:
            return None

        data = response.json()

        if "miners" in data and len(data["miners"]) > 0:
            return data["miners"][0]   # Always take first miner

        return None

    except Exception as e:
        st.write("Connection Error:", e)
        return None

# ==============================
# MAIN UI
# ==============================

st.title("🚨 5G Smart Miner Rescue Command Center")

data = fetch_data()

if not data:
    st.error("⚠️ Unable to fetch data from Edge")
    st.stop()

# ==============================
# SAFE FIELD EXTRACTION
# ==============================

miner_id = data.get("id", "Miner 1")
status = data.get("category", "UNKNOWN")

hr = data.get("heartrate") or data.get("hr") or 0
gas = data.get("gasLevel") or data.get("gaslevel") or data.get("gas level") or 0
temp = data.get("temperature") or data.get("temp") or data.get("Temp") or 0
score = data.get("score") or 0

# ==============================
# STORE HISTORY
# ==============================

st.session_state.history_hr.append(hr)
st.session_state.history_gas.append(gas)
st.session_state.history_temp.append(temp)

st.session_state.history_hr = st.session_state.history_hr[-40:]
st.session_state.history_gas = st.session_state.history_gas[-40:]
st.session_state.history_temp = st.session_state.history_temp[-40:]

# ==============================
# STATUS BAR
# ==============================

col1, col2, col3, col4 = st.columns(4)

col1.metric("Miner ID", miner_id)
col2.metric("Status", status)
col3.metric("Severity Score", score)
col4.metric("Edge Gateway", "ONLINE")

st.divider()

# ==============================
# COLOR LOGIC
# ==============================

status_color = {
    "STABLE": "#2ecc71",
    "MONITOR": "#f39c12",
    "CRITICAL": "#e74c3c",
    "DECEASED": "#000000"
}.get(status, "gray")

st.markdown(
    f"""
    <div style="
        padding:20px;
        border-radius:12px;
        background-color:{status_color};
        color:white;
        font-size:22px;
        font-weight:bold;
        text-align:center;
        box-shadow: 0px 0px 20px rgba(255,0,0,0.4);
    ">
        Miner 1 Condition: {status}
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()

# ==============================
# GRAPHS SECTION
# ==============================

col1, col2, col3 = st.columns(3)

# ------------------------------
# HEART RATE GRAPH
# ------------------------------

with col1:
    st.subheader("❤️ Heart Rate")

    df_hr = pd.DataFrame({
        "Time": list(range(len(st.session_state.history_hr))),
        "Heart Rate": st.session_state.history_hr
    })

    fig_hr = px.line(
        df_hr,
        x="Time",
        y="Heart Rate",
        line_shape="spline"
    )

    fig_hr.update_traces(line_color="red")
    fig_hr.update_layout(height=350)

    # Add danger zones
    fig_hr.add_hline(y=1000, line_dash="dash", line_color="red")

    st.plotly_chart(fig_hr, use_container_width=True)

# ------------------------------
# GAS GRAPH
# ------------------------------

with col2:
    st.subheader("☁️ Gas Level")

    df_gas = pd.DataFrame({
        "Time": list(range(len(st.session_state.history_gas))),
        "Gas Level": st.session_state.history_gas
    })

    fig_gas = px.line(
        df_gas,
        x="Time",
        y="Gas Level",
        line_shape="spline"
    )

    fig_gas.update_traces(line_color="orange")
    fig_gas.update_layout(height=350)

    # Add thresholds
    fig_gas.add_hline(y=700, line_dash="dash", line_color="orange")
    fig_gas.add_hline(y=750, line_dash="dash", line_color="red")

    st.plotly_chart(fig_gas, use_container_width=True)

# ------------------------------
# TEMPERATURE GRAPH
# ------------------------------

with col3:
    st.subheader("🌡️ Temperature")

    df_temp = pd.DataFrame({
        "Time": list(range(len(st.session_state.history_temp))),
        "Temperature": st.session_state.history_temp
    })

    fig_temp = px.line(
        df_temp,
        x="Time",
        y="Temperature",
        line_shape="spline"
    )

    fig_temp.update_traces(line_color="purple")
    fig_temp.update_layout(height=350)

    # Dynamic zoom scaling
    if len(st.session_state.history_temp) > 0:
        min_temp = min(st.session_state.history_temp)
        max_temp = max(st.session_state.history_temp)

        padding = 0.5  # zoom sensitivity
        fig_temp.update_yaxes(range=[min_temp - padding, max_temp + padding])

    # Threshold lines
    fig_temp.add_hline(y=39.5, line_dash="dash", line_color="orange")
    fig_temp.add_hline(y=41.5, line_dash="dash", line_color="red")

    st.plotly_chart(fig_temp, use_container_width=True)

# ==============================
# AUTO REFRESH
# ==============================

time.sleep(1)
st.rerun()
