from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List, Optional
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from shared.gns3_utils import GNS3Console, load_inventory

mcp = FastMCP("Observer Server")

# Mock Live State (simulating GNS3)
LIVE_STATE = {
    "router": {
        "interfaces": {
            "Ethernet0/0": {"is_up": True, "ip": "10.0.0.99"},
            "Ethernet0/1": {"is_up": True, "ip": "20.0.0.99"}
        }
    },
    "pc1": {
        "interfaces": {
            "eth0": {"is_up": True, "ip": "10.0.0.1"}
        }
    },
    "pc2": {
        "interfaces": {
            "eth0": {"is_up": True, "ip": "10.0.0.2"}
        }
    },
    "pc3": {
        "interfaces": {
            "eth0": {"is_up": True, "ip": "20.0.0.1"}
        }
    }
}

@mcp.tool()
def check_reachability(source_device: str, target_ip: str) -> str:
    """Checks ping reachability from source to target."""
    try:
        inv = load_inventory()
        host_data = inv.get("hosts", {}).get(source_device)
        if not host_data:
            return f"Error: Device {source_device} not in inventory."
            
        port = host_data.get("port")
        groups = host_data.get("groups", [])
        platform = "linux" if "linux" in groups else "cisco_ios"
        
        console = GNS3Console("localhost", port, platform=platform)
        console.connect()
        output = console.ping(target_ip)
        console.close()
        
        # Analyze output
        success = False
        if "!!!!" in output or "bytes from" in output or "0% packet loss" in output:
             success = True
             
        if success:
            return f"SUCCESS: {output}"
        else:
            return f"FAILURE: {output}"

    except Exception as e:
        return f"Error running ping: {str(e)}"

@mcp.tool()
def get_interface_health(device: str, interface: str) -> str:
    """Returns interface status and errors. Connects to REAL device."""
    try:
        inv = load_inventory()
        host_data = inv.get("hosts", {}).get(device)
        if not host_data:
            return f"Error: Device {device} not found in inventory."
            
        port = host_data.get("port")
        groups = host_data.get("groups", [])
        platform = "linux" if "linux" in groups else "cisco_ios"
        
        console = GNS3Console("localhost", port, platform=platform)
        console.connect()
        
        # Get real interfaces
        real_interfaces = console.get_interfaces()
        console.close()
        
        if not real_interfaces:
            # Fallback for Linux or if parsing failed
            if platform == "linux":
                return "Linux interface health check not implemented yet (use ping)."
            return "Error: Could not retrieve interfaces from Router."

        # Find requested interface
        # Try exact match first
        target = next((i for i in real_interfaces if i["name"] == interface), None)
        
        # If not found, try case-insensitive or short name matching manually if needed.
        # But for now, returning available interfaces is helpful!
        if not target:
            available_names = [i["name"] for i in real_interfaces]
            return f"Error: Interface '{interface}' not found. Available interfaces: {', '.join(available_names)}"
            
        status = target["status"]
        protocol = target["protocol"]
        return f"Interface {interface}: Status={status}, Protocol={protocol}. IP={target['ip']}."

    except Exception as e:
        return f"Error connecting to device: {str(e)}"

@mcp.tool()
def simulate_link_failure(device: str, interface: str):
    """(Simulation Tool) Cuts a wire in GNS3 (mocks it)."""
    if device in LIVE_STATE and interface in LIVE_STATE[device]["interfaces"]:
        LIVE_STATE[device]["interfaces"][interface]["is_up"] = False
        return f"Simulated cut on {device} {interface}."
    return "Interface not found."

@mcp.tool()
def detect_link_failures(topology_definition: str) -> List[str]:
    """
    Compares live state against expected topology.
    """
    failures = []
    for dev_name, data in LIVE_STATE.items():
        for iface_name, iface_data in data["interfaces"].items():
            if not iface_data["is_up"]:
                failures.append(f"CRITICAL: {dev_name} {iface_name} is DOWN (Expected: UP)")
                
    if not failures:
        return ["All systems nominal."]
    return failures

@mcp.prompt()
def monitor_critical_links() -> str:
    """Workflow: Monitor network health."""
    return """
1. Call `librarian` to get `topology/definition`.
2. Call `detect_link_failures`.
3. If failures found (`router Ethernet0/0` etc), Plan fix.
    """

if __name__ == "__main__":
    mcp.run()
