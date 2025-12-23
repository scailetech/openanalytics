#!/usr/bin/env python3
"""
OpenAnalytics CLI - AEO Health Checks & AI Mentions Analysis

Fully standalone - requires only Gemini API key.

Run comprehensive AEO analysis from your terminal:
- Health Check: 29 checks across Technical, Schema, AI Access, Authority
- Mentions Check: AI visibility analysis using Gemini with Google Search grounding

Usage:
    openanalytics health https://example.com
    openanalytics mentions "Company Name" --url https://company.com
"""

import asyncio
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bs4 import BeautifulSoup
from fetcher import fetch_website
from checks.technical import run_technical_checks, extract_technical_summary
from checks.structured_data import run_structured_data_checks, extract_structured_data_summary, extract_schema_data
from checks.aeo_crawler import run_aeo_crawler_checks, extract_crawler_summary
from checks.authority import run_authority_checks, extract_authority_summary
from scoring import (
    calculate_tiered_score,
    calculate_grade,
    calculate_visibility_band,
    calculate_category_clarity_score,
    calculate_entity_strength_score,
    calculate_authority_signal_score,
    count_issues_by_severity,
)

console = Console()

# Output directory
DOWNLOADS_DIR = Path.home() / "Downloads"
CONFIG_DIR = Path.home() / ".openanalytics"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config() -> dict:
    """Load configuration."""
    if not CONFIG_FILE.exists():
        return {}
    try:
        return json.loads(CONFIG_FILE.read_text())
    except Exception:
        return {}


def save_config(config: dict) -> None:
    """Save configuration."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


# ============================================================================
# MENTIONS CHECK - Gemini Only (Standalone)
# ============================================================================

def generate_mention_queries(company_name: str, industry: str = "", num_queries: int = 10) -> List[Dict[str, str]]:
    """Generate queries to check AI visibility."""
    queries = []

    # Branded queries
    queries.append({"query": f"What is {company_name}?", "dimension": "Branded"})
    queries.append({"query": f"Tell me about {company_name}", "dimension": "Branded"})
    queries.append({"query": f"{company_name} reviews", "dimension": "Branded"})

    # Competitive queries
    queries.append({"query": f"{company_name} alternatives", "dimension": "Competitive"})
    queries.append({"query": f"{company_name} vs competitors", "dimension": "Competitive"})

    # Industry queries
    if industry:
        queries.append({"query": f"best {industry} companies", "dimension": "Industry"})
        queries.append({"query": f"top {industry} tools", "dimension": "Industry"})
        queries.append({"query": f"{industry} software recommendations", "dimension": "Industry"})
    else:
        queries.append({"query": f"best companies like {company_name}", "dimension": "Industry"})
        queries.append({"query": f"top tools similar to {company_name}", "dimension": "Industry"})

    # Use case queries
    queries.append({"query": f"how to solve problems with {company_name}", "dimension": "Use-Case"})
    queries.append({"query": f"when to use {company_name}", "dimension": "Use-Case"})

    return queries[:num_queries]


def detect_mention_type(text: str, company_name: str) -> str:
    """Detect how the company is mentioned."""
    text_lower = text.lower()
    company_lower = company_name.lower()

    if company_lower not in text_lower:
        return "none"

    # Check for recommendation patterns
    recommend_patterns = [
        f"recommend {company_lower}",
        f"{company_lower} is the best",
        f"best.*{company_lower}",
        f"{company_lower}.*excellent",
    ]
    for pattern in recommend_patterns:
        if re.search(pattern, text_lower):
            return "primary_recommendation"

    # Check for top option patterns
    if re.search(f"(top|leading|best).*{company_lower}", text_lower):
        return "top_option"

    # Check for list patterns
    if re.search(f"\\d+\\.|\\*.*{company_lower}", text, re.IGNORECASE):
        return "listed_option"

    return "mentioned_in_context"


def count_mentions(text: str, company_name: str) -> Dict[str, Any]:
    """Count and score mentions."""
    raw_mentions = len(re.findall(re.escape(company_name), text, re.IGNORECASE))

    if raw_mentions == 0:
        return {
            "raw_mentions": 0,
            "capped_mentions": 0,
            "quality_score": 0.0,
            "mention_type": "none",
        }

    capped_mentions = min(raw_mentions, 3)
    mention_type = detect_mention_type(text, company_name)

    # Score by mention type
    scores = {
        "primary_recommendation": 9.0,
        "top_option": 7.0,
        "listed_option": 5.0,
        "mentioned_in_context": 3.0,
        "none": 0.0,
    }
    quality_score = scores.get(mention_type, 3.0)

    # Bonus for multiple mentions
    quality_score = min(10.0, quality_score + (capped_mentions - 1) * 0.5)

    return {
        "raw_mentions": raw_mentions,
        "capped_mentions": capped_mentions,
        "quality_score": round(quality_score, 2),
        "mention_type": mention_type,
    }


async def query_gemini(query: str, api_key: str) -> Dict[str, Any]:
    """Query Gemini with Google Search grounding."""
    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise Exception("google-genai not installed. Run: pip install google-genai")

    client = genai.Client(api_key=api_key)

    prompt = f"""You are a helpful AI assistant. Answer the following question using current information from the web.

