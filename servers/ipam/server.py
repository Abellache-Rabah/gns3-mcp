from mcp.server.fastmcp import FastMCP
from typing import Dict, Any, List
import ipaddress

mcp = FastMCP("IPAM Server")

# Mock IPAM Database
SUBNETS = {
    "management": "192.168.1.0/24",
    "users": "10.0.10.0/24",
    "servers": "10.0.20.0/24",
    "transit": "10.100.0.0/24"
}

ALLOCATIONS = {
    "192.168.1.1": "core-router",
    "192.168.1.2": "dist-switch-01",
    "192.168.1.10": "access-switch-01",
    "192.168.1.100": "srv-web-01"
}

@mcp.tool()
def list_subnets() -> Dict[str, str]:
    """List all managed subnets."""
    return SUBNETS

@mcp.tool()
def get_subnet_usage(subnet_name: str) -> str:
    """Calculate usage for a specific subnet."""
    if subnet_name not in SUBNETS:
        return f"Error: Subnet '{subnet_name}' not found."
    
    cidr = SUBNETS[subnet_name]
    net = ipaddress.ip_network(cidr)
    total_hosts = net.num_addresses - 2 # exclude net/broadcast
    
    used_count = 0
    for ip in ALLOCATIONS:
        if ipaddress.ip_address(ip) in net:
            used_count += 1
            
    usage_percent = (used_count / total_hosts) * 100
    return f"Subnet {subnet_name} ({cidr}): {used_count}/{total_hosts} used ({usage_percent:.1f}%)"

@mcp.tool()
def allocate_ip(subnet_name: str, description: str) -> str:
    """Allocates the next available IP in a subnet."""
    if subnet_name not in SUBNETS:
        return f"Error: Subnet '{subnet_name}' not found."

    cidr = SUBNETS[subnet_name]
    net = ipaddress.ip_network(cidr)
    
    # Simple sequential scan
    for ip in net.hosts():
        ip_str = str(ip)
        if ip_str not in ALLOCATIONS:
            ALLOCATIONS[ip_str] = description
            return f"Allocated {ip_str} for '{description}' in {subnet_name}"
            
    return f"Error: No IPs available in {subnet_name}"

@mcp.resource("ipam://subnets/list")
def resource_subnets() -> str:
    """Returns a textual list of subnets and their CIDRs."""
    output = ["IPAM Managed Subnets:"]
    for name, cidr in SUBNETS.items():
        output.append(f"- {name}: {cidr}")
    return "\n".join(output)

if __name__ == "__main__":
    mcp.run()
