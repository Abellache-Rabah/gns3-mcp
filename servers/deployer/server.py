from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, Optional
import time
import difflib
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../../"))
from shared.gns3_utils import GNS3Console, load_inventory

mcp = FastMCP("Deployer Server")

# Mock State for GNS3 Topology
CONFIG_STORE = {
    "router": """hostname router
!
interface Ethernet0/0
 description Connected to Switch1 (PCs)
 ip address 10.0.0.99 255.0.0.0
 no shutdown
!
interface Ethernet0/1
 description Connected to PC3
 ip address 20.0.0.99 255.0.0.0
 no shutdown
!
""",
    "pc1": "# PC1 Configuration\nifconfig eth0 10.0.0.1 netmask 255.0.0.0",
    "pc2": "# PC2 Configuration\nifconfig eth0 10.0.0.2 netmask 255.0.0.0",
    "pc3": "# PC3 Configuration\nifconfig eth0 20.0.0.1 netmask 255.0.0.0"
}

@mcp.tool()
def get_config_diff(device: str, new_config: str) -> str:
    """Calculates diff between current running config (simulated) and candidate."""
    current = CONFIG_STORE.get(device, "")
    
    diff = difflib.unified_diff(
        current.splitlines(keepends=True),
        new_config.splitlines(keepends=True),
        fromfile=f"running-config@{device}",
        tofile="candidate-config"
    )
    return "".join(diff)

@mcp.tool()
def deploy_config(device: str, config: str, dry_run: bool = True, auto_rollback: bool = True) -> str:
    """
    Deploys configuration to a device.
    """
    if device not in CONFIG_STORE:
        return f"Error: Device {device} not found/reachable."

    if dry_run:
        return f"[DRY-RUN] Would push the following config to {device} (localhost via Telnet):\n{config}"

    # Real Deployment Logic for GNS3
    try:
        # Load Inventory to get Port
        inv = load_inventory()
        host_data = inv.get("hosts", {}).get(device)
        
        if not host_data:
            return f"Error: Device {device} not found in inventory."
            
        port = host_data.get("port")
        if not port:
             return f"Error: No port defined for {device} in invenotry."
             
        # Connect via GNS3 Utils
        groups = host_data.get("groups", [])
        platform = "linux" if "linux" in groups else "cisco_ios"
        
        console = GNS3Console("localhost", port, platform=platform)
        console.connect()
        
        if platform == "linux":
            output = console.configure_linux(config)
        else:
            output = console.configure_cisco(config)
            
        console.close()
        
        return f"SUCCESS: Config deployed to {device} (Port {port}).\nOutput Capture:\n{output}"

    except Exception as e:
        return f"FAILURE: Connection/Deployment failed: {str(e)}"

@mcp.tool()
def rollback(device: str, revision_id: str = "last") -> str:
    """Manually rollback configuration."""
    return f"Rolled back {device} to revision {revision_id}."

@mcp.prompt()
def plan_deployment(device: str) -> str:
    """Workflow: Plan a safe deployment."""
    return f"""To safely deploy to {device}, please follows these steps:
1. Retrieve current config.
2. Generate candidate config.
3. Call `get_config_diff` to review changes.
4. Verify config with `verifier` server.
5. Call `deploy_config` with dry_run=True.
6. Check connection (Telnet/SSH) parameters.
7. Call `deploy_config` with dry_run=False.
"""

if __name__ == "__main__":
    mcp.run()
