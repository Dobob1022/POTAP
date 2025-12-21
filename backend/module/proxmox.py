import os
import re
import urllib3
from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv

# 1. .env 파일 로드 (프로젝트 루트의 .env를 찾습니다)
load_dotenv()

# SSL 경고 무시
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 2. 환경 변수 가져오기
PROXMOX_HOST = os.getenv("PROXMOX_HOST")
PROXMOX_USER = os.getenv("PROXMOX_USER")
PROXMOX_PASSWORD = os.getenv("PROXMOX_PASSWORD")
PROXMOX_NODE = os.getenv("PROXMOX_NODE", "pve")  # 기본값 'pve'
# 문자열 "true" 여부를 확인하여 boolean으로 변환
PROXMOX_VERIFY_SSL = os.getenv("PROXMOX_VERIFY_SSL", "false").lower() == "true"

# 3. Proxmox 연결 인스턴스 생성 (모듈 로드 시 실행됨)
proxmox = ProxmoxAPI(
    PROXMOX_HOST,
    user=PROXMOX_USER,
    password=PROXMOX_PASSWORD,
    verify_ssl=PROXMOX_VERIFY_SSL
)

def get_next_vmid():
    """사용 가능한 다음 VM ID를 가져옵니다."""
    cluster = proxmox.cluster.nextid.get()
    return cluster

# [수정됨] disk_size 위치 변경 (기본값이 없는 인자는 기본값이 있는 인자보다 앞에 와야 함)
def create_pxe_vm(vmid, name, disk_size, memory=2048, cores=2, bridge1="route", bridge2="mirror"):
    """
    PXE 부팅을 위한 VM을 생성합니다.
    """
    try:
        # VM 생성 설정
        config = {
            "vmid": vmid,
            "name": name,
            "memory": memory,
            "cores": cores,
            "sockets": 1,
            "net0": f"virtio,bridge={bridge1}",
            "net1": f"virtio,bridge={bridge2}",
            "scsihw": "virtio-scsi-pci",
            "boot": "order=net0;scsi0",       # [중요] PXE(net0) 우선 부팅
            "ostype": "l26",                  # Linux Kernel 2.6+
            "scsi0": f"data-disk2:{disk_size}", # 스토리지:크기 (GB)
        }
        
        # VM 생성 요청
        proxmox.nodes(PROXMOX_NODE).qemu.create(**config)
        return {"status": "success", "vmid": vmid}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_vm_mac(vmid):
    """특정 VM의 MAC 주소를 조회합니다."""
    try:
        config = proxmox.nodes(PROXMOX_NODE).qemu(vmid).config.get()
        # net0 설정 값 가져오기
        net0_config = config.get("net0", "")
        
        # 정규식으로 MAC 주소 추출
        match = re.search(r'([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})', net0_config)
        if match:
            return match.group(0)
        return None
    except Exception as e:
        print(f"Error getting MAC: {e}")
        return None

def start_vm(vmid):
    """VM 시작"""
    return proxmox.nodes(PROXMOX_NODE).qemu(vmid).status.start.post()

def stop_vm(vmid):
    """VM 강제 종료"""
    return proxmox.nodes(PROXMOX_NODE).qemu(vmid).status.stop.post()

def delete_vm(vmid):
    """VM 삭제"""
    return proxmox.nodes(PROXMOX_NODE).qemu(vmid).delete()