"""
AEO Services - Unified API Gateway for AEO Analysis

All AEO-related services in one Modal app:
- /company/* - Company analysis (Gemini + GPT-4o-mini logo detection)
- /health/* - Website health check (30 checks across 4 categories)
- /mentions/* - AEO mentions check (5 AI platforms with search grounding)
- /analyze - Complete analysis: URL → all checks → HTML + PDF reports

Endpoint: https://clients--aeo-checks-fastapi-app.modal.run
"""

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

# Main app
app = FastAPI(
    title="AEO Services",
    description="Unified API gateway for AEO analysis services",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Service directory."""
    return {
        "service": "aeo-checks",
        "version": "1.0.0",
        "endpoints": {
            # Complete Analysis (NEW)
            "/analyze": "POST - Complete analysis: URL → company + health + mentions → HTML + PDF",
            # Company Analysis
            "/company/analyze": "POST - Full company analysis with logo detection",
            "/company/crawl-logo": "POST - Standalone logo detection",
            "/company/health": "GET - Company analysis service health",
            # Health Check
            "/health/check": "POST - Website AEO health check (30 checks)",
            "/health/health": "GET - Health check service status",
            # Mentions Check
            "/mentions/check": "POST - AEO mentions check across AI platforms",
            "/mentions/health": "GET - Mentions check service status",
            # Gateway
            "/status": "GET - Gateway status with all service health",
        }
    }


@app.get("/status")
async def gateway_status():
    """Gateway health check with service status."""
    return {
        "status": "healthy",
        "service": "aeo-checks",
        "version": "1.0.0",
        "services": {
            "company": "operational",
            "health": "operational",
            "mentions": "operational",
        }
    }


# Mount Company Analysis service under /company
from company_service import app as company_app
app.mount("/company", company_app)

# Mount Health Check service under /health
from health_service import app as health_app
app.mount("/health", health_app)

# Mount Mentions Check service under /mentions
from mentions_service import app as mentions_app
app.mount("/mentions", mentions_app)

# Import complete analysis endpoint
from complete_analysis import CompleteAnalysisRequest, CompleteAnalysisResponse, run_complete_analysis


@app.post("/analyze", response_model=CompleteAnalysisResponse)
async def analyze_complete(request: CompleteAnalysisRequest):
    """
    Complete AEO Analysis Pipeline
    
    Takes a URL and runs:
    1. Company Analysis (logo detection, tech stack, brand assets)
    2. Health Check (29 checks across 4 categories)
    3. Mentions Check (AI platform visibility)
    4. HTML Report Generation
    5. PDF Report Generation (if PDF service URL provided)
    
    Returns:
    - Full JSON data (company_analysis, health_check, mentions_check)
    - HTML report (html_report)
    - PDF report (pdf_base64, pdf_size_bytes)
    
    Example:
    ```json
    {
      "url": "https://example.com",
      "company_name": "Example Inc",
      "mentions_mode": "fast",
      "theme": "dark",
      "pdf_service_url": "https://your-workspace--pdf-service-fastapi-app.modal.run"
    }
    ```
    """
    import os
    
    # Get base URL (current service)
    # In Modal, construct from workspace name or use environment variable
    workspace = os.getenv("MODAL_WORKSPACE")
    if workspace:
        base_url = f"https://{workspace}--aeo-checks-fastapi-app.modal.run"
    else:
        # Fallback to localhost for local development
        base_url = os.getenv("MODAL_FUNCTION_URL", "http://localhost:8000")
    
    # Get PDF service URL from request or environment
    pdf_service_url = request.pdf_service_url or os.getenv("PDF_SERVICE_URL")
    
    try:
        result = await run_complete_analysis(request, base_url, pdf_service_url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

