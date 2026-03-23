# LLM adapters (Ollama, Groq)
import os
from typing import Optional
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
            # The recommended fast SLM for Groq
            return "llama-3.1-8b-instant"
        return ""

    def set_model(self, model_name: str):
        """Allows overriding the default model at runtime."""
        self.model = model_name