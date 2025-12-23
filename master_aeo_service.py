"""
Master AEO Service - Advanced Analysis Platform
Combines the best features from aeo-health-check and aeo-leaderboard implementations.

Features:
- Health Check: v4.0 tiered scoring (29 checks across 4 categories)
- Mentions Check: Advanced hyperniche targeting with Gemini 2.5 Flash
- Quality Scoring: Sophisticated mention quality detection and brand confusion analysis
- Multi-platform Support: 5 AI platforms with native/search integration
- Unified API: Single service for all AEO analytics needs

Architecture:
- aeo-health-check: Health scoring system, crawler access detection
- aeo-leaderboard: Advanced query generation, quality scoring, business intelligence
- Master: Unified service with best-of-both implementations
"""

import os
import re
import json
import asyncio
import logging
import time
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from bs4 import BeautifulSoup

# Import health check components (from aeo-health-check)
from fetcher import fetch_website, FetchResult
from checks.technical import run_technical_checks, extract_technical_summary
from checks.structured_data import (
    run_structured_data_checks, 
    extract_structured_data_summary,
    extract_schema_data
)
from checks.aeo_crawler import run_aeo_crawler_checks, extract_crawler_summary
from checks.authority import run_authority_checks, extract_authority_summary
from scoring import (
    calculate_overall_score,
    calculate_tiered_score,
    calculate_grade,
    calculate_visibility_band,
    calculate_category_clarity_score,
    calculate_entity_strength_score,
    calculate_authority_signal_score,
    count_issues_by_severity,
)

# Import AI clients for mentions check
from gemini_client import get_gemini_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Master AEO Service",
    description="Advanced AEO Analysis Platform combining health checks and mentions analytics with sophisticated business intelligence",
    version="5.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Data Models ====================

class CompanyInfo(BaseModel):
    """Company information for targeted analysis."""
    name: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    productCategory: Optional[str] = None
    products: Optional[List[str]] = None
    services: Optional[List[str]] = None
    pain_points: Optional[List[str]] = None
    target_audience: Optional[str] = None
    icp: Optional[str] = None
    country: Optional[str] = None

class Competitor(BaseModel):
    """Competitor information."""
    name: str
    website: Optional[str] = None
    description: Optional[str] = None

class CompanyAnalysis(BaseModel):
    """Complete company analysis data."""
    companyInfo: CompanyInfo
    competitors: List[Competitor] = Field(default_factory=list)

# Health Check Models
class HealthCheckRequest(BaseModel):
    """Health check request."""
    url: str
    include_performance: bool = True
    include_accessibility: bool = True

class CheckResult(BaseModel):
    """Individual check result."""
    name: str
    status: str  # 'pass', 'warning', 'fail'
    message: str
    impact: str  # 'critical', 'high', 'medium', 'low'
    recommendation: Optional[str] = None
    score: float
    max_score: float

class CategoryResult(BaseModel):
    """Category check results."""
    name: str
    score: float
    max_score: float
    grade: str
    checks: List[CheckResult]
    summary: str

class HealthCheckResponse(BaseModel):
    """Complete health check response."""
    url: str
    overall_score: float
    max_score: float
    grade: str
    visibility_band: str
    categories: List[CategoryResult]
    issues_summary: Dict[str, int]
    recommendations: List[str]
    execution_time_seconds: float

# Mentions Check Models (Enhanced from aeo-leaderboard)
class MentionsCheckRequest(BaseModel):
    """Advanced mentions check request."""
    companyName: str
    companyAnalysis: Optional[CompanyAnalysis] = None
    language: str = "english"
    country: str = "US"
    numQueries: int = 50
    mode: str = Field(default="full", description="'full' (50 queries, all platforms) or 'fast' (10 queries, Gemini + ChatGPT only)")
    generateInsights: bool = True
    platforms: Optional[List[str]] = None

class QueryResult(BaseModel):
    """Individual query result with advanced metrics."""
    query: str
    dimension: str
    platform: str
    raw_mentions: int
    capped_mentions: int
    quality_score: float
    mention_type: str
    position: Optional[int] = None
    source_urls: List[str] = Field(default_factory=list)
    competitor_mentions: List[Dict[str, Any]] = Field(default_factory=list)
    response_text: str = ""

class PlatformStats(BaseModel):
    """Platform-specific statistics."""
    mentions: int
    quality_score: float
    responses: int
    errors: int
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    cost: float = 0.0

class DimensionStats(BaseModel):
    """Dimension-specific statistics."""
    mentions: int
    quality_score: float
    queries: int

class TLDRSummary(BaseModel):
    """Advanced business intelligence summary."""
    visibility_assessment: str
    key_insights: List[str]
    brand_confusion_risk: str
    competitive_positioning: str
    actionable_recommendations: List[str]
    health_integration: Optional[str] = None  # Integration with health scores

class MentionsCheckResponse(BaseModel):
    """Advanced mentions check response."""
    companyName: str
    visibility: float  # Presence-based visibility score (0-100%)
    band: str  # Dominant/Strong/Moderate/Weak/Minimal
    mentions: int  # Total capped mentions across all responses
    presence_rate: float  # What % of responses mentioned the company (0-100%)
    quality_score: float  # Average quality score when mentioned (0-10)
    max_quality: float  # Maximum possible quality (responses × 10)
    platform_stats: Dict[str, PlatformStats]
    dimension_stats: Dict[str, DimensionStats]
    query_results: List[QueryResult]
    actualQueriesProcessed: int
    execution_time_seconds: float
    total_cost: float
    total_tokens: int
    mode: str
    tldr: TLDRSummary

# Combined Analysis Models
class MasterAnalysisRequest(BaseModel):
    """Master analysis request combining health + mentions."""
    url: str
    companyName: str
    companyAnalysis: Optional[CompanyAnalysis] = None
    # Health options
    include_performance: bool = True
    include_accessibility: bool = True
    # Mentions options
    language: str = "english"
    country: str = "US"
    numQueries: int = 10  # Production standard (10 queries)
    mode: str = "balanced"  # fast/balanced/full
    generateInsights: bool = True
    platforms: Optional[List[str]] = None

class MasterAnalysisResponse(BaseModel):
    """Complete master analysis response."""
    url: str
    companyName: str
    # Health results
    health: HealthCheckResponse
    # Mentions results  
    mentions: MentionsCheckResponse
    # Combined insights
    combined_score: float  # Weighted health + visibility score
    combined_grade: str
    strategic_recommendations: List[str]
    priority_actions: List[str]
    execution_time_seconds: float

# ==================== AI Platform Configuration ====================

# Enhanced platform configuration combining both implementations
AI_PLATFORMS = {
    "perplexity": {
        "model": "perplexity/sonar-pro",
        "has_search": True,  # Native search built-in
        "needs_tool": False,  # Perplexity has native web search
        "provider": None,
        "cost_per_token": 0.001,  # Approximate
    },
    "claude": {
        "model": "anthropic/claude-3.5-sonnet",
        "has_search": True,
        "needs_tool": True,  # Uses google_search tool
        "provider": None,
        "cost_per_token": 0.003,
    },
    "chatgpt": {
        "model": "openai/gpt-4.1",  # Latest model
        "has_search": True,
        "needs_tool": True,  # Uses google_search tool
        "provider": "openai",  # Force OpenAI provider
        "cost_per_token": 0.002,
    },
    "gemini": {
        "model": "google/gemini-3-pro-preview",
        "has_search": True,
        "needs_tool": False,  # Uses native Google search grounding
        "provider": "native_gemini",  # Enhanced: Will use native SDK when available
        "cost_per_token": 0.001,
    },
    "mistral": {
        "model": "mistralai/mistral-large",
        "has_search": True,
        "needs_tool": True,  # Uses google_search tool
        "provider": None,
        "cost_per_token": 0.002,
    },
}

