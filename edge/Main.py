from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

alert={"status":"No data received yet"}

class vestdata(BaseModel):
	minerid:str
	heartrate:int
	gaslevel:int
	moving:bool
	
@app.get("/")
def checkstatus():
	return{"status":"5G Edge Node Online"}

@app.post("/process")
def logic(data:vestdata):
	global alert

	score=0

	if data.gaslevel>100:
		score+=5
	elif data.gaslevel>50:
		score+=2

	if data.heartrate>130 or data.heartrate<50:
		score+=4
	elif data.heartrate>110:
		score+=3


	status="STABLE"

	if score>=8:
		status="CRITICAL"
	elif score>=5:
		status="WARNING"

	alert={"id":data.minerid,"category":status,"score":score,"timestamp":"Real-time 5G feed"}
	print(f"Miner {data.minerid} status: {status} (Score:{score})")

	return alert

@app.get("/status")
def getstatus():
	return alert