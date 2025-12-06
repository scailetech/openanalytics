"""
Simple HTML to PDF exporter.

Reads an HTML file and posts it to a configurable PDF endpoint.
Default endpoint: http://localhost:8000/pdf/convert
Expected payload (POST JSON):
{
  "html": "<html>...</html>",
  "format": "A4",
  "print_background": true,
  "color_scheme": "dark"
}
"""

import os
import argparse
import requests


def export_pdf(html_path: str, output_path: str, endpoint: str) -> None:
    with open(html_path, "r", encoding="utf-8") as f:
        html = f.read()

    payload = {
        "html": html,
        "format": "A4",
        "print_background": True,
        "color_scheme": "dark",
    }

    resp = requests.post(endpoint, json=payload, timeout=60)
    resp.raise_for_status()

    data = resp.json()
    pdf_b64 = data.get("pdf_base64")
    if not pdf_b64:
        raise RuntimeError("No pdf_base64 returned from PDF service")

    import base64

    pdf_bytes = base64.b64decode(pdf_b64)
    with open(output_path, "wb") as f:
        f.write(pdf_bytes)

    size_kb = len(pdf_bytes) / 1024
    print(f"✅ PDF saved to {output_path} ({size_kb:.1f} KB)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export HTML to PDF via HTTP service")
    parser.add_argument("html_path", help="Path to input HTML file")
    parser.add_argument(
        "--output",
        "-o",
        default="report.pdf",
        help="Output PDF path (default: report.pdf)",
    )
    parser.add_argument(
        "--endpoint",
        "-e",
        default=os.getenv("PDF_ENDPOINT", "http://localhost:8000/pdf/convert"),
        help="PDF service endpoint (default env PDF_ENDPOINT or http://localhost:8000/pdf/convert)",
    )
    args = parser.parse_args()

    export_pdf(args.html_path, args.output, args.endpoint)


if __name__ == "__main__":
    main()

