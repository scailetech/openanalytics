"""
Local test script for complete AEO analysis endpoint.

Usage:
    python test_local.py https://example.com

Or set environment variables:
    export AEO_CHECKS_URL=http://localhost:8000
    export PDF_SERVICE_URL=http://localhost:8001
    python test_local.py https://example.com
"""

import sys
import os
import asyncio
import json
import base64
from pathlib import Path

# Add aeo-checks to path
sys.path.insert(0, str(Path(__file__).parent / "aeo-checks"))
sys.path.insert(0, str(Path(__file__).parent))

import httpx
from complete_analysis import CompleteAnalysisRequest, run_complete_analysis


async def test_complete_analysis(url: str, company_name: str = None):
    """Test the complete analysis endpoint locally."""
    
    # Get service URLs from environment or use defaults
    base_url = os.getenv("AEO_CHECKS_URL", "http://localhost:8000")
    pdf_service_url = os.getenv("PDF_SERVICE_URL", "http://localhost:8001")
    
    print(f"🔍 Testing complete AEO analysis for: {url}")
    print(f"📡 AEO Checks Service: {base_url}")
    print(f"📄 PDF Service: {pdf_service_url}")
    print()
    
    # Create request
    request = CompleteAnalysisRequest(
        url=url,
        company_name=company_name,
        mentions_mode="fast",  # Use fast mode for testing
        theme="dark",
        pdf_service_url=pdf_service_url if pdf_service_url != "http://localhost:8001" else None,
    )
    
    try:
        # Run complete analysis
        print("⏳ Running complete analysis...")
        result = await run_complete_analysis(request, base_url, pdf_service_url)
        
        print(f"\n✅ Analysis complete in {result.analysis_time_seconds:.1f} seconds")
        print(f"   Success: {result.success}")
        
        if result.errors:
            print(f"\n⚠️  Errors encountered:")
            for error in result.errors:
                print(f"   - {error}")
        
        # Print summary
        print("\n📊 Results Summary:")
        print(f"   Company Name: {result.company_name}")
        
        if result.company_analysis and not result.company_analysis.get("error"):
            company_info = result.company_analysis.get("companyInfo", {})
            print(f"   Industry: {company_info.get('industry', 'N/A')}")
            print(f"   Products: {len(company_info.get('products', []))}")
            print(f"   Services: {len(company_info.get('services', []))}")
        else:
            print(f"   Company Analysis: {'Error' if result.company_analysis else 'Not run'}")
        
        if result.health_check and not result.health_check.get("error"):
            print(f"   Health Score: {result.health_check.get('score', 'N/A')}")
            print(f"   Grade: {result.health_check.get('grade', 'N/A')}")
        else:
            print(f"   Health Check: {'Error' if result.health_check else 'Not run'}")
        
        if result.mentions_check and not result.mentions_check.get("error"):
            print(f"   Visibility: {result.mentions_check.get('visibility', 'N/A')}%")
            print(f"   Band: {result.mentions_check.get('band', 'N/A')}")
        else:
            print(f"   Mentions Check: {'Error' if result.mentions_check else 'Not run'}")
        
        # Save HTML report
        if result.html_report:
            html_file = "test_report.html"
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(result.html_report)
            print(f"\n📄 HTML Report saved: {html_file}")
        
        # Save PDF report
        if result.pdf_base64:
            pdf_file = "test_report.pdf"
            pdf_bytes = base64.b64decode(result.pdf_base64)
            with open(pdf_file, "wb") as f:
                f.write(pdf_bytes)
            print(f"📑 PDF Report saved: {pdf_file} ({result.pdf_size_bytes} bytes)")
        
        # Save JSON data
        json_file = "test_report_data.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump({
                "url": result.url,
                "company_name": result.company_name,
                "company_analysis": result.company_analysis,
                "health_check": result.health_check,
                "mentions_check": result.mentions_check,
                "analysis_time_seconds": result.analysis_time_seconds,
                "success": result.success,
                "errors": result.errors,
            }, f, indent=2, default=str)
        print(f"📋 JSON Data saved: {json_file}")
        
        print("\n✨ Test complete!")
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_individual_endpoints(url: str, company_name: str = None):
    """Test individual endpoints to verify they're working."""
    
    base_url = os.getenv("AEO_CHECKS_URL", "http://localhost:8000")
    
    print(f"\n🔧 Testing individual endpoints at {base_url}...")
    
    # Test status
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/status")
            if response.status_code == 200:
                print("✅ Status endpoint: OK")
            else:
                print(f"⚠️  Status endpoint: {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint: {str(e)}")
    
    # Test health check (fastest)
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{base_url}/health/check",
                json={"url": url}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: Score {data.get('score', 'N/A')}")
            else:
                print(f"⚠️  Health check: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check: {str(e)}")


def main():
    """Main test function."""
    if len(sys.argv) < 2:
        print("Usage: python test_local.py <URL> [company_name]")
        print("\nExample:")
        print("  python test_local.py https://example.com")
        print("  python test_local.py https://example.com 'Example Inc'")
        print("\nEnvironment variables:")
        print("  AEO_CHECKS_URL=http://localhost:8000")
        print("  PDF_SERVICE_URL=http://localhost:8001")
        sys.exit(1)
    
    url = sys.argv[1]
    company_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Test individual endpoints first
    asyncio.run(test_individual_endpoints(url, company_name))
    
    # Run complete analysis
    result = asyncio.run(test_complete_analysis(url, company_name))
    
    if result and result.success:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

