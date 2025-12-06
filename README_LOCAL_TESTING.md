# Local Testing Guide

## Quick Start

### Option 1: Automated Test Script

```bash
# Make script executable (first time only)
chmod +x run_local.sh

# Run test (will check if services are running)
./run_local.sh https://example.com
```

### Option 2: Manual Testing

#### 1. Start AEO Checks Service

```bash
cd aeo-checks

# Create virtual environment (first time)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install httpx aiohttp

# Start service
uvicorn main:app --reload --port 8000
```

#### 2. Start PDF Service (in another terminal)

```bash
cd pdf-service

# Create virtual environment (first time)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn pydantic playwright httpx

# Install Playwright browser
playwright install chromium

# Start service
uvicorn pdf_service:app --reload --port 8001
```

#### 3. Run Test

```bash
# Set environment variables
export AEO_CHECKS_URL=http://localhost:8000
export PDF_SERVICE_URL=http://localhost:8001

# Run test
python test_local.py https://example.com
```

## Test Script Usage

```bash
python test_local.py <URL> [company_name]

# Examples:
python test_local.py https://example.com
python test_local.py https://scaile.tech "SCAILE Technologies"
```

## Environment Variables

- `AEO_CHECKS_URL` - AEO Checks service URL (default: http://localhost:8000)
- `PDF_SERVICE_URL` - PDF service URL (default: http://localhost:8001)

## Expected Output

The test script will:
1. ✅ Check if services are running
2. ⏳ Run complete analysis
3. 📊 Display results summary
4. 💾 Save files:
   - `test_report.html` - HTML report
   - `test_report.pdf` - PDF report (if PDF service available)
   - `test_report_data.json` - Full JSON data

## Troubleshooting

### Services Not Running

If you see "Services are not running", make sure:
1. Both services are started (see steps above)
2. Ports 8000 and 8001 are not in use by other applications
3. Virtual environments are activated

### Import Errors

If you see import errors:
```bash
# Make sure you're in the openanalytics directory
cd /path/to/openanalytics

# Install all dependencies
pip install -r aeo-checks/requirements.txt
pip install httpx aiohttp
```

### PDF Generation Fails

PDF generation requires:
- PDF service running on port 8001
- Playwright with Chromium installed
- Sufficient memory (Chromium needs ~500MB)

If PDF service is not available, the test will still run but skip PDF generation.

## Testing Individual Endpoints

You can also test individual endpoints:

```bash
# Health check
curl http://localhost:8000/status

# Company analysis
curl -X POST http://localhost:8000/company/analyze \
  -H "Content-Type: application/json" \
  -d '{"website_url": "https://example.com", "company_name": "Example"}'

# Health check
curl -X POST http://localhost:8000/health/check \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

## Complete Analysis Endpoint

Test the unified endpoint:

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "company_name": "Example Inc",
    "mentions_mode": "fast",
    "theme": "dark",
    "pdf_service_url": "http://localhost:8001"
  }'
```

