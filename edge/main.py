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

    # RAW ADC values (0–1023)
    hr_raw = data.heartrate
    gas_raw = data.gaslevel
    temp = data.temp  # already ~36–47

    score = 0

    # ========== GAS (PRIMARY INDICATOR) ==========
    # Typical raw gas values you observed: ~90–120 (can rise)
    if gas_raw >= 700:
        score += 6          # extreme gas
    elif gas_raw >= 500:
        score += 4          # high gas
    elif gas_raw >= 300:
        score += 2          # mild anomaly

    # ========== HEART RATE (RAW ADC) ==========
    # Floating / high raw means stress / bad contact
    if hr_raw >= 800:
        score += 3
    elif hr_raw >= 600:
        score += 2
    elif hr_raw >= 400:
        score += 1

    # ========== TEMPERATURE ==========
    # Your formula already gives ~36.5–46
    if temp >= 42:
        score += 3
    elif temp >= 39:
        score += 2
    elif temp >= 37.5:
        score += 1

    # ========== FINAL SEVERITY ==========
    if score >= 8:
        status = "CRITICAL"
    elif score >= 4:
        status = "WARNING"
    else:
        status = "STABLE"

    alert = {
        "id": data.minerid,
        "category": status,
        "score": score,
        "heartrate_raw": hr_raw,
        "gaslevel_raw": gas_raw,
        "temp": temp,
        "timestamp": "Real-time 5G feed"
    }

    print(
        f"{data.minerid} | "
        f"HR_RAW={hr_raw}, GAS_RAW={gas_raw}, TEMP={temp:.1f} → {status}"
    )

    return alert


@app.get("/status")
def getstatus():
	return alert




