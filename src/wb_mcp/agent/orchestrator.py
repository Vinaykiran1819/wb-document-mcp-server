# Manages the agentic loop and history

"""
orchestrator.py
The central agentic engine for the World Bank MCP system.
Manages multi-turn conversation history, tool discovery, and execution 
loops for OpenAI-compatible providers (Ollama and Groq).
"""

import json
import logging
from typing import List, Dict, Any
from mcp import ClientSession
from .providers import LLMProvider
from .prompts import SYSTEM_PROMPT

logger = logging.getLogger("orchestrator")

class AgentOrchestrator:
    """
    The central 'Brain' of the application.
    Manages conversation history, communicates with the LLM, and executes 
    MCP tools based on the LLM's decisions.
    """
    
    def __init__(self, provider: LLMProvider, mcp_session: ClientSession):
        """
        Initializes the orchestrator with an LLM provider and an active MCP session.
        """
        self.provider = provider
        self.mcp_session = mcp_session
        
        # Initialize conversation history with the imported system prompt
        self.history: List[Dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    async def _get_mcp_tools_for_llm(self) -> List[Dict[str, Any]]:
        """
        Fetches the available tools from the MCP server and translates them 
        into the JSON Schema format that Groq/Ollama expects.
        """
        tools_response = await self.mcp_session.list_tools()
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            } for tool in tools_response.tools
        ]

    async def process_query(self, user_query: str) -> str:
        """
        The main Agentic Loop.
        Takes a user question, consults the LLM, runs tools if requested, 
        and repeats until a final answer is generated.
        """
        self.history.append({"role": "user", "content": user_query})
        
        # Fetch the tools once per query cycle
        available_tools = await self._get_mcp_tools_for_llm()
        
        # Limit reasoning steps to avoid infinite loops or high API costs
        for _ in range(10):
            # Use our unified provider wrapper
            message = await self.provider.chat_completion(
                messages=self.history,
                tools=available_tools if available_tools else None
            )
            
            # Case 1: The LLM gives a final text answer
            if not message.tool_calls:
                self.history.append({"role": "assistant", "content": message.content})
                return message.content
            
            # Case 2: The LLM wants to use a tool
            # First, append the tool-call request to history (required by API)
            self.history.append(message.model_dump(exclude_none=True))
            
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                print(f"   [Agent] ⚙️ Executing: {tool_name}({tool_args})")
                
                try:
                    # Execute the tool via the MCP Session
                    result = await self.mcp_session.call_tool(tool_name, tool_args)
                    
                    # Merge all text content returned by the tool
                    result_text = "\n".join(
                        [c.text for c in result.content if c.type == "text"]
                    )
                except Exception as e:
                    logger.error(f"Tool Execution Error: {str(e)}")
                    result_text = f"Error: {str(e)}"
                
                # Feed the tool's output back into the conversation history
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_text
                })
            
            # The loop continues; the LLM will now see the tool results in history.

        return "Error: Maximum reasoning steps reached without a final answer."