Question: {query}

Provide a helpful, informative answer. If you mention specific companies or products, be accurate."""

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=1024,
                tools=[
                    types.Tool(google_search=types.GoogleSearch()),
                ]
            )
        )
        return {"response": response.text, "error": None}
    except Exception as e:
        return {"response": "", "error": str(e)}


@click.group()
@click.version_option(version="4.0.0")
def cli():
    """
    OpenAnalytics - AEO Health Checks & AI Mentions Analysis

    Fully standalone - requires only Gemini API key.
    """
    pass


@cli.command()
@click.argument("url")
@click.option("--output", "-o", default=None, help="Output file (json)")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed results")
def health(url: str, output: Optional[str], verbose: bool):
    """
    Run AEO health check on a website.

    Performs 29 checks across 4 categories:
    - Technical SEO (16 checks)
    - Structured Data (6 checks)
    - AI Crawler Access (4 checks)
    - Authority Signals (3 checks)

    Example:
        openanalytics health https://example.com
        openanalytics health https://example.com -v
    """
    console.print()
    console.print(Panel(
        f"[bold cyan]OpenAnalytics - AEO Health Check[/bold cyan]\n\n"
        f"URL: [green]{url}[/green]",
        border_style="cyan"
    ))
    console.print()

    async def run_check():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Fetching website...", total=None)

            result = await fetch_website(url)

            if result.error or not result.html:
                console.print(f"\n[red]Error:[/red] Failed to fetch website: {result.error}")
                sys.exit(1)

            progress.update(task, description="[cyan]Parsing HTML...")

            soup = BeautifulSoup(result.html, 'lxml')
            all_issues = []

            progress.update(task, description="[cyan]Running technical checks...")
            technical_issues = run_technical_checks(
                soup, result.final_url,
                sitemap_found=result.sitemap_found,
                response_time_ms=result.html_response_time_ms
            )
            all_issues.extend(technical_issues)

            progress.update(task, description="[cyan]Running structured data checks...")
            structured_issues = run_structured_data_checks(soup)
            all_issues.extend(structured_issues)

            schema_types, all_schemas, org_schema = extract_schema_data(soup)
            structured_summary = extract_structured_data_summary(soup)
            same_as_urls = structured_summary.get('same_as_urls', [])

            progress.update(task, description="[cyan]Running AI crawler checks...")
            crawler_issues = run_aeo_crawler_checks(result.robots_txt)
            all_issues.extend(crawler_issues)

            progress.update(task, description="[cyan]Running authority checks...")
            authority_issues = run_authority_checks(soup, same_as_urls=same_as_urls)
            all_issues.extend(authority_issues)

            progress.update(task, description="[cyan]Calculating scores...")

            overall_score, tier_details = calculate_tiered_score(all_issues)
            grade = calculate_grade(overall_score)
            visibility_band, band_color = calculate_visibility_band(overall_score)

            category_clarity = calculate_category_clarity_score(soup, schema_types, org_schema)
            entity_strength = calculate_entity_strength_score(
                org_schema, structured_summary['same_as_count'], soup
            )
            authority_signal = calculate_authority_signal_score(all_issues)

            severity_counts = count_issues_by_severity(all_issues)

            technical_summary = extract_technical_summary(soup, result.final_url)
            crawler_summary = extract_crawler_summary(result.robots_txt)
            authority_summary = extract_authority_summary(soup, same_as_urls=same_as_urls)

            return {
                "url": result.final_url,
                "score": overall_score,
                "grade": grade,
                "visibility_band": visibility_band,
                "tier_info": tier_details,
                "category_clarity_score": category_clarity,
                "entity_strength_score": entity_strength,
                "authority_signal_score": authority_signal,
                "total_checks": len(all_issues),
                "passed": severity_counts['passed'],
                "errors": severity_counts['errors'],
                "warnings": severity_counts['warnings'],
                "notices": severity_counts['notices'],
                "issues": all_issues,
                "summary": {
                    **technical_summary,
                    **structured_summary,
                    **crawler_summary,
                    **authority_summary,
                    "response_time_ms": result.html_response_time_ms,
                    "js_rendered": result.js_rendered,
                }
            }

    try:
        result = asyncio.run(run_check())
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        sys.exit(1)

    grade_colors = {"A+": "green", "A": "green", "B": "yellow", "C": "orange1", "D": "red", "F": "red"}
    grade_color = grade_colors.get(result["grade"], "white")

    console.print()
    console.print(Panel(
        f"[bold]Score:[/bold] [{grade_color}]{result['score']:.0f}/100[/{grade_color}]  "
        f"[bold]Grade:[/bold] [{grade_color}]{result['grade']}[/{grade_color}]  "
        f"[bold]Band:[/bold] {result['visibility_band']}\n\n"
        f"[bold]Checks:[/bold] {result['passed']} passed, "
        f"[red]{result['errors']} errors[/red], "
        f"[yellow]{result['warnings']} warnings[/yellow], "
        f"{result['notices']} notices\n\n"
        f"[bold]Limiting Factor:[/bold] {result['tier_info']['limiting_reason']}",
        title="[bold green]Results[/bold green]",
        border_style="green"
    ))

    if verbose:
        console.print()
        table = Table(title="Issues Found", show_header=True, header_style="bold")
        table.add_column("Check", style="cyan", width=30)
        table.add_column("Category", style="dim")
        table.add_column("Severity", width=10)
        table.add_column("Status", width=8)

        for issue in result["issues"]:
            severity_style = {"error": "red", "warning": "yellow", "notice": "dim"}.get(issue["severity"], "white")
            status = "[green]PASS[/green]" if issue["passed"] else f"[{severity_style}]FAIL[/{severity_style}]"
            table.add_row(
                issue["check"][:30],
                issue["category"],
                f"[{severity_style}]{issue['severity']}[/{severity_style}]",
                status
            )

        console.print(table)

        console.print()
        summary = result["summary"]
        console.print(f"[bold]Title:[/bold] {summary.get('title', 'N/A')[:60]}")
        console.print(f"[bold]Schema Types:[/bold] {', '.join(summary.get('schema_types', [])) or 'None'}")
        console.print(f"[bold]AI Crawlers Allowed:[/bold] {', '.join(summary.get('ai_crawlers_allowed', [])) or 'None'}")
        console.print(f"[bold]AI Crawlers Blocked:[/bold] {', '.join(summary.get('ai_crawlers_blocked', [])) or 'None'}")

    output_path = output
    if not output_path:
        safe_url = url.replace("https://", "").replace("http://", "").replace("/", "-")[:30]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = DOWNLOADS_DIR / f"aeo-health-{safe_url}-{timestamp}.json"

    Path(output_path).write_text(json.dumps(result, indent=2, default=str))
    console.print(f"\n[dim]Saved to:[/dim] [cyan]{output_path}[/cyan]")
    console.print()


@cli.command()
@click.argument("company_name")
@click.option("--industry", "-i", default="", help="Industry/category for better queries")
@click.option("--queries", "-n", default=10, help="Number of queries (default: 10)")
@click.option("--output", "-o", default=None, help="Output file (json)")
@click.option("--verbose", "-v", is_flag=True, help="Show detailed results")
def mentions(company_name: str, industry: str, queries: int, output: Optional[str], verbose: bool):
    """
    Check AI visibility for a company using Gemini.

    Uses Gemini with Google Search grounding to simulate how AI
    assistants respond to queries about your company.

    Example:
        openanalytics mentions "Acme Inc"
        openanalytics mentions "Acme Inc" --industry "project management"
        openanalytics mentions "Acme Inc" -n 20 -v
    """
    # Check API key
    config = get_config()
    api_key = os.getenv("GEMINI_API_KEY") or config.get("gemini_key")

    if not api_key:
        console.print()
        console.print(Panel(
            "[bold red]No API key configured![/bold red]\n\n"
            "OpenAnalytics needs a Gemini API key.\n\n"
            "[bold]Quick setup:[/bold]\n\n"
            "  [cyan]openanalytics config[/cyan]\n\n"
            "[bold]Or set environment variable:[/bold]\n\n"
            "  [cyan]export GEMINI_API_KEY='your-key'[/cyan]",
            border_style="red"
        ))
        console.print()
        sys.exit(1)

    console.print()
    console.print(Panel(
        f"[bold cyan]OpenAnalytics - AI Mentions Check[/bold cyan]\n\n"
        f"Company: [green]{company_name}[/green]\n"
        f"Industry: [dim]{industry or '(not specified)'}[/dim]\n"
        f"Queries: [yellow]{queries}[/yellow]",
        border_style="cyan"
    ))
    console.print()

    async def run_check():
        start_time = time.time()

        # Generate queries
        query_list = generate_mention_queries(company_name, industry, queries)

        all_results = []
        total_mentions = 0
        total_quality = 0.0
        errors = 0

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Querying Gemini...", total=len(query_list))

            for i, query_data in enumerate(query_list):
                query = query_data["query"]
                dimension = query_data["dimension"]
                progress.update(task, completed=i, description=f"[cyan]Query {i+1}/{len(query_list)}: {query[:35]}...")

                result = await query_gemini(query, api_key)

                if result["error"]:
                    errors += 1
                    continue

                response_text = result["response"]
                mention_data = count_mentions(response_text, company_name)

                all_results.append({
                    "query": query,
                    "dimension": dimension,
                    "platform": "gemini",
                    **mention_data,
                    "response_preview": response_text[:300],
                })

                total_mentions += mention_data["capped_mentions"]
                total_quality += mention_data["quality_score"]

            progress.update(task, completed=len(query_list), description="[green]Done!")

        # Calculate visibility
        total_responses = len(all_results)
        responses_with_mentions = sum(1 for r in all_results if r["mention_type"] != "none")
        presence_rate = responses_with_mentions / total_responses if total_responses > 0 else 0
        avg_quality = total_quality / max(responses_with_mentions, 1) if responses_with_mentions > 0 else 0
        quality_factor = 0.85 + (avg_quality / 10) * 0.30
        visibility = min(100.0, presence_rate * quality_factor * 100)

        # Determine band
        if visibility >= 80:
            band = "Dominant"
        elif visibility >= 60:
            band = "Strong"
        elif visibility >= 40:
            band = "Moderate"
        elif visibility >= 20:
            band = "Weak"
        else:
            band = "Minimal"

        execution_time = time.time() - start_time

        return {
            "company_name": company_name,
            "industry": industry,
            "visibility": round(visibility, 1),
            "band": band,
            "mentions": total_mentions,
            "presence_rate": round(presence_rate * 100, 1),
            "quality_score": round(avg_quality, 2),
            "queries_processed": len(query_list),
            "responses": total_responses,
            "errors": errors,
            "execution_time_seconds": round(execution_time, 2),
            "results": all_results,
        }

    try:
        result = asyncio.run(run_check())
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        sys.exit(1)

    # Display results
    band_colors = {"Dominant": "green", "Strong": "blue", "Moderate": "yellow", "Weak": "orange1", "Minimal": "red"}
    band_color = band_colors.get(result["band"], "white")

    console.print()
    console.print(Panel(
        f"[bold]Visibility:[/bold] [{band_color}]{result['visibility']:.1f}%[/{band_color}]  "
        f"[bold]Band:[/bold] [{band_color}]{result['band']}[/{band_color}]\n\n"
        f"[bold]Mentions:[/bold] {result['mentions']}  "
        f"[bold]Presence Rate:[/bold] {result['presence_rate']:.1f}%  "
        f"[bold]Quality:[/bold] {result['quality_score']:.1f}/10\n\n"
        f"[bold]Queries:[/bold] {result['queries_processed']}  "
        f"[bold]Responses:[/bold] {result['responses']}  "
        f"[bold]Time:[/bold] {result['execution_time_seconds']:.1f}s",
        title="[bold green]AI Visibility Results[/bold green]",
        border_style="green"
    ))

    if verbose and result["results"]:
        console.print()
        table = Table(title="Query Results", show_header=True, header_style="bold")
        table.add_column("Query", style="cyan", width=40)
        table.add_column("Mentions", justify="right", width=10)
        table.add_column("Type", width=20)
        table.add_column("Score", justify="right", width=8)

        for r in result["results"]:
            mention_style = "green" if r["mention_type"] != "none" else "dim"
            table.add_row(
                r["query"][:40],
                f"[{mention_style}]{r['capped_mentions']}[/{mention_style}]",
                r["mention_type"],
                f"{r['quality_score']:.1f}"
            )

        console.print(table)

    # Save output
    output_path = output
    if not output_path:
        safe_name = company_name.replace(" ", "-").lower()[:20]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = DOWNLOADS_DIR / f"aeo-mentions-{safe_name}-{timestamp}.json"

    Path(output_path).write_text(json.dumps(result, indent=2, default=str))
    console.print(f"\n[dim]Saved to:[/dim] [cyan]{output_path}[/cyan]")
    console.print()


@cli.command()
def config():
    """Configure your Gemini API key."""
    console.print()
    console.print(Panel(
        "[bold]Configuration[/bold]\n\n"
        "OpenAnalytics uses Google's Gemini AI.\n"
        "You need a free API key to use the mentions check.",
        border_style="cyan"
    ))
    console.print()

    current_config = get_config()

    if current_config.get("gemini_key"):
        key = current_config["gemini_key"]
        masked = f"{key[:8]}...{key[-4:]}"
        console.print(f"[green]Current API key:[/green] {masked}")
        console.print()

        if not click.confirm("Update API key?", default=False):
            console.print("\n[dim]Configuration unchanged.[/dim]\n")
            return

    console.print()
    console.print("[bold]Get Your Free API Key:[/bold]")
    console.print("1. Visit: [cyan]https://aistudio.google.com/apikey[/cyan]")
    console.print("2. Click 'Create API Key'")
    console.print("3. Copy the key and paste below")
    console.print()

    api_key = click.prompt("Enter your Gemini API key")

    if not api_key or len(api_key) < 10:
        console.print("\n[red]Invalid API key.[/red]\n")
        sys.exit(1)

    current_config["gemini_key"] = api_key.strip()
    save_config(current_config)

    console.print()
    console.print(Panel(
        "[bold green]Configuration saved![/bold green]\n\n"
        f"Config file: [dim]{CONFIG_FILE}[/dim]\n\n"
        "[cyan]Try:[/cyan] openanalytics mentions \"Your Company\"",
        border_style="green"
    ))
    console.print()


@cli.command()
def check():
    """Check API key configuration."""
    console.print()
    console.print("[bold cyan]OpenAnalytics - Configuration Check[/bold cyan]")
    console.print()

    gemini_key = os.getenv("GEMINI_API_KEY") or get_config().get("gemini_key")

    table = Table(show_header=False)
    table.add_column("Setting", style="dim")
    table.add_column("Status")

    if gemini_key:
        table.add_row("GEMINI_API_KEY", f"[green]Set[/green] ({gemini_key[:8]}...)")
    else:
        table.add_row("GEMINI_API_KEY", "[red]Not set[/red]")

    console.print(table)
    console.print()

    if not gemini_key:
        console.print("[bold]Setup:[/bold]")
        console.print("  openanalytics config")
        console.print("  # or")
        console.print("  export GEMINI_API_KEY='your-key'")
    else:
        console.print("[green]Ready![/green]")

    console.print()


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
