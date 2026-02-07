import serial
import time
import requests
COM_PORT = "COM7"
BAUD_RATE = 9600
URL = "https://fiveg-smart-miner-rescue.onrender.com/process"
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
time.sleep(3)  # allow Arduino to reboot fully
print("Gateway running...")
try:
    while True:
        if ser.in_waiting:
            raw = ser.readline()
            try:
                line = raw.decode("utf-8").strip()
            except UnicodeDecodeError:
                continue
            # Skip junk / empty lines
            if not line or "," not in line:
                continue
            parts = line.split(",")
            if len(parts) != 3:
                continue
            try:
                heartrate = int(parts[0])
                gaslevel = int(parts[1])
                temp = float(parts[2])
            except ValueError:
                continue
            payload = {
                "minerid": "Miner_01",
                "heartrate": heartrate,
                "gaslevel": gaslevel,
                "temp": temp   #
            }
            response = requests.post(URL, json=payload, timeout=10)
            print("Sent:", payload)
            print("Status:", response.status_code)
            print("-" * 40)
except KeyboardInterrupt:
    print("Stopping gateway")
    ser.close()
