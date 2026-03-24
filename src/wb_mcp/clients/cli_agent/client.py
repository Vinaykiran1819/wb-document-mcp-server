# CLI entry point and user loop

"""
client.py
The primary CLI entry point for the World Bank Research Assistant.
Manages the MCP server subprocess, user interaction, and the agentic loop.
"""

import asyncio
import logging
import sys
import os
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# Absolute imports from our modular project structure
from wb_mcp.agent.providers import LLMProvider
from wb_mcp.agent.orchestrator import AgentOrchestrator

async def run_chat_loop():
    """
    Initializes the server connection, sets up the AI agent, 
    and runs the interactive command-line chat loop.
    """
    print("\n[System] 🚀 Starting World Bank MCP Server...")
    

    server_env = os.environ.copy()
    server_env["PYTHONPATH"] = "src"
    # Define how to start the server subprocess.
    # We use sys.executable to ensure it uses the Python from your active virtual environment.
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "wb_mcp.servers.docs_server.server"],
        env=server_env
    )

    # Connect to the server using standard input/output
    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the session
            await session.initialize()
            print("[System] ✅ MCP Server connected successfully.")
            
            # Initialize our AI Brain
            # You can change "ollama" to "groq" depending on your setup
            provider = LLMProvider(provider_name="ollama")
            orchestrator = AgentOrchestrator(provider=provider, mcp_session=session)
            
            print(f"[System] 🧠 AI Agent initialized with model: {provider.model}")
            print("\n" + "="*50)
            print("🌍 Welcome to the World Bank Research Assistant!")
            print("Type your question below, or type 'quit' or 'exit' to close.")
            print("="*50 + "\n")

            # The interactive chat loop
            while True:
                try:
                    user_input = input("\n🧑 You: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'q']:
                        print("\n[System] Shutting down successfully. Goodbye! 👋")
                        break
                        
                    if not user_input:
                        continue
                        
                    # Send the query to the Orchestrator
                    response = await orchestrator.process_query(user_input)
                    
                    # Print the final synthesized answer
                    print(f"\n🤖 Agent:\n{response}")
                    
                except KeyboardInterrupt:
                    # Graceful shutdown if you press Ctrl+C
                    print("\n\n[System] Connection interrupted. Shutting down... 👋")
                    break
                except Exception as e:
                    print(f"\n[Error] An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    # Ensure graceful exit on Windows without throwing event loop closed errors
    try:
        asyncio.run(run_chat_loop())
    except KeyboardInterrupt:
        pass