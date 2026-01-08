from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, Any, List
import yaml
import os

mcp = FastMCP("Librarian Server")

# Load Inventory (Mock Source of Truth)
INVENTORY_PATH = os.path.join(os.path.dirname(__file__), "../../shared/inventory.yaml")

def load_inventory() -> Dict:
    try:
        with open(INVENTORY_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {"error": "Inventory not found"}

# Mock Knowledge Base (RAG)
DOCS = {
    "ospf_config": "Standard OSPF Configuration: Process ID 1, Area 0. All interfaces should be P2P.",
    "link_failure_sop": "Link Failure SOP: 1. Verify specific link down. 2. Check physical layer. 3. If permanent, reroute via cost adjustment.",
    "security_policy": "Security Policy 101: specific ACLs must be applied to VTY lines. SSH only. No Telnet."
}

@mcp.tool()
def search_docs(query: str) -> List[str]:
    """Search the knowledge base for documentation."""
    # Simple keyword match for mock RAG
    results = []
    query = query.lower()
    for title, content in DOCS.items():
        if query in title.lower() or query in content.lower():
            results.append(f"[{title}]: {content}")
    
    if not results:
        return ["No documents found matching query."]
    return results

@mcp.tool()
def get_device_info(device_name: str) -> str:
    """Retrieve details for a specific device from Source of Truth."""
    inv = load_inventory()
    hosts = inv.get("hosts", {})
    if device_name in hosts:
        return str(hosts[device_name])
    return f"Device {device_name} not found in inventory."

@mcp.tool()
def list_devices() -> List[str]:
    """List all device names in the inventory."""
    inv = load_inventory()
    # Safely get keys from hosts
    return list(inv.get("hosts", {}).keys())

@mcp.resource("librarian://topology/definition")
def get_topology() -> str:
    """Returns the defining network topology (Source of Truth)."""
    inv = load_inventory()
    return yaml.dump(inv)

@mcp.resource("librarian://topology/physical")
def get_physical_topology() -> str:
    """Returns the PHYSICAL cabling and connection map (Ground Truth)."""
    topo_path = os.path.join(os.path.dirname(__file__), "../../shared/topology_physical.yaml")
    try:
        with open(topo_path, 'r') as f:
            return f.read()
    except Exception:
        return "Physical topology file not found."

if __name__ == "__main__":
    mcp.run()
