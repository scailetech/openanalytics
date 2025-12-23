"""
Unified AI Client for AEO Checks - Wrapper around OpenRouterClient.
"""
import logging
from typing import List, Dict, Any, Optional

from openrouter_client import OpenRouterClient, get_openrouter_client

logger = logging.getLogger(__name__)

class AIClient:
    """Wrapper around OpenRouterClient for compatibility."""
    
    def __init__(self):
        # Use the proven OpenRouterClient from scaile-services
        try:
            self.client = get_openrouter_client()
            logger.info(f"AIClient initialized successfully, client type: {type(self.client)}")
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouterClient: {type(e).__name__}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Any = "auto",
        **kwargs
    ) -> Any:
        """Simple completion - delegates to OpenRouterClient."""
        return await self.client.complete(messages, model, max_tokens=kwargs.pop("max_tokens", None), tools=tools, **kwargs)

    async def complete_with_tools(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        tools: Optional[List[str]] = None,
        max_iterations: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate completion with full tool execution loop - delegates to OpenRouterClient."""
        # Use complete_with_tools directly (not generate_with_tools) to match scaile-services behavior
        result = await self.client.complete_with_tools(
            messages=messages,
            model=model,
            tools=tools,
            max_iterations=max_iterations,
            **kwargs
        )
        # Result is already in the right format (dict with choices)
        return result
    
    async def query_with_structured_output(
        self,
        prompt: str,
        system_prompt: str = "",
        model: str = "gemini-2.5-flash",
        response_format: str = "json",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured output (JSON) from prompt."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Use the OpenRouter client for Gemini with JSON mode
            if "gemini" in model.lower():
                # Use OpenRouter for Gemini
                result = await self.client.complete(
                    messages=messages,
                    model="google/gemini-2.0-flash-exp",  # Use latest Gemini via OpenRouter
                    max_tokens=2000,
                    temperature=0.3,
                    **kwargs
                )
                
                # Extract response content
                if result and hasattr(result, 'choices') and result.choices:
                    response_text = result.choices[0].message.content
                    return {
                        "success": True,
                        "response": response_text,
                        "model": "google/gemini-2.0-flash-exp"
                    }
                else:
                    return {
                        "success": False,
                        "error": "No response from Gemini",
                        "response": ""
                    }
            else:
                # Fallback to other models
                result = await self.client.complete(
                    messages=messages,
                    model=model,
                    max_tokens=2000,
                    temperature=0.3,
                    **kwargs
                )
                
                if result and hasattr(result, 'choices') and result.choices:
                    response_text = result.choices[0].message.content
                    return {
                        "success": True,
                        "response": response_text,
                        "model": model
                    }
                else:
                    return {
                        "success": False,
                        "error": f"No response from {model}",
                        "response": ""
                    }
                    
        except Exception as e:
            logger.error(f"Error in structured output generation: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": ""
            }
