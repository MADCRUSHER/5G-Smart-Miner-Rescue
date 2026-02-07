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

    # Final sanity clamps (edge safety)
    hr = max(40, min(data.heartrate, 180))
    gas = max(0, min(data.gaslevel, 300))
    temp = max(10, min(data.temp, 60))

    score = 0

    # Gas logic
    if gas > 100:
        score += 5
    elif gas > 50:
        score += 2

    # Heart rate logic
    if hr > 130 or hr < 50:
        score += 4
    elif hr > 110:
        score += 3

    # Temperature logic
    if temp > 40:
        score += 4
    elif temp > 37:
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

    print(f"Miner {data.minerid} → {status} | Score: {score}")
    return alert

@app.get("/status")
def getstatus():
	return alert


