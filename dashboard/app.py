import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import time

EDGE_URL = "https://fiveg-smart-miner-rescue.onrender.com/status"

st.set_page_config(layout="wide")
st.title("🚨 5G Smart Miner Rescue Command Center")

# ---------------- FETCH DATA ---------------- #

def fetch_data():
    try:
        response = requests.get(EDGE_URL, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

data = fetch_data()

if not data or "miners" not in data:
    st.warning("Waiting for miner data from Edge...")
    st.stop()

miners = data["miners"]

# ---------------- PRIORITY SORT ---------------- #

priority_order = {
    "DECEASED": 4,
    "CRITICAL": 3,
    "MONITOR": 2,
    "STABLE": 1
}

miners_sorted = sorted(
    miners,
    key=lambda x: priority_order.get(x["category"], 0),
    reverse=True
)

# ---------------- STATUS BAR ---------------- #

critical_count = len([m for m in miners if m["category"] == "CRITICAL"])

col1, col2, col3 = st.columns(3)
col1.metric("Edge Gateway", "ONLINE")
col2.metric("Total Miners", len(miners))
col3.metric("Critical Alerts", critical_count)

st.divider()

left, right = st.columns([1, 2])

# ---------------- TRIAGE PANEL ---------------- #

with left:
    st.subheader("🔥 Triage Priority")

    for miner in miners_sorted:
        category = miner["category"]

        color = "#2ecc71"
        if category == "CRITICAL":
            color = "#e74c3c"
        elif category == "MONITOR":
            color = "#f39c12"
        elif category == "DECEASED":
            color = "#8e44ad"

        st.markdown(
            f"""
            <div style="
                padding:12px;
                margin-bottom:10px;
                border-radius:10px;
                background-color:{color};
                color:white;
                font-weight:bold;
            ">
            {miner['id']}
            <br>Status: {category}
            <br>Heart Rate: {miner['heartrate']}
            <br>Gas Level: {miner['gas level']}
            <br>Temperature: {miner['Temp']}
            </div>
            """,
            unsafe_allow_html=True
        )

# ---------------- GRAPHS ---------------- #

with right:
    st.subheader("📊 Live Vital Monitoring")

    df = pd.DataFrame([
        {
            "Miner": m["id"],
            "Heart Rate": m["heartrate"],
            "Gas Level": m["gas level"],
            "Status": m["category"]
        }
        for m in miners
    ])

    # Heart Rate Graph
    st.markdown("### ❤️ Heart Rate Levels")
    fig_hr = px.bar(
        df,
        x="Miner",
        y="Heart Rate",
        color="Miner",
        text="Heart Rate"
    )
    fig_hr.update_layout(height=350)
    st.plotly_chart(fig_hr, use_container_width=True)

    # Gas Level Graph
    st.markdown("### ☣️ Gas Levels")
    fig_gas = px.bar(
        df,
        x="Miner",
        y="Gas Level",
        color="Miner",
        text="Gas Level"
    )
    fig_gas.update_layout(height=350)
    st.plotly_chart(fig_gas, use_container_width=True)

# ---------------- FOOTER ---------------- #

st.divider()
st.caption(f"Last Update: {data.get('timestamp', 'Unknown')}")

# Auto refresh
time.sleep(2)
st.rerun()
