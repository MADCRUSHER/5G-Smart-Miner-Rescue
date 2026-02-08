import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

st.set_page_config(
    page_title="5G Smart Miner Control Room",
    layout="wide"
)

EDGE_URL = "https://fiveg-smart-miner-rescue.onrender.com/status"

# ---------------- SESSION STATE ----------------

if "history_hr" not in st.session_state:
    st.session_state.history_hr = []
if "history_gas" not in st.session_state:
    st.session_state.history_gas = []
if "history_temp" not in st.session_state:
    st.session_state.history_temp = []

# ---------------- FETCH DATA ----------------

def fetch_data():
    try:
        response = requests.get(EDGE_URL, timeout=5)
        if response.status_code != 200:
            return None

        data = response.json()

        if "miners" in data and len(data["miners"]) > 0:
            return data["miners"][0]

        return None
    except:
        return None

st.title("🚨 5G Smart Miner Rescue Command Center")

data = fetch_data()

if not data:
    st.error("⚠️ Unable to fetch data from Edge")
    st.stop()

# ---------------- EXTRACT FIELDS ----------------

miner_id = data.get("id", "Unknown")
status = data.get("category", "UNKNOWN")

hr = data.get("heartrate", 0)
gas = data.get("gas level", 0)
temp = data.get("Temp", 0)

# ---------------- STORE HISTORY ----------------

st.session_state.history_hr.append(hr)
st.session_state.history_gas.append(gas)
st.session_state.history_temp.append(temp)

st.session_state.history_hr = st.session_state.history_hr[-40:]
st.session_state.history_gas = st.session_state.history_gas[-40:]
st.session_state.history_temp = st.session_state.history_temp[-40:]

# ---------------- STATUS BAR ----------------

col1, col2, col3 = st.columns(3)

col1.metric("Miner ID", miner_id)
col2.metric("Heart Rate", hr)
col3.metric("Gas Level", gas)

# ---------------- CRITICAL VISUAL ALERT ----------------

if status == "CRITICAL":
    st.markdown(
        """
        <div style="
            padding:25px;
            border-radius:15px;
            background-color:#e74c3c;
            color:white;
            font-size:28px;
            font-weight:bold;
            text-align:center;
            animation: blink 1s infinite;
        ">
            🚨 CRITICAL CONDITION DETECTED 🚨
        </div>

        <style>
        @keyframes blink {
            0% {opacity: 1;}
            50% {opacity: 0.5;}
            100% {opacity: 1;}
        }
        </style>
        """,
        unsafe_allow_html=True
    )

elif status == "DECEASED":
    st.markdown(
        """
        <div style="
            padding:25px;
            border-radius:15px;
            background-color:black;
            color:red;
            font-size:28px;
            font-weight:bold;
            text-align:center;
        ">
            ☠️ MINER DECEASED ☠️
        </div>
        """,
        unsafe_allow_html=True
    )

elif status == "MONITOR":
    st.markdown(
        """
        <div style="
            padding:20px;
            border-radius:12px;
            background-color:#f39c12;
            color:white;
            font-size:22px;
            font-weight:bold;
            text-align:center;
        ">
            ⚠️ MONITOR CLOSELY
        </div>
        """,
        unsafe_allow_html=True
    )

else:
    st.success("✅ STABLE CONDITION")

st.divider()

# ---------------- GRAPHS ----------------

col1, col2, col3 = st.columns(3)

# HEART RATE
with col1:
    df_hr = pd.DataFrame({
        "Time": range(len(st.session_state.history_hr)),
        "HR": st.session_state.history_hr
    })

    fig_hr = px.line(df_hr, x="Time", y="HR", markers=True)
    fig_hr.update_traces(line=dict(color="red", width=3))
    fig_hr.update_layout(height=350)
    st.plotly_chart(fig_hr, use_container_width=True)

# GAS
with col2:
    df_gas = pd.DataFrame({
        "Time": range(len(st.session_state.history_gas)),
        "Gas": st.session_state.history_gas
    })

    fig_gas = px.line(df_gas, x="Time", y="Gas", markers=True)
    fig_gas.update_traces(line=dict(color="orange", width=3))
    fig_gas.update_layout(height=350)
    st.plotly_chart(fig_gas, use_container_width=True)

# TEMP
with col3:
    df_temp = pd.DataFrame({
        "Time": range(len(st.session_state.history_temp)),
        "Temp": st.session_state.history_temp
    })

    fig_temp = px.line(df_temp, x="Time", y="Temp", markers=True)
    fig_temp.update_traces(line=dict(color="purple", width=3))
    fig_temp.update_layout(height=350)

    if len(st.session_state.history_temp) > 0:
        min_temp = min(st.session_state.history_temp)
        max_temp = max(st.session_state.history_temp)
        fig_temp.update_layout(yaxis_range=[min_temp - 0.5, max_temp + 0.5])

    st.plotly_chart(fig_temp, use_container_width=True)

time.sleep(1)
st.rerun()
