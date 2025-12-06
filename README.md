# OpenAnalytics

A comprehensive Answer Engine Optimization (AEO) analysis platform. Analyze company websites, check AI visibility, generate health scores, and create professional reports.

## 🎯 Features

### 1. **Company Analysis** (`/company/*`)
- Two-phase analysis (website-first, then search)
- Logo detection via GPT-4o-mini vision
- Tech stack detection (CMS, frameworks, analytics)
- Brand assets extraction (colors, fonts)
- Competitor identification

### 2. **Health Check** (`/health/*`) - v4.0
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

### 3. **Mentions Check** (`/mentions/*`)
- Queries 4 AI platforms via OpenRouter + DataForSEO SERP:
  - Perplexity (sonar-pro) - native search
  - Claude (claude-3.5-sonnet) - google_search tool → DataForSEO
  - ChatGPT (openai/gpt-4o) - google_search tool → DataForSEO
  - Gemini (gemini-3-pro-preview) - google_search tool → DataForSEO
- Quality-adjusted scoring with mention capping
- Fast mode (10 queries) vs Full mode (50 queries)

### 4. **Report Generation**
- HTML report generation from analysis data
- PDF conversion with pixel-perfect rendering
- Dark/light theme support
- Professional design with insights and recommendations

## 📁 Repository Structure

```
openanalytics/
├── aeo-checks/          # Main AEO analysis service (Python/FastAPI)
│   ├── main.py         # Unified API gateway
│   ├── company_service.py
│   ├── health_service.py
│   ├── mentions_service.py
│   └── modal_deploy.py
├── pdf-service/         # PDF generation service (Python/FastAPI)
│   ├── pdf_service.py
│   └── modal_deploy.py
├── reports/            # Report generation utilities
│   └── html_generator.py  # HTML report builder
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- [Modal](https://modal.com) account
- API keys:
  - OpenAI API key (for logo detection)
  - OpenRouter API key (for AI calls)
  - DataForSEO credentials (for SERP data)

### 1. Deploy AEO Checks Service

```bash
cd aeo-checks
modal profile activate YOUR_WORKSPACE

# Set up secrets
modal secret create openai-api-key OPENAI_API_KEY=your_key_here
modal secret create openrouter-api-key OPENROUTER_API_KEY=your_key_here
modal secret create serp-credentials \
  DATAFORSEO_LOGIN=your_login \
  DATAFORSEO_PASSWORD=your_password

# Deploy
modal deploy modal_deploy.py
```

### 2. Deploy PDF Service

```bash
cd pdf-service
modal profile activate YOUR_WORKSPACE
modal deploy modal_deploy.py
```

### 3. Test the Services

#### Complete Analysis (Recommended - One Endpoint for Everything)

```bash
# Complete analysis: URL → all checks → HTML + PDF reports
curl -X POST https://YOUR_WORKSPACE--aeo-checks-fastapi-app.modal.run/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "company_name": "Example Inc",
    "mentions_mode": "fast",
    "theme": "dark",
    "pdf_service_url": "https://YOUR_WORKSPACE--pdf-service-fastapi-app.modal.run"
  }'
```

This returns:
- `company_analysis` - Full company analysis JSON
- `health_check` - Health check results JSON
- `mentions_check` - Mentions check results JSON
- `html_report` - Complete HTML report
- `pdf_base64` - PDF report (base64 encoded)
- `pdf_size_bytes` - PDF file size

#### Individual Endpoints

```bash
# Health check
curl https://YOUR_WORKSPACE--aeo-checks-fastapi-app.modal.run/status

# Company analysis
curl -X POST https://YOUR_WORKSPACE--aeo-checks-fastapi-app.modal.run/company/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "website_url": "https://example.com",
    "company_name": "Example Inc"
  }'

# Health check
curl -X POST https://YOUR_WORKSPACE--aeo-checks-fastapi-app.modal.run/health/check \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Mentions check
curl -X POST https://YOUR_WORKSPACE--aeo-checks-fastapi-app.modal.run/mentions/check \
  -H "Content-Type: application/json" \
  -d '{
    "companyName": "Example Inc",
    "companyAnalysis": {
      "companyInfo": {
        "products": ["Product A", "Product B"],
        "industry": "Technology"
      }
    },
    "mode": "fast"
  }'
```

## 📊 API Endpoints

### AEO Checks Service

**Base URL:** `https://YOUR_WORKSPACE--aeo-checks-fastapi-app.modal.run`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | **Complete analysis**: URL → all checks → HTML + PDF reports |
| `/status` | GET | Gateway health with service status |
| `/company/analyze` | POST | Full company analysis |
| `/company/crawl-logo` | POST | Standalone logo detection |
| `/company/health` | GET | Company service health |
| `/health/check` | POST | Website health check |
| `/health/health` | GET | Health check service status |
| `/mentions/check` | POST | AEO mentions check |
| `/mentions/health` | GET | Mentions service status |

### PDF Service

