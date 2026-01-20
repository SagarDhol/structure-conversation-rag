"""
LLM package initialization with unified factory.
Provides easy access to different LLM providers.
"""

from typing import Literal, Optional, Union

from app.config import get_settings
from app.llm.openai import OpenAIProvider
from app.llm.ollama import OllamaProvider
from app.utils import logger


LLMProvider = Union[OpenAIProvider, OllamaProvider]


def get_llm_provider(
    provider: Optional[Literal["openai", "ollama"]] = None,
    model: Optional[str] = None
) -> LLMProvider:
    """
    Factory function to get an LLM provider.
    
    Args:
        provider: Provider name (openai or ollama), defaults to config
        model: Model name, defaults to provider's default
        
    Returns:
        LLM provider instance
        
    Raises:
        ValueError: If provider is unknown
    """
    settings = get_settings()
    provider = provider or settings.default_llm_provider
    
    logger.info(f"Getting LLM provider: {provider}")
    
    if provider == "openai":
        return OpenAIProvider(model=model)
    elif provider == "ollama":
        return OllamaProvider(model=model)
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")


__all__ = [
    "OpenAIProvider",
    "OllamaProvider",
    "LLMProvider",
    "get_llm_provider",
]
