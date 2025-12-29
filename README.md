# OpenAnalytics

Clean, production-ready AEO analysis API.

## Services

1. **Health Check** - 29 AEO checks with tiered scoring
2. **Mentions Check** - AI-powered hyperniche query generation

## Quick Start

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Set API key
export GEMINI_API_KEY=your_key_here

# Run
python app.py
```

Server runs at: `http://localhost:8000`

### Docker

```bash
docker build -t openanalytics .
docker run -p 8000:8000 -e GEMINI_API_KEY=your_key openanalytics
```

### Railway

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway link
railway up
```

Set environment variable in Railway dashboard:
- `GEMINI_API_KEY`: Your Gemini API key

## API Usage

### Health Check

```bash
curl -X POST http://localhost:8000/health \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Response:
```json
{
  "url": "https://example.com",
  "score": 45.0,
  "max_score": 100.0,
  "grade": "C",
  "band": "Moderate",
  "checks_passed": 18,
  "checks_failed": 11,
  "issues": [...],
  "execution_time": 0.56
}
```

### Mentions Check

```bash
curl -X POST http://localhost:8000/mentions \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "SCAILE",
    "industry": "AI Marketing",
    "products": ["AEO Platform", "Health Check"],
    "target_audience": "B2B SaaS companies",
    "num_queries": 10
  }'
```

Response:
```json
{
  "company_name": "SCAILE",
  "queries_generated": [
    {
      "query": "best AEO platform for B2B SaaS companies United States",
      "dimension": "UNBRANDED_HYPERNICHE"
    },
    ...
  ],
  "visibility": 75.0,
  "mentions": 8,
  "presence_rate": 80.0,
  "quality_score": 6.5,
  "execution_time": 45.2
}
```

## Query Generation

The mentions check uses AI to generate sophisticated queries:

**70% Unbranded** - Tests organic visibility
- "best AEO platform for B2B SaaS companies"
- "answer engine optimization for marketing teams"

**20% Competitive** - Competitive analysis
- "SCAILE alternatives for enterprise"
- "leading AEO platforms vs SCAILE"

**10% Branded** - Brand awareness
- "SCAILE AEO platform"

This tests **real organic discovery**, not just brand awareness.

## File Structure

```
openanalytics/
├── app.py                 # Main API (310 lines)
├── fetcher.py             # Website fetcher
├── gemini_client.py       # AI client
├── scoring.py             # Scoring logic
├── checks/                # Health check modules
│   ├── technical.py
│   ├── structured_data.py
│   ├── aeo_crawler.py
│   └── authority.py
├── requirements.txt       # Dependencies
├── Dockerfile             # Docker config
├── Procfile               # Railway/Heroku
└── README.md              # This file
```

**Total:** 8 files, ~1,500 lines of actual code

## Environment Variables

- `GEMINI_API_KEY` (required) - Your Gemini API key
- `PORT` (optional) - Server port (default: 8000)

## Deployment

### Railway (Recommended)

1. Push to GitHub
2. Connect Railway to your repo
3. Set `GEMINI_API_KEY` in environment variables
4. Deploy automatically

### Render

```yaml
# render.yaml
services:
  - type: web
    name: openanalytics
    env: docker
    envVars:
      - key: GEMINI_API_KEY
        sync: false
```

### Fly.io

```bash
fly launch
fly secrets set GEMINI_API_KEY=your_key
fly deploy
```

## Performance

- Health Check: ~0.5s
- Query Generation: ~2s (AI)
- Mentions Check: ~30-60s (10 queries)

## License

MIT