**Base URL:** `https://YOUR_WORKSPACE--pdf-service-fastapi-app.modal.run`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/convert` | POST | Convert HTML string to PDF |
| `/convert/url` | POST | Convert URL to PDF |

## 📈 Health Check Scoring (v4.0)

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

## 🔧 Configuration

### Modal Secrets

Required secrets for `aeo-checks`:
- `openai-api-key` - For logo detection (GPT-4o-mini)
- `openrouter-api-key` - For AI calls (company analysis, mentions)
- `serp-credentials` - DataForSEO credentials:
  - `DATAFORSEO_LOGIN`
  - `DATAFORSEO_PASSWORD`

### Environment Variables

For local development:
```bash
export OPENAI_API_KEY=your_key
export OPENROUTER_API_KEY=your_key
export DATAFORSEO_LOGIN=your_login
export DATAFORSEO_PASSWORD=your_password
```

## 📝 Usage Examples

### Complete Analysis Workflow (Simplified)

The `/analyze` endpoint does everything in one call:

```python
import requests
import base64

BASE_URL = "https://YOUR_WORKSPACE--aeo-checks-fastapi-app.modal.run"
PDF_SERVICE_URL = "https://YOUR_WORKSPACE--pdf-service-fastapi-app.modal.run"

# Single API call - runs everything
response = requests.post(
    f"{BASE_URL}/analyze",
    json={
        "url": "https://example.com",
        "company_name": "Example Inc",  # Optional, will be extracted from URL
        "mentions_mode": "fast",  # or "full" for 50 queries
        "theme": "dark",  # or "light"
        "pdf_service_url": PDF_SERVICE_URL
    }
)

result = response.json()

# Access all data
company_data = result["company_analysis"]
health_data = result["health_check"]
mentions_data = result["mentions_check"]
html_report = result["html_report"]
pdf_base64 = result.get("pdf_base64")

# Save HTML report
with open("report.html", "w") as f:
    f.write(html_report)

# Save PDF report
if pdf_base64:
    pdf_bytes = base64.b64decode(pdf_base64)
    with open("report.pdf", "wb") as f:
        f.write(pdf_bytes)

print(f"Analysis complete in {result['analysis_time_seconds']:.1f}s")
print(f"Health Score: {health_data.get('score', 'N/A')}")
print(f"Visibility: {mentions_data.get('visibility', 'N/A')}%")
```

### Individual Endpoints Workflow (Advanced)

If you need more control, use individual endpoints:

```python
import requests

BASE_URL = "https://YOUR_WORKSPACE--aeo-checks-fastapi-app.modal.run"

# 1. Company Analysis
company_response = requests.post(
    f"{BASE_URL}/company/analyze",
    json={
        "website_url": "https://example.com",
        "company_name": "Example Inc"
    }
)
company_data = company_response.json()

# 2. Health Check
health_response = requests.post(
    f"{BASE_URL}/health/check",
    json={"url": "https://example.com"}
)
health_data = health_response.json()

# 3. Mentions Check
mentions_response = requests.post(
    f"{BASE_URL}/mentions/check",
    json={
        "companyName": "Example Inc",
        "companyAnalysis": company_data,
        "mode": "fast"
    }
)
mentions_data = mentions_response.json()

# 4. Generate Report (using reports/html_generator.py)
from reports.html_generator import generate_report_html

html_report = generate_report_html(
    company_data=company_data,
    health_data=health_data,
    mentions_data=mentions_data,
    client_name="Example Inc",
    website_url="https://example.com"
)

# 5. Convert to PDF
pdf_response = requests.post(
    "https://YOUR_WORKSPACE--pdf-service-fastapi-app.modal.run/convert",
    json={
        "html": html_report,
        "format": "A4",
        "print_background": True,
        "color_scheme": "dark"
    }
)

# Save PDF
import base64
pdf_bytes = base64.b64decode(pdf_response.json()["pdf_base64"])
with open("report.pdf", "wb") as f:
    f.write(pdf_bytes)
```

## 🏗️ Architecture

### Service Architecture

```
┌─────────────────┐
│   AEO Checks    │  ← Company Analysis, Health, Mentions
│   (FastAPI)     │
└────────┬────────┘
         │
         ├──→ Company Analysis (Gemini + GPT-4o-mini)
         ├──→ Health Check (29 checks, Playwright)
         └──→ Mentions Check (OpenRouter + DataForSEO)
         
┌─────────────────┐
│  PDF Service    │  ← HTML to PDF conversion
│  (FastAPI)      │
└─────────────────┘
         │
         └──→ Playwright/Chromium rendering
```

### Data Flow

1. **Company Analysis** → Extracts company info, logo, tech stack
2. **Health Check** → Runs 29 checks, calculates tiered score
3. **Mentions Check** → Queries AI platforms, calculates visibility
4. **Report Generation** → Combines all data into HTML report
5. **PDF Conversion** → Converts HTML to PDF with Playwright

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built with [Modal](https://modal.com) for serverless deployment
- Uses [Playwright](https://playwright.dev) for browser automation
- Powered by [OpenRouter](https://openrouter.ai) for AI model access
- SERP data via [DataForSEO](https://dataforseo.com)

## 📞 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Made with ❤️ for the AEO community**

