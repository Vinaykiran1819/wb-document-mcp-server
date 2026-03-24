# Server entry point (stdio transport)
"""
server.py
The main entry point for the World Bank Documents MCP Server.
Configures the FastMCP instance, initializes the API client, and starts the stdio transport.
"""

import sys
import logging
import asyncio
from mcp.server.fastmcp import FastMCP
from wb_mcp.api.client import WorldBankClient
from wb_mcp.servers.docs_server.tools import register_tools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("wb_docs_mcp")

def create_server() -> FastMCP:
    """
    Factory function to initialize and configure the FastMCP server.
    Using a factory function makes the server easier to test later.
    """
    # Initialize the server with a clear, professional name
    mcp = FastMCP("WorldBankDocsServer")
    
    # Initialize our highly-modular World Bank API client
    api_client = WorldBankClient(timeout=30.0)
    
    # Register the 4 required tools to this server instance
    register_tools(mcp, api_client)
    
    return mcp

def run():
    """
    The main execution entry point for the server.
    This is called by the client/agent as a subprocess.
    """
    server = create_server()
    
    # The assessment explicitly requires using the stdio transport layer.
    # FastMCP defaults to stdio when running directly.
    server.run(transport="stdio")

if __name__ == "__main__":
    # Standard Python idiom to ensure the script only runs when executed directly
    run()