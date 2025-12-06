# Report Generation

HTML report generation utilities for AEO analysis data.

## Usage

```python
from reports.html_generator import generate_report_html

# Generate HTML report from API responses
html_report = generate_report_html(
    company_data=company_response.json(),
    health_data=health_response.json(),
    mentions_data=mentions_response.json(),
    client_name="Example Inc",
    website_url="https://example.com",
    theme="dark"  # or "light"
)

# Save to file
with open("report.html", "w") as f:
    f.write(html_report)

# Or convert to PDF using your PDF service
import requests
pdf_response = requests.post(
    "http://localhost:8000/pdf/convert",  # Configure your PDF service endpoint
    json={
        "html": html_report,
        "format": "A4",
        "print_background": True,
        "color_scheme": "dark"
    }
)
```

## Features

- **Professional Design** - Clean, modern report layout
- **Dark/Light Themes** - Choose your preferred theme
- **Score Cards** - Visual representation of scores
- **Platform Breakdown** - Detailed AI platform statistics
- **Print-Ready** - Optimized for PDF conversion

## Example

See `html_generator.py` for a complete example with sample data.

