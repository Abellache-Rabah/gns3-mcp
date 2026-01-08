# Network AI Agent MCP Stack

A comprehensive suite of **7 Model Context Protocol (MCP)** servers designed to empower an AI Agent to act as a **Network Engineer**.

## Servers

| Server | Role | Tools Example |
| :--- | :--- | :--- |
| **Verifier** | Design & Analysis | `verify_device_config` (Batfish) |
| **Deployer** | Execution | `deploy_config` (Nornir), `rollback` |
| **Observer** | Monitoring | `check_reachability`, `detect_link_failures` |
| **Librarian** | Knowledge Base | `search_docs` (RAG), `get_topology` |
| **IPAM** | Resource Mgmt | `allocate_ip`, `get_subnet_usage` |
| **Auditor** | Security | `check_compliance`, `scan_vulnerabilities` |
| **TrafficGen** | Validation | `run_traffic_test` (iperf3) |

## Quick Start

### 1. Environment and Dependencies
This project uses a unified virtual environment (originally created in `servers/verifier`).

```bash
# Verify Batfish is running
docker ps | grep batfish
```

### 2. Running the Integration Test
We have a "Zero Error Loop" test that simulates a link failure and autonomous repair.

```bash
export PYTHONPATH=$PYTHONPATH:.
./servers/verifier/.venv/bin/python integration_tests/verify_stack.py
```

### 3. Connect your AI
Configure your AI client (`claude_desktop_config.json` or similar) to point to these servers. Each server can be run via:
`python servers/{server_name}/server.py`

## Connectivity & Authentication

1.  **Credentials**: You define users/passwords in `shared/inventory.yaml`.
2.  **Deployer**: Uses [Nornir](https://nornir.readthedocs.io/) + [Scrapli](https://github.com/carlmontanari/scrapli) to open an **SSH** connection to the device using those credentials. It pushes commands just like a human would.
3.  **Observer**: Uses [NAPALM](https://napalm.readthedocs.io/) (via SSH or API) to retrieve live state (interfaces, existing config).

**Note**: The current code logic in `deployer` and `observer` is using **simulated/mock** logic for demonstration. In a real production or GNS3 environment, you would uncomment the `nornir` imports and use the real drivers provided in the code comments.

## Integration: How to use with an AI

### Option 1: Claude Desktop (Simplest)
1.  Download **Claude Desktop**.
2.  Open your config file:
    -   Mac: `~/Library/Application Support/Claude/claude_desktop_config.json`
    -   Windows: `%APPDATA%\Claude\claude_desktop_config.json`
3.  Copy the contents of `claude_desktop_config.json` (found in this repo) into that file.
4.  Restart Claude. You will see a 🔌 icon indicating the servers are connected.

### Option 2: Gemini / Custom Python Client
To integrate with Gemini API or build a custom CLI:

1.  Use the `mcp` Python SDK to connect to these servers via stdio.
2.  See `client_demo.py` for a basic example of connecting programmatically.
3.  **LangChain / LangGraph**: You can use `langchain-mcp-adapters` to load these tools and pass them to a Gemini model.

### Option 3: "You" (This Agent)
As an AI agent in your terminal, I can run these files directly (like I did in `integration_tests/verify_stack.py`). I act as the "Client" that calls `deployer`, `observer`, etc.

