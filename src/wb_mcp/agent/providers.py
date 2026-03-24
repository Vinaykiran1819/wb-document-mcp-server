# LLM adapters (Ollama, Groq)

"""
providers.py
Unified adapter for LLM/SLM providers: Ollama (Local) and Groq (Cloud).
Both providers support the OpenAI-compatible API standard, allowing us
to use a single AsyncOpenAI client for the entire agent logic.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class LLMProvider:
    """
    A unified, provider-agnostic LLM client.
    Because Groq and Ollama support the standard OpenAI API structure,
    we can use a single adapter for both by swapping the base_url and api_key.
    """
    
    def __init__(self, provider_name: str = "ollama"):
        """
        Initializes the asynchronous LLM client based on the chosen provider.
        
        Args:
            provider_name: The name of the LLM provider ('ollama' or 'groq').
        """
        self.provider_name = provider_name.lower()
        self.client = self._initialize_client()
        self.model = self._get_default_model()

    def _initialize_client(self) -> AsyncOpenAI:
        """Configures the AsyncOpenAI client with the correct endpoint and keys."""
        if self.provider_name == "ollama":
            # Ollama runs locally, so it needs no API key, just the local port.
            return AsyncOpenAI(
                base_url="http://localhost:11434/v1",
                api_key="ollama"
            )
            
        elif self.provider_name == "groq":
            # Groq is blindingly fast and requires a free API key from console.groq.com
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError("GROQ_API_KEY is missing from the .env file.")
            return AsyncOpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=api_key
            )
            
        else:
            raise ValueError(f"Unsupported provider: {self.provider_name}. Use 'ollama' or 'groq'.")

    def _get_default_model(self) -> str:
        """Returns the recommended model string for the chosen provider."""
        if self.provider_name == "ollama":
            # The model recommended by the task document for local execution
            return "qwen2.5:3b"
        elif self.provider_name == "groq":
            return "llama-3.1-8b-instant"
        return ""

    def set_model(self, model_name: str):
        """Allows overriding the default model at runtime."""
        self.model = model_name


    async def chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto"
    ) -> Any:
        """
        Sends a chat request to the LLM.
        
        Args:
            messages: The conversation history.
            tools: Optional list of MCP tool definitions.
            tool_choice: Control over tool usage ('auto', 'none', or specific tool).
            
        Returns:
            The message object from the LLM response.
        """
        try:
            # Prepare the API arguments
            params = {
                "model": self.model,
                "messages": messages,
            }
            
            # Only include tools if they are actually provided
            if tools:
                params["tools"] = tools
                params["tool_choice"] = tool_choice

            response = await self.client.chat.completions.create(**params)
            return response.choices[0].message
            
        except Exception as e:
            logger.error(f"LLM Error ({self.provider_name}): {str(e)}")
            raise