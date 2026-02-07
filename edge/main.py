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
def logic(data:vestdata):
	global alert

	hrate=data.heartrate
	gas=data.gaslevel
	temp=data.temp
	score=0

	if gas>=750:
		score+=6
	elif gas>=700:
		score+=3

	if hrate>=1000:
		score+=2
	elif hrate<=905:
		score=10

	if temp>=41.5:
		score+=6
	elif temp>=39.5:
		score+=3
	elif temp<=37.2:
		score=10


	
	def status(score):
		if score==10:
			return"DECEASED"
		elif score>=8:
			return"CRITICAL"
		elif score>=5:
			return"MONITOR"
		else:
			return"STABLE"
	booga=status(score)

	miners=[]
	miners.append({"id":data.minerid,"category":booga,"heartrate":hrate,"gas level":gas,"Temp":temp})
	miners.append({"id":"Miner 102","category":"WARNING","heartrate":int(hrate*0.75),"gas level":int(gas*0.6),"Temp":round(temp-1.5,1)})
	miners.append({"id":"Miner 103","category":"MONITOR","heartrate":int(hrate*0.4),"gas level":int(gas*0.3),"Temp":round(temp-3,1)})
	miners.append({"id":"Miner 104","category":"STABLE","heartrate":int(hrate*0.35),"gas level":int(gas*0.25),"Temp":round(temp-2.5,1)})

	alert ={ "miners":miners,"timestamp":"Real-time 5G feed"}
	return alert

@app.get("/status")
def getstatus():
	return alert