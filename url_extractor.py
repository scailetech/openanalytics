"""
URL Extractor - Wrapper around OpenPull for content extraction.
Using OpenRouter for AI extraction logic.
"""
import os
import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

logger = logging.getLogger(__name__)

class ExtractionResult(BaseModel):
    success: bool
    url: str
    extracted_data: Optional[Dict[str, Any]] = None
    raw_content: Optional[str] = None
    error: Optional[str] = None
    processing_time: Optional[float] = None

class UrlExtractor:
    """Wrapper for OpenPull scraping."""
    
    def __init__(self):
        self.client = None
        self.model = "google/gemini-2.0-flash-001"
        
        try:
            from openai import AsyncOpenAI
        except ImportError:
            logger.error("openai package not installed - URL extraction will fail")
            return

        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            logger.error("OPENROUTER_API_KEY not found in environment - URL extraction will fail")
            return
        
        # OpenRouter client for OpenPull
        try:
            self.client = AsyncOpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
                timeout=120.0,
            )
        except Exception as e:
            logger.error(f"Failed to initialize OpenRouter client: {e}")
            self.client = None

    async def extract(
        self, 
        url: str, 
        prompt: str = "Extract the main content.", 
        schema: Optional[Dict[str, Any]] = None
    ) -> ExtractionResult:
        start_time = datetime.now()
        
        if not self.client:
            return ExtractionResult(
                success=False, 
                url=url, 
                error="OpenRouter client not initialized (check OPENROUTER_API_KEY secret)"
            )
        
        try:
            from openpull import FlexibleScraper
        except ImportError:
            return ExtractionResult(
                success=False, url=url, error="OpenPull not installed"
            )

        try:
            logger.info(f"Initializing FlexibleScraper with model={self.model}")
            scraper = FlexibleScraper(
                openai_client=self.client,
                model=self.model
            )
            
            logger.info(f"Scraping {url} with OpenPull...")
            # Use OpenPull's scrape method
            result = await scraper.scrape(
                url=url,
                prompt=prompt,
                schema=schema
            )
            
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # OpenPull returns a dict-like object, check for error key
            if isinstance(result, dict):
                error = result.get("error")
                if error:
                    logger.error(f"OpenPull returned error: {error}")
                    return ExtractionResult(
                        success=False,
                        url=url,
                        error=str(error),
                        processing_time=elapsed
                    )
                # Extract data from dict result
                return ExtractionResult(
                    success=True,
                    url=url,
                    extracted_data=result.get("data"),
                    raw_content=result.get("markdown") or result.get("content", ""),
                    processing_time=elapsed
                )
            else:
                # Handle object result (backwards compatibility)
                error = getattr(result, "error", None)
                if error:
                    logger.error(f"OpenPull returned error: {error}")
                    return ExtractionResult(
                        success=False,
                        url=url,
                        error=str(error),
                        processing_time=elapsed
                    )
                
                return ExtractionResult(
                    success=True,
                    url=url,
                    extracted_data=getattr(result, "data", None),
                    raw_content=getattr(result, "markdown", None) or getattr(result, "content", ""),
                    processing_time=elapsed
                )
            
        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            return ExtractionResult(
                success=False,
                url=url,
                error=str(e),
                processing_time=elapsed
            )

