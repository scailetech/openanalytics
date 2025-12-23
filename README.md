# AEO Services - Unified API Gateway

All AEO (Answer Engine Optimization) services in one Modal app.

## Services

### 1. Company Analysis (`/company/*`)
- Two-phase analysis (website-first, then search)
- Logo detection via GPT-4o-mini vision
- Tech stack detection (CMS, frameworks, analytics)
- Brand assets extraction (colors, fonts)

### 2. Health Check (`/health/*`) - v4.0
- **29 checks** across 4 categories:
  - Technical SEO (16 checks)
  - Structured Data (6 checks)
  - AI Crawler Access (4 checks)
  - Authority/E-E-A-T (3 checks)
- **Tiered Objective Scoring**:
  - Tier 0: AI Access Gate (blocks all AI → max 10)
  - Tier 1: Schema Gate (no Organization → max 45)
  - Tier 2: Quality Gate (incomplete → max 75-85)
  - Tier 3: Base performance (up to 100)
- Playwright JS rendering for SPAs
- Cloudflare challenge detection

### 3. Mentions Check (`/mentions/*`)
- Queries 4 AI platforms via OpenRouter + DataForSEO SERP:
  - Perplexity (sonar-pro) - native search
  - Claude (claude-3.5-sonnet) - google_search tool → DataForSEO
  - ChatGPT (openai/gpt-4o) - google_search tool → DataForSEO
  - Gemini (gemini-3-pro-preview) - google_search tool → DataForSEO
- Quality-adjusted scoring with mention capping
- Fast mode (10 queries) vs Full mode (50 queries)

## Deployment

```bash
cd services/aeo-checks
modal profile activate clients
modal deploy modal_deploy.py
```

## Endpoints

**Base URL:** `https://clients--aeo-checks-fastapi-app.modal.run`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/status` | GET | Gateway health with service status |
| `/company/analyze` | POST | Full company analysis |
| `/company/crawl-logo` | POST | Standalone logo detection |
| `/company/health` | GET | Company service health |
| `/health/check` | POST | Website health check |
| `/health/health` | GET | Health check service status |
| `/mentions/check` | POST | AEO mentions check |
| `/mentions/health` | GET | Mentions service status |

## Health Check Scoring (v4.0)

The health check uses **tiered objective scoring** based on AEO reality:

| Grade | Range | Meaning |
|-------|-------|---------|
| A+ | 90+ | Excellent - passes all tiers |
| A | 80-89 | Good optimization |
| B | 65-79 | Has schema, needs work |
| C | 45-64 | No schema - AI can't identify |
| D | 25-44 | Partial AI access |
| F | <25 | Blocks AI crawlers |

**Key principle**: If AI can't access your site, nothing else matters.

## Required Secrets (Modal)

- `openai-secret` - For logo detection (GPT-4o-mini)

Note: AI calls for company analysis and mentions check go through 
`scaile-services` OpenRouter gateway (no direct API keys needed).

## Usage Examples

### Health Check
```bash
curl -X POST https://clients--aeo-checks-fastapi-app.modal.run/health/check \
  -H "Content-Type: application/json" \
  -d '{"url": "https://scaile.tech"}'
```

### Company Analysis
```bash
curl -X POST https://clients--aeo-checks-fastapi-app.modal.run/company/analyze \
  -H "Content-Type: application/json" \
  -d '{"website_url": "https://scaile.tech", "company_name": "SCAILE"}'
```

### Mentions Check (Fast Mode)
```bash
curl -X POST https://clients--aeo-checks-fastapi-app.modal.run/mentions/check \
  -H "Content-Type: application/json" \
  -d '{"companyName": "SCAILE", "mode": "fast"}'
```
