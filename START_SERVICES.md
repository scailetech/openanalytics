# Starting Services for Local Testing

## Quick Start

### Terminal 1: Start AEO Checks Service

```bash
cd aeo-checks
source venv/bin/activate  # or: venv\Scripts\activate on Windows
uvicorn main:app --reload --port 8000
```

Wait for: `Application startup complete`

### Terminal 2: Start PDF Service (Optional)

```bash
cd pdf-service
source venv/bin/activate
uvicorn pdf_service:app --reload --port 8001
```

Wait for: `Application startup complete`

### Terminal 3: Run Test

```bash
cd openanalytics
python3 test_local.py https://example.com
```

Or use the quick test script:

```bash
./quick_test.sh https://example.com
```

## Verify Services Are Running

```bash
# Check AEO Checks
curl http://localhost:8000/status

# Check PDF Service
curl http://localhost:8001/health
```

## Troubleshooting

### Port Already in Use

If port 8000 or 8001 is already in use:

```bash
# Find what's using the port
lsof -i :8000
lsof -i :8001

# Kill the process or use different ports
export AEO_CHECKS_URL=http://localhost:8002
export PDF_SERVICE_URL=http://localhost:8003
```

### Missing Dependencies

```bash
cd aeo-checks
source venv/bin/activate
pip install -r requirements.txt httpx aiohttp

cd ../pdf-service
source venv/bin/activate
pip install fastapi uvicorn pydantic playwright httpx
playwright install chromium
```

### Import Errors

Make sure you're running from the `openanalytics` root directory:

```bash
cd /path/to/openanalytics
python3 test_local.py https://example.com
```
