"""
Complete AEO Analysis - Unified Endpoint

Takes a URL, runs all checks (company analysis, health check, mentions check),
generates HTML and PDF reports, and returns everything.
"""

import httpx
import base64
import os
from typing import Optional, Dict, Any
from fastapi import HTTPException
from pydantic import BaseModel, Field
import logging
import asyncio

logger = logging.getLogger(__name__)

# Import report generator
# Try to import from parent directory (reports/)
try:
    import sys
    from pathlib import Path
    parent_dir = Path(__file__).parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))
    from reports.html_generator import generate_report_html
except ImportError:
    # Fallback: if reports module not available, create a simple HTML generator
    def generate_report_html(**kwargs):
        return "<html><body><h1>AEO Analysis Report</h1><p>Report generation requires reports module.</p></body></html>"


class CompleteAnalysisRequest(BaseModel):
    """Request for complete AEO analysis."""
    url: str = Field(..., description="Website URL to analyze")
    company_name: Optional[str] = Field(None, description="Company name (optional, will be extracted from URL)")
    mentions_mode: str = Field("fast", description="Mentions check mode: 'fast' (10 queries) or 'full' (50 queries)")
    theme: str = Field("dark", description="Report theme: 'dark' or 'light'")
    pdf_service_url: Optional[str] = Field(None, description="PDF service URL (optional, will use env var if not provided)")


class CompleteAnalysisResponse(BaseModel):
    """Complete analysis response with all data and reports."""
    url: str
    company_name: str
    
    # Analysis results
    company_analysis: Dict[str, Any]
    health_check: Dict[str, Any]
    mentions_check: Dict[str, Any]
    
    # Reports
    html_report: str
    pdf_base64: Optional[str] = None
    pdf_size_bytes: Optional[int] = None
    
    # Metadata
    analysis_time_seconds: float
    success: bool
    errors: list[str] = []


async def run_complete_analysis(
    request: CompleteAnalysisRequest,
    base_url: str,
    pdf_service_url: Optional[str] = None
) -> CompleteAnalysisResponse:
    """
    Run complete AEO analysis pipeline.
    
    Args:
        request: Analysis request
        base_url: Base URL of the aeo-checks service
        pdf_service_url: URL of PDF service (optional)
    
    Returns:
        Complete analysis response with all data and reports
    """
    import time
    start_time = time.time()
    errors = []
    
    # Extract company name from URL if not provided
    company_name = request.company_name
    if not company_name:
        try:
            from urllib.parse import urlparse
            domain = urlparse(request.url).netloc.replace('www.', '')
            company_name = domain.split('.')[0].title()
        except:
            company_name = "Company"
    
    # Step 1: Company Analysis
    logger.info(f"Starting company analysis for {request.url}")
    company_analysis = None
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            company_response = await client.post(
                f"{base_url}/company/analyze",
                json={
                    "website_url": request.url,
                    "company_name": company_name,
                    "extract_logo": True,
                }
            )
            if company_response.status_code == 200:
                company_analysis = company_response.json()
                logger.info("Company analysis complete")
            else:
                error_msg = f"Company analysis failed: {company_response.status_code}"
                logger.error(error_msg)
                errors.append(error_msg)
                company_analysis = {"error": error_msg, "status_code": company_response.status_code}
    except Exception as e:
        error_msg = f"Company analysis error: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
        company_analysis = {"error": error_msg}
    
    # Step 2: Health Check (can run in parallel, but we'll do it sequentially for simplicity)
    logger.info(f"Starting health check for {request.url}")
    health_check = None
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            health_response = await client.post(
                f"{base_url}/health/check",
                json={"url": request.url}
            )
            if health_response.status_code == 200:
                health_check = health_response.json()
                logger.info("Health check complete")
            else:
                error_msg = f"Health check failed: {health_response.status_code}"
                logger.error(error_msg)
                errors.append(error_msg)
                health_check = {"error": error_msg, "status_code": health_response.status_code}
    except Exception as e:
        error_msg = f"Health check error: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
        health_check = {"error": error_msg}
    
    # Step 3: Mentions Check (requires company analysis)
    logger.info(f"Starting mentions check for {company_name}")
    mentions_check = None
    if company_analysis and not company_analysis.get("error"):
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                mentions_response = await client.post(
                    f"{base_url}/mentions/check",
                    json={
                        "companyName": company_name,
                        "companyAnalysis": company_analysis,
                        "mode": request.mentions_mode,
                    }
                )
                if mentions_response.status_code == 200:
                    mentions_check = mentions_response.json()
                    logger.info("Mentions check complete")
                else:
                    error_msg = f"Mentions check failed: {mentions_response.status_code}"
                    logger.error(error_msg)
                    errors.append(error_msg)
                    mentions_check = {"error": error_msg, "status_code": mentions_response.status_code}
        except Exception as e:
            error_msg = f"Mentions check error: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            mentions_check = {"error": error_msg}
    else:
        error_msg = "Skipping mentions check - company analysis failed or incomplete"
        logger.warning(error_msg)
        errors.append(error_msg)
        mentions_check = {"error": "Company analysis required for mentions check"}
    
    # Step 4: Generate HTML Report
    logger.info("Generating HTML report")
    html_report = None
    try:
        # Extract logo URL from company analysis
        logo_url = None
        if company_analysis and not company_analysis.get("error"):
            brand_assets = company_analysis.get("brandAssets", {})
            logo_url = brand_assets.get("logo", {}).get("url") if brand_assets else None
        
        html_report = generate_report_html(
            company_data=company_analysis if company_analysis and not company_analysis.get("error") else None,
            health_data=health_check if health_check and not health_check.get("error") else None,
            mentions_data=mentions_check if mentions_check and not mentions_check.get("error") else None,
            client_name=company_name,
            website_url=request.url,
            logo_url=logo_url,
            theme=request.theme,
        )
        logger.info("HTML report generated")
    except Exception as e:
        error_msg = f"HTML report generation error: {str(e)}"
        logger.error(error_msg)
        errors.append(error_msg)
        html_report = f"<html><body><h1>Error generating report</h1><p>{error_msg}</p></body></html>"
    
    # Step 5: Generate PDF Report
    pdf_base64 = None
    pdf_size_bytes = None
    if html_report and pdf_service_url:
        logger.info("Generating PDF report")
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                pdf_response = await client.post(
                    f"{pdf_service_url}/convert",
                    json={
                        "html": html_report,
                        "format": "A4",
                        "print_background": True,
                        "color_scheme": request.theme,
                        "viewport_width": 900,
                        "device_scale_factor": 2,
                    }
                )
                if pdf_response.status_code == 200:
                    pdf_data = pdf_response.json()
                    pdf_base64 = pdf_data.get("pdf_base64")
                    pdf_size_bytes = pdf_data.get("size_bytes")
                    logger.info(f"PDF report generated ({pdf_size_bytes} bytes)")
                else:
                    error_msg = f"PDF generation failed: {pdf_response.status_code}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        except Exception as e:
            error_msg = f"PDF generation error: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
    
    analysis_time = time.time() - start_time
    
    return CompleteAnalysisResponse(
        url=request.url,
        company_name=company_name,
        company_analysis=company_analysis or {},
        health_check=health_check or {},
        mentions_check=mentions_check or {},
        html_report=html_report or "",
        pdf_base64=pdf_base64,
        pdf_size_bytes=pdf_size_bytes,
        analysis_time_seconds=analysis_time,
        success=len(errors) == 0 or (company_analysis and not company_analysis.get("error")),
        errors=errors,
    )

