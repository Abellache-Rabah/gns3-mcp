
import sys
import os
sys.path.append(os.getcwd())
from shared.gns3_utils import GNS3Console

def get_router_status():
    print("Connecting to router...")
    try:
        console = GNS3Console("localhost", 5006, platform="cisco_ios")
        console.connect()
        interfaces = console.get_interfaces()
        console.close()
        print("Interfaces:")
        for iface in interfaces:
            print(iface)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_router_status()
