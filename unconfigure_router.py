
import sys
import os
sys.path.append(os.getcwd())
from shared.gns3_utils import GNS3Console

def unconfigure_router():
    print("Connecting to router to unconfigure...")
    try:
        console = GNS3Console("localhost", 5006, platform="cisco_ios")
        console.connect()
        console.configure_cisco("interface Ethernet0/0\nno ip address")
        console.close()
        print("Router unconfigured.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    unconfigure_router()