# ==================== Initialization ====================

# Use native Gemini client with Google Search support
def get_ai_client():
    """Get native Gemini client instance with Google Search support."""
    return get_gemini_client()

# ==================== Health Check Implementation ====================

@app.post("/health/check", response_model=HealthCheckResponse)
async def health_check(request: HealthCheckRequest):
    """
    Advanced AEO Health Check - v4.0 Tiered Objective Scoring
    
    Performs 29 checks across 4 categories with hierarchical gating:
    - AI Access Gate (Tier 0): Critical - blocks all AI if failed
    - Schema Gate (Tier 1): Essential - limits AI understanding if failed
    - Quality Gate (Tier 2): Important - affects optimization quality
    - Excellence (Tier 3): Full optimization potential
    
    Returns comprehensive analysis with actionable recommendations.
    """
    start_time = time.time()
    logger.info(f"Starting health check for: {request.url}")
    
    try:
        # Fetch website with enhanced error handling
        fetch_result = await fetch_website(request.url)
        
        if not fetch_result.success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to fetch website: {fetch_result.error}"
            )
        
        soup = BeautifulSoup(fetch_result.content, 'html.parser')
        
        # Run all check categories with correct signatures
        # Technical checks: needs soup, final_url, sitemap_found, response_time_ms
        technical_results = run_technical_checks(
            soup=soup,
            final_url=request.url,
            sitemap_found=getattr(fetch_result, 'sitemap_found', False),
            response_time_ms=int(getattr(fetch_result, 'response_time', 0.5) * 1000)
        )
        
        # Structured data checks: only needs soup
        structured_data_results = run_structured_data_checks(soup)
        
        # AEO crawler checks: needs robots_txt (extract from fetch_result)
        robots_txt = getattr(fetch_result, 'robots_txt', None)
        crawler_results = run_aeo_crawler_checks(robots_txt)
        
        # Authority checks: needs soup and same_as_urls (extract from structured data)
        schema_types, all_schemas, org_schema = extract_schema_data(soup)
        same_as_urls = []
        if org_schema and 'sameAs' in org_schema:
            same_as_urls = org_schema['sameAs'] if isinstance(org_schema['sameAs'], list) else [org_schema['sameAs']]
        authority_results = run_authority_checks(soup, same_as_urls)
        
        # Flatten all results into a single list for tiered scoring
        all_issues = []
        all_issues.extend(technical_results)
        all_issues.extend(structured_data_results) 
        all_issues.extend(crawler_results)
        all_issues.extend(authority_results)
        
        # Calculate scores using v4.0 tiered system
        overall_score, tier_details = calculate_tiered_score(all_issues)
        
        # Calculate grade and visibility band
        grade = calculate_grade(overall_score)
        visibility_band, band_color = calculate_visibility_band(overall_score)
        
        # Count issues by severity (using flattened list)
        issues_summary = count_issues_by_severity(all_issues)
        
        # Generate category results
        categories = []
        for category_name, results in [
            ("Technical SEO", technical_results),
            ("Structured Data", structured_data_results),
            ("AI Crawler Access", crawler_results),
            ("Authority/E-E-A-T", authority_results)
        ]:
            category_checks = []
            for check in results:
                # Map check result format to our expected format
                status = "pass" if check.get("passed", False) else "fail"
                impact = check.get("severity", "medium")
                
                category_checks.append(CheckResult(
                    name=check.get("check", "unknown_check"),
                    status=status,
                    message=check.get("message", ""),
                    impact=impact,
                    recommendation=check.get("recommendation", ""),
                    score=check.get("score_impact", 0),
                    max_score=10  # Default max score
                ))
            
            category_score = sum(check.get("score_impact", 0) for check in results)
            max_category_score = len(results) * 10  # All checks have max score of 10
            category_grade = calculate_grade((category_score / max_category_score) * 100 if max_category_score > 0 else 0)
            
            # Generate category summary
            if category_name == "Technical SEO":
                summary_dict = extract_technical_summary(soup, request.url)
                summary = json.dumps(summary_dict) if summary_dict else ""
            elif category_name == "Structured Data":
                summary_dict = extract_structured_data_summary(soup)
                summary = json.dumps(summary_dict) if summary_dict else ""
            elif category_name == "AI Crawler Access":
                summary_dict = extract_crawler_summary(robots_txt)
                summary = json.dumps(summary_dict) if summary_dict else ""
            else:
                summary_dict = extract_authority_summary(soup, same_as_urls)
                summary = json.dumps(summary_dict) if summary_dict else ""
            
            categories.append(CategoryResult(
                name=category_name,
                score=category_score,
                max_score=max_category_score,
                grade=category_grade,
                checks=category_checks,
                summary=summary
            ))
        
        # Generate recommendations based on tiered scoring
        recommendations = generate_health_recommendations(
            overall_score, categories, issues_summary
        )
        
        execution_time = time.time() - start_time
        
        logger.info(f"Health check completed in {execution_time:.2f}s: {overall_score:.1f}/100 ({grade})")
        
        return HealthCheckResponse(
            url=request.url,
            overall_score=round(overall_score, 1),
            max_score=100.0,
            grade=grade,
            visibility_band=visibility_band,
            categories=categories,
            issues_summary=issues_summary,
            recommendations=recommendations,
            execution_time_seconds=round(execution_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

def generate_health_recommendations(
    overall_score: float, 
    categories: List[CategoryResult], 
    issues_summary: Dict[str, int]
) -> List[str]:
    """Generate tiered recommendations based on health score."""
    recommendations = []
    
    # Critical issues (Tier 0)
    if overall_score < 25:
        recommendations.append("CRITICAL: Fix AI crawler blocking issues immediately - your site is invisible to AI platforms")
        recommendations.append("Priority 1: Remove robots.txt blocks for AI crawlers (GPTBot, ChatGPT-User, etc.)")
    
    # Schema issues (Tier 1)  
    if overall_score < 45:
        recommendations.append("Essential: Add Organization schema markup - AI platforms cannot identify your company")
        recommendations.append("Priority 2: Implement basic schema.org structured data for company identification")
    
    # Quality issues (Tier 2)
    if 45 <= overall_score < 75:
        recommendations.append("Important: Enhance content quality and schema completeness")
        recommendations.append("Focus on: Complete product/service schema and improve content depth")
    
    # Excellence opportunities (Tier 3)
    if overall_score >= 75:
        recommendations.append("Optimization: Fine-tune advanced schema and authority signals")
        recommendations.append("Next level: Implement comprehensive FAQ and How-to schema")
    
    # Category-specific recommendations
    for category in categories:
        if category.score / category.max_score < 0.6:  # Less than 60%
            if "Technical" in category.name:
                recommendations.append("Technical: Address core SEO hygiene issues")
            elif "Structured" in category.name:
                recommendations.append("Schema: Implement missing structured data elements")
            elif "Crawler" in category.name:
                recommendations.append("Access: Remove AI crawler restrictions")
            elif "Authority" in category.name:
                recommendations.append("Trust: Strengthen E-E-A-T and authority signals")
    
    return recommendations[:6]  # Limit to top 6 recommendations

# ==================== Advanced Mentions Check Implementation ====================
# (Combining best features from aeo-leaderboard with enhancements)

# Quality Scoring Functions (from aeo-leaderboard, enhanced)
def detect_mention_type(text: str, company_name: str) -> str:
    """Enhanced mention quality type detection."""
    text_lower = text.lower()
    company_lower = company_name.lower()

    # Primary recommendation patterns (highest value)
    recommend_patterns = [
        f"recommend {company_lower}",
        f"i recommend {company_lower}",
        f"{company_lower} is the best",
        f"best.*{company_lower}",
        f"{company_lower}.*excellent",
        f"top choice.*{company_lower}",
        f"highly recommend.*{company_lower}"
    ]

    for pattern in recommend_patterns:
        if re.search(pattern, text_lower):
            return 'primary_recommendation'

    # Top option patterns (high value)
    top_patterns = [
        f"(top|leading|best).*{company_lower}",
        f"{company_lower}.*(top|leading|best)",
        f"among.*{company_lower}",
        f"{company_lower}.*among.*the",
        f"one of the best.*{company_lower}",
        f"{company_lower}.*stands out"
    ]
    
    for pattern in top_patterns:
        if re.search(pattern, text_lower):
            return 'top_option'

    # Listed option patterns
    if re.search(f"\\d+\\.|\\*.*{company_lower}", text):
        return 'listed_option'

    # Simple mention
    if company_lower in text_lower:
        return 'mentioned_in_context'

    return 'none'

def detect_list_position(text: str, company_name: str) -> Optional[int]:
    """Detect position in numbered/bulleted lists."""
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if re.search(re.escape(company_name), line, re.IGNORECASE):
            # Check for numbered list
            match = re.match(r'^\s*([\d]+)[\.)\s]', line)
            if match:
                return int(match.group(1))
            # Check for bullet list  
            if re.match(r'^\s*[\*\-\•]', line):
                return i + 1
    return None

def count_mentions_advanced(text: str, company_name: str) -> Dict[str, Any]:
    """
    Advanced mention counting with sophisticated quality scoring.
    
    Enhanced scoring philosophy:
    - Base score by mention type (how valuable is this mention?)
    - Position bonus (first in list = more valuable)
    - Multiple mentions bonus (up to cap)
    - Brand context analysis
    """
    raw_mentions = len(re.findall(re.escape(company_name), text, re.IGNORECASE))
    
    if raw_mentions == 0:
        return {
            'raw_mentions': 0,
            'capped_mentions': 0,
            'quality_score': 0.0,
            'mention_type': 'none',
            'position': None,
        }

    capped_mentions = min(raw_mentions, 3)  # Cap at 3
    mention_type = detect_mention_type(text, company_name)
    position = detect_list_position(text, company_name)

    # Enhanced base scores
    base_scores = {
        'primary_recommendation': 9.5,   # "I recommend X" - highest value
        'top_option': 7.5,               # "top/leading/best X" - high value  
        'listed_option': 5.0,            # Listed among options - medium value
        'mentioned_in_context': 3.5,     # Just mentioned - still valuable
        'none': 0.0,                     # Not mentioned - no value
    }
    base_score = base_scores.get(mention_type, 3.5)

    # Enhanced position bonus
    position_bonus = 0.0
    if position:
        if position == 1:
            position_bonus = 2.5   # #1 position is very valuable
        elif position <= 3:
            position_bonus = 1.5   # Top 3 is good
        elif position <= 5:
            position_bonus = 0.8   # Top 5 is okay
        # 6+ gets no bonus

    # Multiple mentions bonus
    mention_bonus = min(1.2, (capped_mentions - 1) * 0.6)  # 0, 0.6, or 1.2

    quality_score = min(10.0, base_score + position_bonus + mention_bonus)

    return {
        'raw_mentions': raw_mentions,
        'capped_mentions': capped_mentions,
        'quality_score': round(quality_score, 2),
        'mention_type': mention_type,
        'position': position,
    }

# Advanced Query Generation (from aeo-leaderboard, enhanced)
async def generate_advanced_queries(
    company_name: str,
    company_analysis: Optional[CompanyAnalysis],
    num_queries: int = 10,
    mode: str = "balanced",
    country: str = "US",
    language: str = "english",
) -> List[Dict[str, str]]:
    """
    HYPERNICHE query generation using Gemini 2.5 Flash with structured JSON output.
    
    Generates sophisticated multi-dimensional targeting queries:
    - 70% UNBRANDED: Industry + Role + Geo + Company Size layers
    - 20% COMPETITIVE: Competitor alternatives and comparisons  
    - 10% BRANDED: Company + Product combinations
    
    Based on aeo-leaderboard's proven hyperniche query generation.
    """
    try:
        # Try AI-powered hyperniche generation first
        return await generate_queries_with_gemini_ai(
            company_name, company_analysis, num_queries, mode, country, language
        )
    except Exception as e:
        logger.warning(f"AI query generation failed for {company_name}: {e}, falling back to rule-based")
        # Fallback to rule-based generation
        return await generate_queries_fallback(
            company_name, company_analysis, num_queries, mode, country, language
        )


async def generate_queries_with_gemini_ai(
    company_name: str,
    company_analysis: Optional[CompanyAnalysis],
    num_queries: int = 10,
    mode: str = "balanced",
    country: str = "US",
    language: str = "english",
) -> List[Dict[str, str]]:
    """Generate hyperniche queries using Gemini 2.5 Flash with sophisticated targeting."""
    
    # Extract company context
    info = {}
    competitors = []
    if company_analysis and company_analysis.companyInfo:
        info = company_analysis.companyInfo.dict()
    if company_analysis and company_analysis.competitors:
        competitors = [c.dict() for c in company_analysis.competitors][:3]  # Top 3 competitors
    
    # Build hyperniche targeting data
    industry = clean_query_term(info.get("industry", ""))
    products = [clean_query_term(p) for p in (info.get("products", []) or [])[:3] if clean_query_term(p)]
    services = [clean_query_term(s) for s in (info.get("services", []) or [])[:2] if clean_query_term(s)]
    
    # Handle ICP data (might be string or list)
    icp_raw = info.get("target_audience", "") or info.get("icp", "") or ""
    if isinstance(icp_raw, list):
        icp_text = ", ".join(icp_raw) if icp_raw else ""
    else:
        icp_text = icp_raw or ""
    
    # Extract sophisticated targeting dimensions
    hyperniche_data = {
        "industry": industry,
        "product_category": clean_query_term(info.get("productCategory", "")),
        "products": products,
        "services": services,
        "target_industries": extract_target_industries_from_icp(icp_text),
        "company_size": extract_company_size_from_icp(icp_text),
        "roles": extract_roles_from_icp(icp_text),
        "pain_points": info.get("pain_points", []) or [],
        "competitors": [c.get('name', '') for c in competitors if c.get('name')],
        "geo_suffix": "United States" if country in ["US", "USA"] else country if should_add_geographic_modifier(country) else ""
    }
    
    # Build sophisticated AI prompt for hyperniche query generation
    prompt = f"""Generate {num_queries} HYPERNICHE, highly targeted AEO visibility queries that test real organic visibility using sophisticated B2B targeting.

HYPERNICHE TARGETING DATA:
- Industry: {hyperniche_data.get('industry', 'N/A')}
- Products: {hyperniche_data.get('products', [])}
- Services: {hyperniche_data.get('services', [])}
- Target Industries: {hyperniche_data.get('target_industries', [])}
- Company Size: {hyperniche_data.get('company_size', 'N/A')}
- Roles: {hyperniche_data.get('roles', [])}
- Geographic: {hyperniche_data.get('geo_suffix', '')}
- Competitors: {hyperniche_data.get('competitors', [])}
- Pain Points: {hyperniche_data.get('pain_points', [])}
- Target Audience: {icp_text}

QUERY DISTRIBUTION (follow this exact ratio):
70% UNBRANDED_HYPERNICHE (organic visibility test):
1. PRODUCT_INDUSTRY_GEO: "best [product] for [target_industry] {hyperniche_data.get('geo_suffix', '')}"
2. SERVICE_INDUSTRY_GEO: "[service] for [target_industry] {hyperniche_data.get('geo_suffix', '')}"
3. INDUSTRY_PRODUCT_ENTERPRISE: "enterprise [industry] [product] solutions"
4. TARGET_ROLE_SPECIFIC: "[product] for [specific_role] in [target_industry]"
5. COMPANY_SIZE_SPECIFIC: "[product] for [company_size] [target_industry] companies"
6. PAIN_POINT_SOLUTION: "best tools for [key_phrase_from_pain_point]"
7. GEOGRAPHIC_NICHE: "[product/service] [target_industry] {hyperniche_data.get('geo_suffix', '')}"

20% COMPETITIVE_HYPERNICHE:
8. COMPETITOR_ALTERNATIVE: "alternatives to [competitor] for [target_industry]"
9. COMPETITOR_VS_CATEGORY: "[competitor] vs [product_category] for [company_size]"

10% BRANDED_DIRECT:
10. BRANDED_PRODUCT: "{company_name} [main_product]" (always include product if available)

CRITICAL HYPERNICHE REQUIREMENTS:
- 70% MUST NOT mention {company_name} at all
- Layer 2-3 targeting dimensions per query (Industry + Role + Geo, Product + Company_Size + Pain_Point, etc.)
- Use EXACT target industries, roles, company sizes from the data
- Include geographic qualifiers when available
- Extract key phrases from pain points for problem-solution queries
- Generate queries in {language} language for {country} market
- Make queries HYPER-SPECIFIC to actual B2B search patterns
- Each query should be searchable by the exact ICP described
- Focus on multi-dimensional targeting
- NEVER duplicate the company name
- NEVER use unrelated competitors

EXAMPLES for AEO consulting company targeting "enterprise SaaS companies":
✅ HYPERNICHE: "AEO consulting for SaaS companies United States", "ChatGPT optimization for B2B software enterprise", "AI visibility for Marketing Directors in SaaS"
✅ BRANDED_PRODUCT: "SCAILE AEO consulting", "SCAILE AI visibility", "SCAILE ChatGPT optimization"
❌ GENERIC: "best AEO consulting", "SEO services", "SCAILE" (brand only without product)

Return exactly {num_queries} queries as a JSON array:
[{{"query": "actual search query", "dimension": "HYPERNICHE_TYPE"}}]"""

    try:
        # Use AI client to generate sophisticated queries
        ai_client = get_ai_client()
        
        response = await ai_client.query_with_structured_output(
            prompt=prompt,
            system_prompt="You are a B2B hyperniche query generation expert. Generate highly specific, multi-dimensional targeting queries that test organic visibility for the exact ICP described.",
            model="gemini-2.5-flash",
            response_format="json"
        )
        
        if response.get("success") and response.get("response"):
            try:
                # Parse JSON response
                queries_data = json.loads(response["response"])
                
                # Validate and clean up
                valid_queries = []
                for q in queries_data:
                    if isinstance(q, dict) and "query" in q and "dimension" in q:
                        query_text = q["query"].strip()
                        dimension = q["dimension"].strip()
                        if query_text and dimension and len(query_text) <= 200:
                            valid_queries.append({"query": query_text, "dimension": dimension})
                
                if valid_queries:
                    logger.info(f"✅ Generated {len(valid_queries)} hyperniche queries for {company_name} via Gemini AI")
                    return valid_queries[:num_queries]
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed for {company_name}: {e}")
        
        # If AI generation fails, fallback to rule-based
        logger.warning(f"AI query generation failed for {company_name}, falling back to rule-based")
        return await generate_queries_fallback(company_name, company_analysis, num_queries, mode, country, language)
        
    except Exception as e:
        logger.error(f"Error in AI query generation for {company_name}: {e}")
        return await generate_queries_fallback(company_name, company_analysis, num_queries, mode, country, language)


async def generate_queries_fallback(
    company_name: str,
    company_analysis: Optional[CompanyAnalysis],
    num_queries: int = 10,
    mode: str = "balanced",
    country: str = "US",
    language: str = "english",
) -> List[Dict[str, str]]:
    """Fallback rule-based query generation when AI fails."""
    queries = []
    
    # Extract company context
    info = {}
    competitors = []
    if company_analysis and company_analysis.companyInfo:
        info = company_analysis.companyInfo.dict()
    if company_analysis and company_analysis.competitors:
        competitors = [c.dict() for c in company_analysis.competitors]
    
    # Build sophisticated targeting data
    hyperniche_data = extract_hyperniche_targeting(info, competitors, country)
    
    # Generate query distribution based on mode
    if mode == "fast":
        num_queries = min(num_queries, 10)
        unbranded_count = int(num_queries * 0.7)  # Match aeo-leaderboard ratio
        competitive_count = int(num_queries * 0.2)
        branded_count = num_queries - unbranded_count - competitive_count
    elif mode == "balanced":
        num_queries = min(num_queries, 25)
        unbranded_count = int(num_queries * 0.7)
        competitive_count = int(num_queries * 0.2)
        branded_count = num_queries - unbranded_count - competitive_count
    else:  # full
        num_queries = min(num_queries, 50)
        unbranded_count = int(num_queries * 0.75)
        competitive_count = int(num_queries * 0.20)
        branded_count = num_queries - unbranded_count - competitive_count
    
    # Generate unbranded queries (organic visibility test)
    queries.extend(generate_unbranded_queries(hyperniche_data, unbranded_count, language))
    
    # Generate competitive queries
    queries.extend(generate_competitive_queries(company_name, hyperniche_data, competitive_count))
    
    # Generate branded queries
    queries.extend(generate_branded_queries(company_name, hyperniche_data, branded_count))
    
    return queries[:num_queries]

def extract_hyperniche_targeting(
    info: Dict[str, Any], 
    competitors: List[Dict[str, Any]], 
    country: str
) -> Dict[str, Any]:
    """Extract sophisticated targeting dimensions for hyperniche queries."""
    # Clean and extract key data
    industry = clean_query_term(info.get("industry", ""))
    product_category = clean_query_term(info.get("productCategory", ""))
    products = [clean_query_term(p) for p in (info.get("products", []) or [])[:3] if clean_query_term(p)]
    services = [clean_query_term(s) for s in (info.get("services", []) or [])[:2] if clean_query_term(s)]
    
    # Handle ICP data (might be string or list)
    icp_raw = info.get("target_audience", "") or info.get("icp", "") or ""
    if isinstance(icp_raw, list):
        icp_text = ", ".join(icp_raw) if icp_raw else ""
    else:
        icp_text = icp_raw or ""
    
    return {
        "industry": industry,
        "product_category": product_category,
        "products": products,
        "services": services,
        "target_industries": extract_target_industries_from_icp(icp_text),
        "company_size": extract_company_size_from_icp(icp_text),
        "roles": extract_roles_from_icp(icp_text),
        "pain_points": info.get("pain_points", []) or [],
        "competitors": [c.get('name', '') for c in competitors[:3] if c.get('name')],
        "geo_suffix": "United States" if country in ["US", "USA"] else country if should_add_geographic_modifier(country) else ""
    }

def clean_query_term(term: str) -> str:
    """Clean query terms by removing noise and limiting length."""
    if not term:
        return ""
    # Remove parentheticals
    term = re.sub(r'\([^)]*\)', '', term)
    # Clean slashes
    term = re.sub(r'\s*/\s*', ' ', term)
    # Limit words and length
    words = term.split()
    if len(words) > 3:
        term = ' '.join(words[:3])
    if len(term) > 60:
        term = term[:57] + '...'
    return term.strip()

# Helper functions from aeo-leaderboard (condensed)
def extract_company_size_from_icp(icp_text: str) -> str:
    """Extract company size indicators from ICP text."""
    if not icp_text:
        return ""
    
    icp_lower = icp_text.lower()
    if any(term in icp_lower for term in ['startup', 'small business', 'smb']):
        return "startups"
    elif any(term in icp_lower for term in ['enterprise', 'large']):
        return "enterprise companies"
    elif 'mid-size' in icp_lower or 'medium' in icp_lower:
        return "mid-size companies"
    return ""

def extract_roles_from_icp(icp_text: str) -> List[str]:
    """Extract target roles from ICP text."""
    if not icp_text:
        return []
    
    roles = []
    role_patterns = [
        r'\b(cmos?|ceos?|ctos?|cfos?)\b',
        r'\b(marketing directors?|content managers?|seo managers?)\b',
    ]
    
    for pattern in role_patterns:
        matches = re.findall(pattern, icp_text, re.IGNORECASE)
        for match in matches:
            if len(roles) < 2:  # Limit to 2 roles
                roles.append(match.upper() + 's' if match.upper() in ['CMO', 'CEO', 'CTO', 'CFO'] else match)
    
    return roles

def extract_target_industries_from_icp(icp_text: str) -> List[str]:
    """Extract target industries from ICP text."""
    if not icp_text:
        return []
    
    industry_patterns = [
        r'\b(saas|software)\s+companies?\b',
        r'\b(e-?commerce)\s+companies?\b', 
        r'\b(fintech|financial\s+services?)\b',
        r'\b(healthcare|healthtech)\b',
    ]
    
    industries = []
    for pattern in industry_patterns:
        if re.search(pattern, icp_text, re.IGNORECASE) and len(industries) < 2:
            industries.append(f"{pattern.split('|')[0].title()} companies")
    
    return industries

def should_add_geographic_modifier(country: str) -> bool:
    """Check if geographic modifier should be added to queries."""
    skip_countries = ['US', 'USA', 'United States', 'Global', 'International']
    return country and country not in skip_countries

def generate_unbranded_queries(hyperniche_data: Dict[str, Any], count: int, language: str) -> List[Dict[str, str]]:
    """Generate unbranded queries for organic visibility testing."""
    queries = []
    
    # Product + Industry queries
    for product in hyperniche_data["products"][:2]:
        if product:
            queries.append({"query": f"best {product}", "dimension": "Product"})
            if hyperniche_data["industry"]:
                queries.append({"query": f"best {product} for {hyperniche_data['industry']}", "dimension": "Product-Industry"})
    
    # Target industry queries  
    for industry in hyperniche_data["target_industries"][:2]:
        main_product = hyperniche_data["products"][0] if hyperniche_data["products"] else "software"
        queries.append({"query": f"{main_product} for {industry}", "dimension": "Target-Industry"})
    
    # Role-based queries
    for role in hyperniche_data["roles"][:1]:
        main_product = hyperniche_data["products"][0] if hyperniche_data["products"] else "tools"
        queries.append({"query": f"best {main_product} for {role}", "dimension": "Role-Specific"})
    
    # Geographic queries
    if hyperniche_data["geo_suffix"]:
        main_product = hyperniche_data["products"][0] if hyperniche_data["products"] else "software"
        queries.append({"query": f"best {main_product} {hyperniche_data['geo_suffix']}", "dimension": "Geographic"})
    
    return queries[:count]

def generate_competitive_queries(company_name: str, hyperniche_data: Dict[str, Any], count: int) -> List[Dict[str, str]]:
    """Generate competitive positioning queries."""
    queries = []
    
    # General alternatives
    queries.append({"query": f"{company_name} alternatives", "dimension": "Competitive"})
    
    # Specific competitor comparisons
    for competitor in hyperniche_data["competitors"][:2]:
        if competitor:
            queries.append({"query": f"{company_name} vs {competitor}", "dimension": "Competitive-Specific"})
            queries.append({"query": f"alternatives to {competitor}", "dimension": "Competitive-Alternative"})
    
    return queries[:count]

def generate_branded_queries(company_name: str, hyperniche_data: Dict[str, Any], count: int) -> List[Dict[str, str]]:
    """Generate branded queries."""
    queries = []
    
    # Basic branded
    queries.append({"query": company_name, "dimension": "Branded"})
    
    # Branded + product
    main_product = hyperniche_data["products"][0] if hyperniche_data["products"] else "software"
    queries.append({"query": f"{company_name} {main_product}", "dimension": "Branded-Product"})
    
    return queries[:count]

# AI Platform Query Functions (enhanced from both implementations)
async def query_platform_advanced(
    platform: str,
    query: str,
    model_config: Dict[str, Any],
    company_name: str,
) -> Dict[str, Any]:
    """Advanced AI platform querying with enhanced error handling."""
    model = model_config["model"]
    needs_tool = model_config.get("needs_tool", False)
    provider = model_config.get("provider")
    
    try:
        # Use appropriate tools based on platform
        tools = ["google_search"] if needs_tool else None
        messages = [{"role": "user", "content": query}]
        
        # Enhanced: Use native Gemini when available
        if platform == "gemini" and provider == "native_gemini":
            # Use native Gemini SDK with search grounding
            try:
                gemini_client = get_ai_client()  # This now returns Gemini client
                result = await gemini_client.query_mentions_with_search_grounding(query, company_name)
                
                if result.get("success"):
                    return {
                        "platform": platform,
                        "query": query,
                        "response": result["response"],
                        "model": result["model"],
                        "has_search_grounding": True,
                        "search_enabled": True,
                        "provider": "native_gemini"
                    }
            except Exception as e:
                logger.error(f"Native Gemini error: {e}, falling back to standard completion")
        
        # Use OpenRouter for other platforms or fallback
        ai_client = get_ai_client()
        result = await ai_client.complete_with_tools(
            messages=messages,
            model=model,
            tools=tools,
            temperature=0.7,
            max_tokens=1024,
            provider=provider
        )
        
        # Extract response
        choice = result.get("choices", [{}])[0]
        content = choice.get("message", {}).get("content", "")
        
        return {
            "platform": platform,
            "response": content,
            "tokens": result.get("usage", {}).get("total_tokens", 0),
            "cost": estimate_cost(result.get("usage", {}).get("total_tokens", 0), model_config),
        }
            
    except Exception as e:
        logger.error(f"{platform} query error: {e}")
        return {"error": str(e), "platform": platform}

def estimate_cost(tokens: int, model_config: Dict[str, Any]) -> float:
    """Estimate API cost based on tokens and model."""
    cost_per_token = model_config.get("cost_per_token", 0.001)
    return tokens * cost_per_token

async def query_all_platforms_parallel(
    query: str,
    platforms: List[str],
    company_name: str = None,
) -> List[Dict[str, Any]]:
    """Query all platforms in parallel with enhanced error handling."""
    tasks = []
    for platform in platforms:
        if platform in AI_PLATFORMS:
            tasks.append(query_platform_advanced(
                platform, query, AI_PLATFORMS[platform], company_name or ""
            ))
    
    return await asyncio.gather(*tasks, return_exceptions=True)

@app.post("/mentions/check", response_model=MentionsCheckResponse) 
async def mentions_check_advanced(request: MentionsCheckRequest):
    """
    Advanced AEO Mentions Check with Sophisticated Business Intelligence
    
    Combines best features from aeo-leaderboard implementation:
    - Hyperniche query generation with AI assistance
    - Quality-adjusted scoring with mention type detection
    - Brand confusion analysis and competitive positioning
    - Comprehensive TL;DR with actionable recommendations
    
    Requires company analysis data for meaningful results.
    """
    import time
    start_time = time.time()
    
    # Validate company analysis data (strict requirement)
    if not request.companyAnalysis or not request.companyAnalysis.companyInfo:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Company analysis data required",
                "message": "Advanced mentions check requires company analysis with products/services data for meaningful visibility scores."
            }
        )
    
    company_info = request.companyAnalysis.companyInfo
    products = company_info.products or []
    services = company_info.services or []
    
    if not products and not services:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Insufficient company data",
                "message": "At least one product or service is required from company analysis for targeted query generation."
            }
        )
    
    logger.info(f"Starting advanced mentions check for {request.companyName} (mode: {request.mode})")
    
    # Determine platforms to use
    if request.platforms:
        platforms = request.platforms
    elif request.mode == "fast":
        platforms = ["gemini", "chatgpt"]  # Fast mode: top 2 platforms
    elif request.mode == "balanced":
        platforms = ["gemini", "chatgpt", "claude", "perplexity"]  # Balanced: 4 platforms
    else:
        platforms = list(AI_PLATFORMS.keys())  # Full: all platforms
    
    # Generate advanced queries
    queries = await generate_advanced_queries(
        request.companyName,
        request.companyAnalysis,
        request.numQueries,
        request.mode,
        request.country,
        request.language,
    )
    logger.info(f"Generated {len(queries)} hyperniche queries")
    
    # Initialize stats tracking
    platform_stats = {p: PlatformStats(mentions=0, quality_score=0, responses=0, errors=0) for p in platforms}
    dimension_stats: Dict[str, DimensionStats] = {}
    query_results: List[QueryResult] = []
    total_mentions = 0
    total_quality = 0.0
    total_tokens = 0
    total_cost = 0.0
    
    # Get competitors for analysis
    competitors = []
    if request.companyAnalysis:
        competitors = [c.dict() for c in request.companyAnalysis.competitors]
    
    # Initialize dimension stats
    for query_data in queries:
        dimension = query_data["dimension"]
        if dimension not in dimension_stats:
            dimension_stats[dimension] = DimensionStats(mentions=0, quality_score=0, queries=0)
        dimension_stats[dimension].queries += 1
    
    # Process all queries in parallel for maximum efficiency
    async def process_single_query(query_data):
        query = query_data["query"]
        dimension = query_data["dimension"]
        logger.info(f"Querying: '{query}' ({dimension})")
        results = await query_all_platforms_parallel(query, platforms, request.companyName)
        return {"query_data": query_data, "results": results}
    
    logger.info(f"Processing {len(queries)} queries across {len(platforms)} platforms in parallel...")
    all_query_results = await asyncio.gather(
        *[process_single_query(q) for q in queries],
        return_exceptions=True
    )
    logger.info("All queries completed")
    
    # Process results with advanced analytics
    for query_result in all_query_results:
        if isinstance(query_result, Exception):
            logger.error(f"Query failed: {query_result}")
            continue
        
        query_data = query_result["query_data"]
        results = query_result["results"]
        query = query_data["query"]
        dimension = query_data["dimension"]
        
        for result in results:
            if isinstance(result, Exception):
                continue
            
            platform = result.get("platform", "unknown")
            
            if "error" in result:
                if platform in platform_stats:
                    platform_stats[platform].errors += 1
                continue
            
            response_text = result.get("response", "")
            tokens = result.get("tokens", 0)
            cost = result.get("cost", 0.0)
            
            # Advanced mention analysis
            mention_data = count_mentions_advanced(response_text, request.companyName)
            
            # Extract competitor mentions
            comp_mentions = extract_competitor_mentions_advanced(response_text, competitors)
            
            # Create detailed query result
            qr = QueryResult(
                query=query,
                dimension=dimension,
                platform=platform,
                raw_mentions=mention_data["raw_mentions"],
                capped_mentions=mention_data["capped_mentions"],
                quality_score=mention_data["quality_score"],
                mention_type=mention_data["mention_type"],
                position=mention_data["position"],
                competitor_mentions=comp_mentions,
                response_text=response_text[:500],  # Truncate for storage
            )
            query_results.append(qr)
            
            # Update comprehensive stats
            if platform in platform_stats:
                platform_stats[platform].mentions += mention_data["capped_mentions"]
                platform_stats[platform].quality_score += mention_data["quality_score"]
                platform_stats[platform].responses += 1
                platform_stats[platform].total_tokens += tokens
                platform_stats[platform].cost += cost
            
            dimension_stats[dimension].mentions += mention_data["capped_mentions"]
            dimension_stats[dimension].quality_score += mention_data["quality_score"]
            
            total_mentions += mention_data["capped_mentions"]
            total_quality += mention_data["quality_score"]
            total_tokens += tokens
            total_cost += cost
    
    # Calculate advanced visibility metrics
    total_responses = sum(s.responses for s in platform_stats.values())
    max_quality = total_responses * 10.0
    
    # Presence rate (how often mentioned)
    responses_with_mentions = sum(1 for qr in query_results if qr.mention_type != 'none')
    presence_rate = responses_with_mentions / total_responses if total_responses > 0 else 0
    
    # Average quality when mentioned
    avg_quality_when_mentioned = total_quality / max(responses_with_mentions, 1) if responses_with_mentions > 0 else 0
    
    # Enhanced visibility calculation with quality weighting
    quality_factor = 0.85 + (avg_quality_when_mentioned / 10) * 0.30
    visibility = min(100.0, presence_rate * quality_factor * 100)
    visibility = round(visibility, 1)
    
    # Determine visibility band
    if visibility >= 80:
        band = "Dominant"
    elif visibility >= 60:
        band = "Strong"  
    elif visibility >= 40:
        band = "Moderate"
    elif visibility >= 20:
        band = "Weak"
    else:
        band = "Minimal"
    
    # Calculate average quality scores
    for platform in platforms:
        if platform in platform_stats and platform_stats[platform].responses > 0:
            platform_stats[platform].quality_score /= platform_stats[platform].responses
    
    for dimension in dimension_stats:
        if dimension_stats[dimension].queries > 0:
            dimension_stats[dimension].quality_score /= dimension_stats[dimension].queries
    
    # Generate advanced TL;DR summary with business intelligence
    tldr_summary = generate_advanced_tldr_summary(
        company_name=request.companyName,
        visibility=visibility,
        band=band,
        platform_stats=platform_stats,
        dimension_stats=dimension_stats,
        query_results=query_results
    )
    
    execution_time = time.time() - start_time
    
    logger.info(f"Advanced mentions check complete: visibility={visibility:.1f}% (presence={presence_rate*100:.1f}%), band={band}, mentions={total_mentions}")
    
    return MentionsCheckResponse(
        companyName=request.companyName,
        visibility=visibility,
        band=band,
        mentions=total_mentions,
        presence_rate=round(presence_rate * 100, 1),
        quality_score=round(avg_quality_when_mentioned, 2),
        max_quality=max_quality,
        platform_stats=platform_stats,
        dimension_stats=dimension_stats,
        query_results=query_results,
        actualQueriesProcessed=len(queries),
        execution_time_seconds=round(execution_time, 2),
        total_cost=round(total_cost, 4),
        total_tokens=total_tokens,
        mode=request.mode,
        tldr=tldr_summary,
    )

