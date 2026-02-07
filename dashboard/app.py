import streamlit as st
import random
import time
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(
    page_title="5G Smart Miner Control Room",
    layout="wide"
)

EDGE_URL = "http://localhost:8000/process"

# ---------------- SEND DATA TO EDGE ---------------- #

def send_to_edge(miner_data):
    try:
        response = requests.post(EDGE_URL, json={
            "minerid": miner_data["id"],
            "heartrate": miner_data["hr"],
            "gaslevel": miner_data["gas"],
            "moving": miner_data["movement"]
        })

        if response.status_code == 200:
            return response.json()
        else:
            return None
    except:
        return None


# ---------------- INITIAL STATE ---------------- #

if "miners_state" not in st.session_state:
    affected = random.sample([f"M{i}" for i in range(1, 6)], 2)

    st.session_state.miners_state = {
        f"M{i}": {
            "hr": random.randint(70, 85),
            "gas": random.randint(10, 20),
            "movement": True,
            "x": random.randint(1, 10),
            "y": random.randint(1, 10),
            "time": 0,
            "event": f"M{i}" in affected
        }
        for i in range(1, 6)
    }

if "logs" not in st.session_state:
    st.session_state.logs = []

if "history" not in st.session_state:
    st.session_state.history = {}


# ---------------- SIMULATION + EDGE PROCESSING ---------------- #

def update_miners():
    miners = []

    for miner_id, state in st.session_state.miners_state.items():
        state["time"] += 1

        # Normal fluctuation
        state["hr"] += random.randint(-2, 2)
        state["hr"] = max(60, min(state["hr"], 180))

        state["gas"] += random.randint(-1, 1)
        state["gas"] = max(5, min(state["gas"], 150))

        # Gradual deterioration for selected miners
        if state["event"] and state["time"] > 8:
            state["gas"] += random.randint(3, 6)
            state["hr"] += random.randint(3, 7)

            if state["gas"] > 80:
                state["movement"] = False

        miner_payload = {
            "id": miner_id,
            "hr": state["hr"],
            "gas": state["gas"],
            "movement": state["movement"]
        }

        # Send to Edge
        edge_result = send_to_edge(miner_payload)

        if edge_result:
            status = edge_result["Health"]
            severity = edge_result["Score"]
        else:
            status = "UNKNOWN"
            severity = 0

        miner_data = {
            "id": miner_id,
            "hr": state["hr"],
            "gas": state["gas"],
            "movement": state["movement"],
            "severity": severity,
            "status": status,
            "x": state["x"],
            "y": state["y"]
        }

        miners.append(miner_data)

        # Store HR history
        if miner_id not in st.session_state.history:
            st.session_state.history[miner_id] = []

        st.session_state.history[miner_id].append(state["hr"])

        # Log CRITICAL once
        if status == "CRITICAL":
            log_entry = f"[EDGE] {miner_id} CRITICAL | HR={state['hr']} | Gas={state['gas']} → Drone Dispatched"
            if log_entry not in st.session_state.logs:
                st.session_state.logs.append(log_entry)

    return sorted(miners, key=lambda x: x["severity"], reverse=True)


# ---------------- MAIN UI ---------------- #

st.title("🚨 5G Smart Miner Rescue Command Center")

miners = update_miners()

critical_count = len([m for m in miners if m["status"] == "CRITICAL"])

# -------- STATUS BAR -------- #

col1, col2, col3 = st.columns(3)

col1.metric("Edge Gateway", "ONLINE")
col2.metric("Total Miners", len(miners))
col3.metric("Critical Alerts", critical_count)

st.divider()

# -------- MAIN LAYOUT -------- #

left, center, right = st.columns([1.2, 1.5, 1.2])

# -------- TRIAGE PANEL -------- #

with left:
    st.subheader("🔥 Triage Priority")

    for miner in miners:
        color = "#2ecc71"
        if miner["status"] == "CRITICAL":
            color = "#e74c3c"
        elif miner["status"] == "WARNING":
            color = "#f39c12"
        elif miner["status"] == "UNKNOWN":
            color = "#95a5a6"

        st.markdown(
            f"""
            <div style="
                padding:12px;
                margin-bottom:8px;
                border-radius:10px;
                background-color:{color};
                color:white;
                font-weight:bold;
            ">
            {miner['id']} | HR: {miner['hr']} | Gas: {miner['gas']}
            <br>Status: {miner['status']} | Severity: {miner['severity']}
            </div>
            """,
            unsafe_allow_html=True
        )

# -------- MINE MAP -------- #

with center:
    st.subheader("🗺 Mine Map")

    map_df = pd.DataFrame([
        {
            "Miner": m["id"],
            "X": m["x"],
            "Y": m["y"],
            "Status": m["status"]
        }
        for m in miners
    ])

    fig_map = px.scatter(
        map_df,
        x="X",
        y="Y",
        color="Status",
        hover_name="Miner",
        size=[15]*len(map_df),
        color_discrete_map={
            "STABLE": "green",
            "WARNING": "orange",
            "CRITICAL": "red",
            "UNKNOWN": "gray"
        }
    )

    fig_map.update_layout(height=400)
    st.plotly_chart(fig_map, use_container_width=True)

# -------- HEART RATE GRAPH -------- #

with right:
    st.subheader("📊 Heart Rate Trends")

    vitals_df = pd.DataFrame()

    for miner_id in st.session_state.history:
        hr_history = st.session_state.history[miner_id][-20:]
        temp_df = pd.DataFrame({
            "Time": list(range(len(hr_history))),
            "Heart Rate": hr_history,
            "Miner": miner_id
        })
        vitals_df = pd.concat([vitals_df, temp_df])

    if not vitals_df.empty:
        fig_line = px.line(
            vitals_df,
            x="Time",
            y="Heart Rate",
            color="Miner",
            title="Live Heart Rate Monitoring"
        )

        fig_line.update_layout(height=400)
        st.plotly_chart(fig_line, use_container_width=True)

# -------- DECISION LOG -------- #

st.divider()
st.subheader("📜 Decision Log")

for log in reversed(st.session_state.logs[-10:]):
    st.text(log)

# -------- AUTO REFRESH -------- #

time.sleep(2)
st.rerun()
