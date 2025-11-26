#Fastapi imports
from typing import Union
from fastapi import FastAPI
app = FastAPI()

#for mac address validation
import re

#Function to validate mac address
def is_valid_mac(mac: str) -> bool:
    # Regular expression for validating a MAC address
    mac_regex = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    return bool(mac_regex.match(mac))   


#Root endpoint
@app.get("/")
def read_root():
    return {"msg": "Welcome to POTAP project"}

#Progress endpoint
@app.get("/progress/mac={mac_address}&ip={ip_address}&progress={progress_value}")
def read_item(mac_address: str, ip_address: str, progress_value: int):
    # Validate MAC address
    if not is_valid_mac(mac_address):
        # Return error if MAC address is invalid
        return {"error": "Invalid MAC address format"}
    return {"item_id": mac_address, "ip": ip_address, "progress": progress_value}

