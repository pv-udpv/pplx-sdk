"""Configuration and settings for Perplexity AI SDK."""

from typing import Literal, Optional

from pydantic_settings import BaseSettings


class PplxSettings(BaseSettings):
    """Perplexity AI SDK settings."""

    # API Configuration
    api_key: Optional[str] = None
    api_base: str = "https://api.perplexity.ai"
    api_timeout: float = 60.0
    api_retries: int = 3

    # Client Configuration
    user_agent: str = "pplx-sdk/0.1.0"
    verify_ssl: bool = True

    # Models
    default_model: str = "llama-3.1-sonar-large-128k-online"
    default_chat_model: str = "llama-3.1-sonar-large-128k-online"

    # Behavior
    stream_mode: Literal["rest", "sse"] = "sse"
    max_tokens: Optional[int] = None
    temperature: float = 0.7

    class Config:
        """Pydantic config."""

        env_file = ".env"
        env_prefix = "PPLX_"
        case_sensitive = False
