#!/bin/bash
# Local development script for OpenAnalytics

set -e

echo "🚀 Starting OpenAnalytics services locally..."
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r aeo-checks/requirements.txt
pip install -q httpx aiohttp

# Check if services are running
AEO_CHECKS_URL=${AEO_CHECKS_URL:-http://localhost:8000}
PDF_SERVICE_URL=${PDF_SERVICE_URL:-http://localhost:8001}

echo ""
echo "📡 Service URLs:"
echo "   AEO Checks: $AEO_CHECKS_URL"
echo "   PDF Service: $PDF_SERVICE_URL"
echo ""

# Function to check if a service is running
check_service() {
    local url=$1
    local name=$2
    
    if curl -s "$url/status" > /dev/null 2>&1 || curl -s "$url/health" > /dev/null 2>&1; then
        echo "✅ $name is running at $url"
        return 0
    else
        echo "⚠️  $name is not running at $url"
        return 1
    fi
}

# Check services
AEO_RUNNING=false
PDF_RUNNING=false

if check_service "$AEO_CHECKS_URL" "AEO Checks Service"; then
    AEO_RUNNING=true
fi

if check_service "$PDF_SERVICE_URL" "PDF Service"; then
    PDF_RUNNING=true
fi

echo ""
if [ "$AEO_RUNNING" = true ] && [ "$PDF_RUNNING" = true ]; then
    echo "✅ Both services are running!"
    echo ""
    echo "🧪 Running test..."
    python test_local.py "${1:-https://example.com}"
elif [ "$AEO_RUNNING" = true ]; then
    echo "⚠️  AEO Checks is running, but PDF Service is not."
    echo "   PDF generation will be skipped."
    echo ""
    echo "🧪 Running test (without PDF)..."
    python test_local.py "${1:-https://example.com}"
else
    echo "❌ Services are not running."
    echo ""
    echo "To start the services:"
    echo ""
    echo "1. Start AEO Checks Service:"
    echo "   cd aeo-checks"
    echo "   uvicorn main:app --reload --port 8000"
    echo ""
    echo "2. Start PDF Service (in another terminal):"
    echo "   cd pdf-service"
    echo "   uvicorn pdf_service:app --reload --port 8001"
    echo ""
    echo "3. Then run this script again:"
    echo "   ./run_local.sh https://example.com"
    exit 1
fi