def extract_competitor_mentions_advanced(text: str, competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Extract competitor mentions with enhanced analysis."""
    results = []
    for comp in competitors:
        name = comp.get("name", "")
        if name:
            count = len(re.findall(re.escape(name), text, re.IGNORECASE))
            if count > 0:
                results.append({
                    "name": name,
                    "count": count,
                    "mention_type": detect_mention_type(text, name),
                    "position": detect_list_position(text, name)
                })
    return results

def generate_advanced_tldr_summary(
    company_name: str,
    visibility: float,
    band: str,
    platform_stats: Dict[str, PlatformStats],
    dimension_stats: Dict[str, DimensionStats],
    query_results: List[QueryResult]
) -> TLDRSummary:
    """Generate comprehensive business intelligence summary."""
    
    # Enhanced visibility assessment
    if visibility >= 80:
        visibility_assessment = f"Excellent AI search visibility ({visibility:.1f}%) - {band.lower()} market presence with consistent top recommendations"
    elif visibility >= 60:
        visibility_assessment = f"Strong AI search visibility ({visibility:.1f}%) - {band.lower()} positioning with regular mentions"
    elif visibility >= 40:
        visibility_assessment = f"Moderate AI search visibility ({visibility:.1f}%) - {band.lower()} presence but inconsistent quality"
    elif visibility >= 20:
        visibility_assessment = f"Weak AI search visibility ({visibility:.1f}%) - {band.lower()} performance requires immediate attention"
    else:
        visibility_assessment = f"Critical: Minimal AI search visibility ({visibility:.1f}%) - urgent optimization required"
    
    # Platform performance insights
    key_insights = []
    sorted_platforms = sorted(
        platform_stats.items(), 
        key=lambda x: x[1].quality_score if x[1].responses > 0 else 0, 
        reverse=True
    )
    
    if sorted_platforms:
        best_platform, best_stats = sorted_platforms[0]
        if best_stats.responses > 0:
            key_insights.append(f"Strongest performance on {best_platform} (avg quality: {best_stats.quality_score:.1f}/10)")
        
        if len(sorted_platforms) > 1:
            worst_platform, worst_stats = sorted_platforms[-1]
            if worst_stats.responses > 0 and worst_stats.quality_score < best_stats.quality_score:
                key_insights.append(f"Improvement needed on {worst_platform} (quality: {worst_stats.quality_score:.1f}/10)")
    
    # Dimension insights
    best_dimension = max(dimension_stats.items(), key=lambda x: x[1].quality_score if x[1].queries > 0 else 0)
    if best_dimension[1].queries > 0:
        key_insights.append(f"Best performing query type: {best_dimension[0]} (quality: {best_dimension[1].quality_score:.1f}/10)")
    
    # Brand confusion analysis
    brand_confusion_risk = analyze_brand_confusion_risk_advanced(company_name, query_results)
    
    # Competitive positioning
    total_mentions = sum(stats.mentions for stats in platform_stats.values())
    if total_mentions > 15:
        competitive_positioning = "Strong mention frequency suggests competitive market position"
    elif total_mentions > 5:
        competitive_positioning = "Moderate mention frequency with growth opportunities"
    else:
        competitive_positioning = "Low mention frequency indicates need for comprehensive content strategy"
    
    # Generate actionable recommendations
    actionable_recommendations = generate_advanced_recommendations(
        visibility, band, platform_stats, dimension_stats
    )
    
    return TLDRSummary(
        visibility_assessment=visibility_assessment,
        key_insights=key_insights[:4],
        brand_confusion_risk=brand_confusion_risk,
        competitive_positioning=competitive_positioning,
        actionable_recommendations=actionable_recommendations
    )

def analyze_brand_confusion_risk_advanced(company_name: str, query_results: List[QueryResult]) -> str:
    """Enhanced brand confusion analysis."""
    import difflib
    
    company_lower = company_name.lower()
    similar_names = []
    
    for result in query_results:
        response_text = result.response_text
        
        # Extract potential brand names
        potential_brands = re.findall(r'\b[A-Z][A-Za-z]*\b', response_text)
        
        for brand in potential_brands:
            brand_lower = brand.lower()
            # Enhanced filtering
            common_words = {
                'for', 'the', 'and', 'but', 'are', 'is', 'this', 'that', 'with', 'from', 'they',
                'have', 'both', 'can', 'may', 'will', 'all', 'any', 'some', 'many', 'more',
                'most', 'good', 'best', 'new', 'first', 'last', 'long', 'great', 'little',
                'own', 'other', 'old', 'right', 'big', 'high', 'different', 'small', 'large',
                'next', 'early', 'young', 'important', 'few', 'public', 'bad', 'same', 'able'
            }
            
            if (brand_lower != company_lower and 
                brand_lower not in common_words and 
                len(brand) >= 3):
                
                similarity = difflib.SequenceMatcher(None, company_lower, brand_lower).ratio()
                if similarity > 0.7:
                    similar_names.append((brand, similarity))
    
    if not similar_names:
        return "Low - clear brand recognition with minimal confusion"
    
    unique_similar = list(set([name for name, _ in similar_names]))
    if len(unique_similar) == 1:
        return f"Medium - potential confusion with '{unique_similar[0]}'"
    elif len(unique_similar) > 1:
        return f"High - confusion with multiple brands: {', '.join(unique_similar[:3])}"
    
    return "Low - clear brand recognition"

def generate_advanced_recommendations(
    visibility: float, 
    band: str, 
    platform_stats: Dict[str, PlatformStats],
    dimension_stats: Dict[str, DimensionStats]
) -> List[str]:
    """Generate sophisticated actionable recommendations."""
    recommendations = []
    
    # Visibility-based recommendations
    if visibility < 20:
        recommendations.append("URGENT: Implement comprehensive AEO content strategy - current visibility is critical")
        recommendations.append("Priority 1: Create targeted content for AI platforms with structured data markup")
    elif visibility < 40:
        recommendations.append("Important: Develop AI-optimized content focusing on your core value propositions")
        recommendations.append("Focus on: Answer-style content that directly addresses customer questions")
    elif visibility < 60:
        recommendations.append("Optimize: Enhance existing content with AI-friendly formatting and depth")
        recommendations.append("Target: Increase mention quality through thought leadership content")
    elif visibility < 80:
        recommendations.append("Refine: Fine-tune content positioning for premium recommendation status")
        recommendations.append("Advance: Expand topical authority in your core expertise areas")
    else:
        recommendations.append("Maintain: Continue excellent AEO performance with consistent content quality")
        recommendations.append("Scale: Expand into adjacent market segments and use cases")
    
    # Platform-specific recommendations
    worst_platform = min(
        platform_stats.items(), 
        key=lambda x: x[1].quality_score if x[1].responses > 0 else -1
    )
    if worst_platform[1].responses > 0 and worst_platform[1].quality_score < 3:
        recommendations.append(f"Platform focus: Improve {worst_platform[0]} visibility through platform-specific optimization")
    
    return recommendations[:6]  # Limit to top 6 recommendations

# ==================== Master Combined Analysis ====================

@app.post("/analyze/master", response_model=MasterAnalysisResponse)
async def master_analysis(request: MasterAnalysisRequest):
    """
    Master AEO Analysis - Complete Health + Mentions Intelligence
    
    Combines advanced health check with sophisticated mentions analysis:
    1. Health Check: v4.0 tiered scoring with 29 checks
    2. Mentions Check: Hyperniche targeting with quality scoring
    3. Combined Intelligence: Integrated recommendations and priority actions
    
    Returns comprehensive analysis with strategic insights.
    """
    start_time = time.time()
    logger.info(f"Starting master analysis for: {request.url} ({request.companyName})")
    
    try:
        # Run health check
        health_request = HealthCheckRequest(
            url=request.url,
            include_performance=request.include_performance,
            include_accessibility=request.include_accessibility
        )
        health_result = await health_check(health_request)
        
        # Run mentions check (if company analysis provided)
        mentions_result = None
        if request.companyAnalysis:
            mentions_request = MentionsCheckRequest(
                companyName=request.companyName,
                companyAnalysis=request.companyAnalysis,
                language=request.language,
                country=request.country,
                numQueries=request.numQueries,
                mode=request.mode,
                generateInsights=request.generateInsights,
                platforms=request.platforms
            )
            mentions_result = await mentions_check_advanced(mentions_request)
        else:
            # Create minimal mentions result if no company analysis
            mentions_result = MentionsCheckResponse(
                companyName=request.companyName,
                visibility=0.0,
                band="Unknown",
                mentions=0,
                presence_rate=0.0,
                quality_score=0.0,
                max_quality=0.0,
                platform_stats={},
                dimension_stats={},
                query_results=[],
                actualQueriesProcessed=0,
                execution_time_seconds=0.0,
                total_cost=0.0,
                total_tokens=0,
                mode=request.mode,
                tldr=TLDRSummary(
                    visibility_assessment="Unable to assess - no company analysis provided",
                    key_insights=["Company analysis required for mentions check"],
                    brand_confusion_risk="Unknown",
                    competitive_positioning="Unable to determine",
                    actionable_recommendations=["Provide company analysis for complete assessment"]
                )
            )
        
        # Calculate combined metrics
        combined_score, combined_grade = calculate_combined_score(
            health_result.overall_score, 
            mentions_result.visibility if mentions_result else 0
        )
        
        # Generate strategic recommendations
        strategic_recommendations = generate_strategic_recommendations(
            health_result, mentions_result
        )
        
        # Generate priority actions
        priority_actions = generate_priority_actions(
            health_result, mentions_result, combined_score
        )
        
        # Add health integration to mentions TL;DR
        if mentions_result and mentions_result.tldr:
            mentions_result.tldr.health_integration = f"Health score: {health_result.overall_score:.1f}/100 ({health_result.grade}) - affects AI platform accessibility"
        
        execution_time = time.time() - start_time
        
        logger.info(f"Master analysis complete in {execution_time:.2f}s: Combined score {combined_score:.1f} ({combined_grade})")
        
        return MasterAnalysisResponse(
            url=request.url,
            companyName=request.companyName,
            health=health_result,
            mentions=mentions_result,
            combined_score=combined_score,
            combined_grade=combined_grade,
            strategic_recommendations=strategic_recommendations,
            priority_actions=priority_actions,
            execution_time_seconds=round(execution_time, 2)
        )
        
    except Exception as e:
        logger.error(f"Master analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Master analysis failed: {str(e)}")

def calculate_combined_score(health_score: float, visibility_score: float) -> tuple[float, str]:
    """Calculate weighted combined score from health and visibility."""
    # Weight: 60% health (foundation), 40% visibility (performance)
    combined = (health_score * 0.6) + (visibility_score * 0.4)
    
    # Determine combined grade
    if combined >= 90:
        grade = "A+"
    elif combined >= 80:
        grade = "A"
    elif combined >= 70:
        grade = "B"
    elif combined >= 60:
        grade = "C"
    elif combined >= 50:
        grade = "D"
    else:
        grade = "F"
    
    return round(combined, 1), grade

def generate_strategic_recommendations(
    health_result: HealthCheckResponse, 
    mentions_result: MentionsCheckResponse
) -> List[str]:
    """Generate high-level strategic recommendations."""
    recommendations = []
    
    # Foundation vs Performance analysis
    if health_result.overall_score < 45:
        recommendations.append("STRATEGIC PRIORITY: Fix foundational issues before visibility optimization")
        recommendations.append("Foundation First: AI platforms cannot properly access or understand your website")
    elif health_result.overall_score < 75 and mentions_result.visibility > 40:
        recommendations.append("OPTIMIZATION OPPORTUNITY: Strong visibility despite technical issues - fix foundation for exponential gains")
    elif health_result.overall_score > 75 and mentions_result.visibility < 30:
        recommendations.append("CONTENT STRATEGY: Excellent foundation but low visibility - focus on AI-optimized content creation")
    else:
        recommendations.append("BALANCED APPROACH: Continue optimizing both technical foundation and content strategy")
    
    # Integration recommendations
    if health_result.visibility_band == "Weak" and mentions_result.band in ["Weak", "Minimal"]:
        recommendations.append("COMPREHENSIVE AEO: Implement full AEO strategy covering technical, content, and distribution")
    elif health_result.grade in ["A", "A+"] and mentions_result.band in ["Strong", "Dominant"]:
        recommendations.append("MARKET LEADERSHIP: Maintain excellence and expand into adjacent markets")
    
    return recommendations[:4]

def generate_priority_actions(
    health_result: HealthCheckResponse,
    mentions_result: MentionsCheckResponse,
    combined_score: float
) -> List[str]:
    """Generate specific priority actions based on combined analysis."""
    actions = []
    
    # Critical issues (combined score < 50)
    if combined_score < 50:
        if health_result.overall_score < 25:
            actions.append("IMMEDIATE: Remove robots.txt blocks for AI crawlers")
        if health_result.overall_score < 45:
            actions.append("URGENT: Implement Organization schema markup")
        if mentions_result.visibility < 10:
            actions.append("CRITICAL: Create basic answer-style content for core queries")
    
    # Growth opportunities (combined score 50-75)
    elif 50 <= combined_score < 75:
        actions.append("OPTIMIZE: Complete schema implementation for all key pages")
        actions.append("CONTENT: Develop AI-optimized FAQ and how-to content")
        if mentions_result.visibility < 40:
            actions.append("TARGETING: Focus content on identified weak dimensions")
    
    # Excellence initiatives (combined score 75+)
    else:
        actions.append("SCALE: Expand content to cover long-tail query variations")
        actions.append("AUTHORITY: Develop thought leadership content for expertise")
        if mentions_result.visibility < 80:
            actions.append("QUALITY: Improve mention quality through strategic content positioning")
    
    # Platform-specific actions
    if mentions_result.platform_stats:
        worst_platforms = [
            name for name, stats in mentions_result.platform_stats.items()
            if stats.responses > 0 and stats.quality_score < 3
        ]
        if worst_platforms:
            actions.append(f"PLATFORM: Create {worst_platforms[0]}-optimized content")
    
    return actions[:5]

# ==================== Service Health and Info Endpoints ====================

@app.get("/")
async def root():
    """Service directory and information."""
    return {
        "service": "master-aeo-service",
        "version": "5.0.0",
        "description": "Advanced AEO Analysis Platform combining health checks and mentions analytics",
        "features": [
            "Health Check: v4.0 tiered scoring (29 checks across 4 categories)",
            "Mentions Check: Hyperniche targeting with Gemini 2.5 Flash",
            "Quality Scoring: Advanced mention quality detection",
            "Business Intelligence: Brand confusion and competitive analysis",
            "Master Analysis: Combined health + mentions with strategic insights"
        ],
        "endpoints": {
            "/health/check": "POST - Advanced health check with tiered scoring",
            "/mentions/check": "POST - Sophisticated mentions analysis with business intelligence",
            "/analyze/master": "POST - Complete analysis combining health + mentions",
            "/health": "GET - Service health status",
            "/status": "GET - Detailed service status"
        },
        "platforms": list(AI_PLATFORMS.keys()),
        "modes": {
            "fast": "10 queries, Gemini + ChatGPT only",
            "balanced": "25 queries, 4 platforms (recommended)",
            "full": "50 queries, all 5 platforms"
        }
    }

@app.get("/health")
async def service_health():
    """Service health check."""
    return {
        "status": "healthy",
        "service": "master-aeo-service",
        "version": "5.0.0",
        "components": {
            "health_check": "operational",
            "mentions_check": "operational", 
            "ai_platforms": "operational",
            "master_analysis": "operational"
        },
        "ai_platforms": {
            platform: {"model": config["model"], "status": "available"}
            for platform, config in AI_PLATFORMS.items()
        }
    }

@app.get("/status")  
async def detailed_status():
    """Detailed service status with configuration."""
    return {
        "service": "master-aeo-service",
        "version": "5.0.0",
        "status": "healthy",
        "features": {
            "health_check": {
                "version": "4.0",
                "checks": 29,
                "categories": 4,
                "scoring": "tiered_objective"
            },
            "mentions_check": {
                "version": "5.0",
                "platforms": len(AI_PLATFORMS),
                "query_generation": "ai_assisted_hyperniche",
                "scoring": "quality_adjusted_with_position"
            },
            "master_analysis": {
                "version": "1.0",
                "combines": ["health", "mentions"],
                "intelligence": "strategic_recommendations"
            }
        },
        "ai_platforms": {
            platform: {
                "model": config["model"],
                "has_search": config["has_search"],
                "provider": config.get("provider", "openrouter"),
                "cost_per_token": config["cost_per_token"]
            }
            for platform, config in AI_PLATFORMS.items()
        },
        "health_categories": [
            "Technical SEO (16 checks)",
            "Structured Data (6 checks)",
            "AI Crawler Access (4 checks)", 
            "Authority/E-E-A-T (3 checks)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)