from mcp.server.fastmcp import FastMCP
from typing import Dict, Any
import time

mcp = FastMCP("TrafficGen Server")

@mcp.tool()
def start_traffic_server(host: str, port: int = 5201) -> str:
    """Starts iperf3 server on a host (simulated)."""
    # Real: SSH to Linux host -> `iperf3 -s -p {port} -D`
    return f"Started iperf3 server on {host}:{port} (PID: 1234)"

@mcp.tool()
def run_traffic_test(client: str, server_ip: str, duration: int = 10, bandwidth: str = "1G") -> str:
    """Runs iperf3 client traffic test."""
    # Real: SSH to client -> `iperf3 -c {server_ip} -t {duration} -b {bandwidth}`
    
    # Simulation Logic
    # We could query Observer to see if link is up. For now, assume success if not specifically broken.
    
    time.sleep(1) # Fake test duration
    
    return f"""
-----------------------------------------------------------
Client connecting to {server_ip}, TCP port 5201
TCP window size: 85.3 KByte (default)
-----------------------------------------------------------
[  3] local {client} port 54321 connected with {server_ip} port 5201
[ ID] Interval       Transfer     Bandwidth
[  3]  0.0-10.0 sec  1.10 GBytes   {bandwidth}bits/sec
Test Complete. Result: SUCCESS.
"""

@mcp.resource("traffic://last_test_result")
def get_last_result() -> str:
    """Returns the result of the last run test."""
    return "Last test: 1.10 GBytes transferred at 1Gbits/sec (PASS)"

@mcp.prompt()
def stress_test_link() -> str:
    """Workflow: Verify link capacity."""
    return """
1. Identify server and client hosts on ends of the link.
2. `start_traffic_server(server)`.
3. `run_traffic_test(client, server_ip)`.
4. Validate bandwidth matches expectation.
"""

if __name__ == "__main__":
    mcp.run()
