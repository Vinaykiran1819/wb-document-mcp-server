# Manages the agentic loop and history
import json
from typing import List, Dict, Any
from mcp import ClientSession
from .providers import LLMProvider
from .prompts import SYSTEM_PROMPT

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
        into the JSON Schema format that OpenAI/Groq/Ollama expects.
        """
        tools_response = await self.mcp_session.list_tools()
        formatted_tools = []
        
        for tool in tools_response.tools:
            formatted_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        return formatted_tools

    async def process_query(self, user_query: str) -> str:
        """
        The main Agentic Loop.
        Takes a user question, consults the LLM, runs tools if requested, 
        and repeats until a final answer is generated.
        """
        # 1. Add the new user question to the history
        self.history.append({"role": "user", "content": user_query})
        
        # 2. Fetch the tools dynamically from our MCP server
        available_tools = await self._get_mcp_tools_for_llm()
        
        # 3. Start the reasoning loop (Limit to 10 iterations to prevent infinite loops)
        for iteration in range(10):
            # Send the entire history and tools to the LLM
            response = await self.provider.client.chat.completions.create(
                model=self.provider.model,
                messages=self.history,
                tools=available_tools if available_tools else None,
                tool_choice="auto"
            )
            
            message = response.choices[0].message
            
            # If the LLM didn't call a tool, it has formulated our final answer!
            if not message.tool_calls:
                # Add the LLM's final answer to history so it remembers it for the next question
                self.history.append({"role": "assistant", "content": message.content})
                return message.content
            
            # If the LLM DID call a tool, we need to execute it.
            # First, append the tool call itself to the history (API requirement)
            self.history.append(message.model_dump(exclude_none=True))
            
            # Execute each requested tool in sequence
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                # Provide a visual cue to the user that the AI is thinking/working
                print(f"\n   [Agent] ⚙️ Calling tool: {tool_name}")
                
                try:
                    # Call the actual MCP server over stdio
                    tool_result = await self.mcp_session.call_tool(tool_name, tool_args)
                    
                    # Extract the text from the MCP result
                    # FastMCP returns results as a list of TextContent objects
                    result_text = "\n".join([content.text for content in tool_result.content if content.type == "text"])
                    
                except Exception as e:
                    # Catch MCP execution errors gracefully
                    result_text = f"Error executing tool: {str(e)}"
                
                # Append the raw data result back to the history so the LLM can read it
                self.history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_text
                })
                
            # The loop will now restart automatically. 
            # It sends the newly updated history (with the tool results) back to the LLM.

        return "I'm sorry, I reached the maximum number of reasoning steps and couldn't find an answer."