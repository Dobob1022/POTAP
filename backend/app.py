#Fastapi imports
from typing import Union
from fastapi import FastAPI
app = FastAPI()

#import db module
from module import db

#import proxmoxer module
from module import proxmox

#for mac address validation
import re

#for load dot\env
from dotenv import load_dotenv
load_dotenv()

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

@app.get("/vms")
def get_vms():
    """Returns list of all VMs from database"""
    db_session = next(db.get_db())
    vms = db_session.query(db.VmInfo).all()
    return vms

@app.post("/vms")
def create_vm(mac_address: str, hostname: str, template: str):
    """Create a new VM entry in the database"""
    db_session = next(db.get_db())
    new_vm = db.add_vm(db_session, mac_address, hostname, template)
    return new_vm

## test proxmox connection with next vmid
@app.get("/proxmox/next_vmid")
def proxmox_get_next_vmid():
    """Returns next available VMID from Proxmox server"""
    try:
        vmid = proxmox.get_next_vmid()
        return {"next_vmid": vmid}
    except Exception as e:
        return {"error": str(e)}
    
# Add OS templete creation endpoint
@app.post("/templete")
def create_templete():
    """Create OS templete"""
    try:
        ## ADD TEMPLETE CREATION LOGIC HERE
        return {"status": "OK"}
    except Exception as e:
        return {"error": str(e)}
