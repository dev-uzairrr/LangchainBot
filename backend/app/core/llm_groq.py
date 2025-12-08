"""
Groq LLM integration for chat completions.
"""
import logging
from typing import AsyncGenerator, Optional

import httpx
from groq import Groq, AsyncGroq
from groq import PermissionDeniedError, AuthenticationError, APIError
from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqLLM:
    """Wrapper for Groq LLM API."""
    
    def __init__(self):
        """Initialize Groq client (lazy initialization)."""
        self._client = None
        self._async_client = None
        self.model = settings.GROQ_MODEL
        self.temperature = settings.GROQ_TEMPERATURE
        self.max_tokens = settings.GROQ_MAX_TOKENS
    
    def _ensure_client_initialized(self):
        """Ensure Groq client is initialized (lazy loading)."""
        if self._client is not None:
            return
        
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is required")
        
        try:
            # Create custom httpx clients to avoid proxies parameter issue
            # Workaround for groq library bug with httpx proxies parameter
            sync_http_client = httpx.Client(trust_env=False)
            async_http_client = httpx.AsyncClient(trust_env=False)
            
            self._client = Groq(
                api_key=settings.GROQ_API_KEY,
                http_client=sync_http_client
            )
            self._async_client = AsyncGroq(
                api_key=settings.GROQ_API_KEY,
                http_client=async_http_client
            )
            logger.info("Groq client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {str(e)}", exc_info=True)
            raise
    
    @property
    def client(self):
        """Get synchronous Groq client (lazy loaded)."""
        self._ensure_client_initialized()
        return self._client
    
    @property
    def async_client(self):
        """Get asynchronous Groq client (lazy loaded)."""
        self._ensure_client_initialized()
        return self._async_client
    
    def chat_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate chat completion synchronously.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated text response
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
            
            return response.choices[0].message.content
            
        except PermissionDeniedError as e:
            error_msg = "Access denied to Groq API. Please check your API key and network settings."
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise ValueError(error_msg) from e
        except AuthenticationError as e:
            error_msg = "Authentication failed. Please check your GROQ_API_KEY."
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise ValueError(error_msg) from e
        except APIError as e:
            error_msg = f"Groq API error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            logger.error(f"Error in Groq chat completion: {str(e)}", exc_info=True)
            raise
    
    async def chat_completion_async(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate chat completion asynchronously.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Generated text response
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )
            
            return response.choices[0].message.content
            
        except PermissionDeniedError as e:
            error_msg = "Access denied to Groq API. Please check your API key and network settings."
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise ValueError(error_msg) from e
        except AuthenticationError as e:
            error_msg = "Authentication failed. Please check your GROQ_API_KEY."
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise ValueError(error_msg) from e
        except APIError as e:
            error_msg = f"Groq API error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            logger.error(f"Error in Groq async chat completion: {str(e)}", exc_info=True)
            raise
    
    async def stream_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """
        Stream chat completion asynchronously.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            
        Yields:
            Chunks of generated text
        """
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            stream = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except PermissionDeniedError as e:
            error_msg = "Access denied to Groq API. Please check your API key and network settings."
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise ValueError(error_msg) from e
        except AuthenticationError as e:
            error_msg = "Authentication failed. Please check your GROQ_API_KEY."
            logger.error(f"{error_msg}: {str(e)}", exc_info=True)
            raise ValueError(error_msg) from e
        except APIError as e:
            error_msg = f"Groq API error: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise RuntimeError(error_msg) from e
        except Exception as e:
            logger.error(f"Error in Groq stream completion: {str(e)}", exc_info=True)
            raise


# Global instance - will be initialized lazily on first use
groq_llm = GroqLLM()

