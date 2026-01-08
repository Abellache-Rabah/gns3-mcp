import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Example: Connecting to just the 'Librarian' server programmatically
# To connect to all, you would manage multiple sessions.

async def main():
    # 1. Define how to start the server
    server_params = StdioServerParameters(
        command="./servers/verifier/.venv/bin/python",
        args=["servers/librarian/server.py"],
        env=None
    )

    print("Connecting to Librarian MCP Server...")
    
    # 2. Connect
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 3. List available tools
            tools = await session.list_tools()
            print(f"\nConnected! Available Tools: {[t.name for t in tools.tools]}")
            
            # 4. Simulate LLM interaction
            user_query = "Link Failure"
            print(f"\n[User]: Search for docs about '{user_query}'")
            
            # The "LLM" decides to call a tool
            result = await session.call_tool("search_docs", arguments={"query": user_query})
            
            print(f"[AI Agent]: Tool Output -> {result.content[0].text}")

if __name__ == "__main__":
    # Ensure we are in the project root
    import os
    if not os.path.exists("servers"):
        print("Please run this from the project root.")
        sys.exit(1)
        
    asyncio.run(main())
