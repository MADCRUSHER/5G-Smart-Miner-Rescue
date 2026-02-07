from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

alert={"status":"No data received yet"}

class vestdata(BaseModel):
	minerid:str
	heartrate:int
	gaslevel:int
	temp:float
	
@app.get("/")
def checkstatus():
	return{"status":"5G Edge Node Online"}

@app.post("/process")
def logic(data: vestdata):
    global alert

    hr = data.heartrate
    gas = data.gaslevel
    temp = data.temp

    score = 0

    # ---- GAS (±5 ppm buffer) ----
    if gas > 105:
        score += 5
    elif gas > 55:
        score += 2

    # ---- HEART RATE (±5 BPM buffer) ----
    if hr > 135 or hr < 45:
        score += 4
    elif hr > 115:
        score += 3

    # ---- TEMPERATURE (±0.5°C buffer) ----
    if temp > 40.5:
        score += 4
    elif temp > 37.5:
        score += 2

    status = "STABLE"
    if score >= 8:
        status = "CRITICAL"
    elif score >= 5:
        status = "WARNING"

    alert = {
        "id": data.minerid,
        "category": status,
        "score": score,
        "heartrate": hr,
        "gaslevel": gas,
        "temp": temp,
        "timestamp": "Real-time 5G feed"
    }

    print(f"Miner {data.minerid}: {status} | Score={score}")
    return alert


@app.get("/status")
def getstatus():
	return alert



