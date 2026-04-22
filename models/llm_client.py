"""
LLM Client - Unified interface for different LLM providers.
"""

from typing import Optional, Dict, Any, List
import os


class LLMClient:
    """
    Unified LLM client supporting multiple providers.

    Supports:
    - OpenAI (GPT-4, GPT-3.5)
    - Anthropic (Claude)
    - Local models (via Ollama, etc.)
    """

    def __init__(
        self,
        provider: str = "openai",
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize LLM client.

        Args:
            provider: LLM provider (openai, anthropic, local)
            model: Model name
            api_key: API key for the provider
            **kwargs: Additional provider-specific parameters
        """
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key
        self.kwargs = kwargs

        self._client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the provider-specific client."""
        if self.provider == "openai":
            self._initialize_openai()
        elif self.provider == "anthropic":
            self._initialize_anthropic()
        elif self.provider == "local":
            self._initialize_local()
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _initialize_openai(self):
        """Initialize OpenAI client."""
        try:
            import openai
            openai.api_key = self.api_key
            self._client = openai
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai")

    def _initialize_anthropic(self):
        """Initialize Anthropic client."""
        try:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("anthropic package not installed. Run: pip install anthropic")

    def _initialize_local(self):
        """Initialize local model client."""
        # Placeholder for local model support (Ollama, etc.)
        self._client = None

    def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        **kwargs
    ) -> str:
        """
        Generate completion from LLM.

        Args:
            prompt: Input prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional generation parameters

        Returns:
            Generated text
        """
        if self.provider == "openai":
            return self._generate_openai(prompt, temperature, max_tokens, **kwargs)
        elif self.provider == "anthropic":
            return self._generate_anthropic(prompt, temperature, max_tokens, **kwargs)
        elif self.provider == "local":
            return self._generate_local(prompt, temperature, max_tokens, **kwargs)

    def _generate_openai(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using OpenAI API."""
        try:
            # Use the new OpenAI client format (v1.0+)
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Linux performance testing and benchmarking assistant with deep knowledge of system performance analysis, real-time testing, and optimization strategies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Warning: OpenAI API call failed: {e}")
            return self._fallback_response()

    def _generate_anthropic(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using Anthropic API."""
        try:
            response = self._client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                **kwargs
            )
            return response.content[0].text
        except Exception as e:
            print(f"Warning: Anthropic API call failed: {e}")
            return self._fallback_response()

    def _generate_local(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
        **kwargs
    ) -> str:
        """Generate using local model."""
        # Placeholder - would integrate with Ollama or similar
        print("Warning: Local model generation not implemented")
        return self._fallback_response()

    def _fallback_response(self) -> str:
        """
        Fallback response when LLM is unavailable.

        Returns a basic JSON structure for test planning.
        """
        return """{
            "summary": "Automated test plan",
            "test_cases": [
                {
                    "name": "Basic performance test",
                    "suite": "unixbench",
                    "parameters": {}
                }
            ],
            "estimated_duration": "30 minutes"
        }"""

    def is_available(self) -> bool:
        """
        Check if LLM is available.

        Returns:
            True if LLM can be used
        """
        return self._client is not None and self.api_key is not None
