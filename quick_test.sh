#!/bin/bash
# Quick test script - starts services and runs test

set -e

echo "🚀 OpenAnalytics Quick Test"
echo "=========================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get URL from argument or use default
URL=${1:-"https://example.com"}
COMPANY_NAME=${2:-""}

echo "📋 Test Configuration:"
echo "   URL: $URL"
if [ -n "$COMPANY_NAME" ]; then
    echo "   Company: $COMPANY_NAME"
fi
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is required${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Check if services are already running
AEO_RUNNING=false
PDF_RUNNING=false

if check_port 8000; then
    echo -e "${GREEN}✅ AEO Checks service is already running on port 8000${NC}"
    AEO_RUNNING=true
else
    echo -e "${YELLOW}⚠️  AEO Checks service is not running${NC}"
fi

if check_port 8001; then
    echo -e "${GREEN}✅ PDF service is already running on port 8001${NC}"
    PDF_RUNNING=true
else
    echo -e "${YELLOW}⚠️  PDF service is not running (PDF generation will be skipped)${NC}"
fi

echo ""

# If services aren't running, provide instructions
if [ "$AEO_RUNNING" = false ]; then
    echo "To start the AEO Checks service, run in a separate terminal:"
    echo ""
    echo "  cd aeo-checks"
    echo "  source venv/bin/activate"
    echo "  uvicorn main:app --reload --port 8000"
    echo ""
    echo "Then run this script again."
    echo ""
    exit 1
fi

# Set environment variables
export AEO_CHECKS_URL=http://localhost:8000
if [ "$PDF_RUNNING" = true ]; then
    export PDF_SERVICE_URL=http://localhost:8001
fi

# Run the test
echo "🧪 Running test..."
echo ""

cd "$(dirname "$0")"
python3 test_local.py "$URL" "$COMPANY_NAME"

