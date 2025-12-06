"""
HTML Report Generator - Python Implementation

Generates standalone HTML reports for AEO analysis.
"""

from typing import Optional, Literal, TypedDict, List, Dict, Any
from datetime import datetime

try:
    from .design_system import (
        escape_html, format_number, format_percent, get_score_class, get_rating,
        ICONS, SCAILE_LOGO, SCAILE_BRAND, get_styles, build_footer
    )
    from .components import (
        ProgressBar, MetricRow, CompetitorRow, QueryRow, QualityBar, ActionItem,
        build_table_of_contents, get_status_color, Grid2
    )
except ImportError:
    # Fallback for direct script execution
    from design_system import (
        escape_html, format_number, format_percent, get_score_class, get_rating,
        ICONS, SCAILE_LOGO, SCAILE_BRAND, get_styles, build_footer
    )
    from components import (
        ProgressBar, MetricRow, CompetitorRow, QueryRow, QualityBar, ActionItem,
        build_table_of_contents, get_status_color, Grid2
    )

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================

class ContentStrategyPillar(TypedDict):
    name: str
    subtitle: str
    clusters: List[str]

class ContentStrategyPriorityContent(TypedDict):
    title: str
    description: str
    wordCount: str
    priority: Literal['Critical', 'High', 'Medium', 'Low']
    schema: List[str]

class ContentStrategy(TypedDict):
    pillars: List[ContentStrategyPillar]
    priorityContent: List[ContentStrategyPriorityContent]
    priorityOrder: List[Dict[str, Any]]
    monthlyCapacity: str

class CtaConfig(TypedDict, total=False):
    name: str
    title: str
    photoBase64: Optional[str]
    description: str
    calendlyLink: str
    linkedinLink: Optional[str]

class HtmlReportData(TypedDict, total=False):
    canvasData: Dict[str, Any]  # CallCanvasData
    queryInsights: Optional[Dict[str, Any]]  # QueryInsights
    clientName: str
    websiteUrl: Optional[str]
    logoUrl: Optional[str]
    generatedAt: Optional[datetime]
    contentStrategy: Optional[ContentStrategy]
    ctaConfig: Optional[CtaConfig]
    theme: Literal['dark', 'light']

# ============================================================================
# INDUSTRY BENCHMARKS
# ============================================================================

INDUSTRY_BENCHMARKS: Dict[str, Dict[str, Any]] = {
    'SaaS': {'avgVisibility': 35, 'topPerformerVisibility': 70, 'avgMentionQuality': 5.5, 'description': 'Software as a Service'},
    'Software': {'avgVisibility': 32, 'topPerformerVisibility': 65, 'avgMentionQuality': 5.2, 'description': 'Software & Technology'},
    'Technology': {'avgVisibility': 30, 'topPerformerVisibility': 60, 'avgMentionQuality': 5.0, 'description': 'Technology companies'},
    'AI': {'avgVisibility': 45, 'topPerformerVisibility': 80, 'avgMentionQuality': 6.5, 'description': 'AI & Machine Learning'},
    'Cybersecurity': {'avgVisibility': 38, 'topPerformerVisibility': 72, 'avgMentionQuality': 5.8, 'description': 'Security software'},
    'B2B Services': {'avgVisibility': 28, 'topPerformerVisibility': 55, 'avgMentionQuality': 4.8, 'description': 'Business services'},
    'Consulting': {'avgVisibility': 25, 'topPerformerVisibility': 50, 'avgMentionQuality': 4.5, 'description': 'Professional consulting'},
    'Marketing': {'avgVisibility': 30, 'topPerformerVisibility': 58, 'avgMentionQuality': 5.0, 'description': 'Marketing & Advertising'},
    'HR Tech': {'avgVisibility': 32, 'topPerformerVisibility': 62, 'avgMentionQuality': 5.3, 'description': 'HR & Recruitment Tech'},
    'Recruitment': {'avgVisibility': 30, 'topPerformerVisibility': 58, 'avgMentionQuality': 5.0, 'description': 'Recruitment & Staffing'},
    'E-commerce': {'avgVisibility': 25, 'topPerformerVisibility': 55, 'avgMentionQuality': 4.5, 'description': 'Online retail'},
    'Retail': {'avgVisibility': 22, 'topPerformerVisibility': 48, 'avgMentionQuality': 4.2, 'description': 'Retail & Consumer goods'},
    'DTC': {'avgVisibility': 28, 'topPerformerVisibility': 52, 'avgMentionQuality': 4.8, 'description': 'Direct to Consumer'},
    'Fintech': {'avgVisibility': 35, 'topPerformerVisibility': 68, 'avgMentionQuality': 5.5, 'description': 'Financial technology'},
    'Finance': {'avgVisibility': 30, 'topPerformerVisibility': 60, 'avgMentionQuality': 5.0, 'description': 'Financial services'},
    'Insurance': {'avgVisibility': 25, 'topPerformerVisibility': 52, 'avgMentionQuality': 4.5, 'description': 'Insurance providers'},
    'Healthcare': {'avgVisibility': 28, 'topPerformerVisibility': 55, 'avgMentionQuality': 5.2, 'description': 'Healthcare & Medical'},
    'Health Tech': {'avgVisibility': 32, 'topPerformerVisibility': 62, 'avgMentionQuality': 5.5, 'description': 'Health technology'},
    'Biotech': {'avgVisibility': 30, 'topPerformerVisibility': 58, 'avgMentionQuality': 5.3, 'description': 'Biotechnology'},
    'Education': {'avgVisibility': 25, 'topPerformerVisibility': 50, 'avgMentionQuality': 4.8, 'description': 'Education & EdTech'},
    'Real Estate': {'avgVisibility': 22, 'topPerformerVisibility': 45, 'avgMentionQuality': 4.2, 'description': 'Real estate & PropTech'},
    'Manufacturing': {'avgVisibility': 20, 'topPerformerVisibility': 42, 'avgMentionQuality': 4.0, 'description': 'Manufacturing & Industrial'},
    'Default': {'avgVisibility': 28, 'topPerformerVisibility': 55, 'avgMentionQuality': 5.0, 'description': 'General industry average'},
}

def get_industry_benchmark(industry: Optional[str]) -> Dict[str, Any]:
    """Get benchmark for an industry with fuzzy matching"""
    if not industry:
        return {**INDUSTRY_BENCHMARKS['Default'], 'matchedIndustry': 'General', 'isDefault': True}
    
    industry_segments = [s.strip().lower() for s in industry.split(',') if s.strip()]
    
    priority_order = [
        'AI', 'Cybersecurity', 'Fintech', 'Health Tech', 'HR Tech', 'SaaS',
        'Software', 'Technology', 'B2B Services', 'Consulting', 'Marketing',
        'E-commerce', 'DTC', 'Retail', 'Finance', 'Insurance', 'Healthcare',
        'Biotech', 'Education', 'Real Estate', 'Manufacturing', 'Recruitment'
    ]
    
    # Try exact match
    for segment in industry_segments:
        for key, benchmark in INDUSTRY_BENCHMARKS.items():
            if key.lower() == segment:
                return {**benchmark, 'matchedIndustry': key, 'isDefault': False}
    
    # Try priority matching
    for priority_key in priority_order:
        priority_lower = priority_key.lower()
        for segment in industry_segments:
            if priority_lower in segment or segment in priority_lower:
                if priority_key in INDUSTRY_BENCHMARKS:
                    return {**INDUSTRY_BENCHMARKS[priority_key], 'matchedIndustry': priority_key, 'isDefault': False}
    
    return {**INDUSTRY_BENCHMARKS['Default'], 'matchedIndustry': 'General', 'isDefault': True}

def format_ordinal(n: int) -> str:
    """Format number with ordinal suffix"""
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return f"{n}{suffix}"

def calculate_percentile(value: float, avg_value: float, top_value: float) -> float:
    """Calculate percentile ranking"""
    if top_value == avg_value:
        return 50.0
    if value >= top_value:
        return 100.0
    if value <= avg_value:
        return max(0, (value / avg_value) * 50)
    return 50 + ((value - avg_value) / (top_value - avg_value)) * 50

def get_grade_class(grade: str) -> str:
    """Get CSS class for grade badge"""
    grade_upper = grade.upper()
    if grade_upper in ['A', 'A+', 'A-']:
        return 'grade-A'
    if grade_upper in ['B', 'B+', 'B-']:
        return 'grade-B'
    if grade_upper in ['C', 'C+', 'C-']:
        return 'grade-C'
    if grade_upper in ['D', 'D+', 'D-']:
        return 'grade-D'
    if grade_upper in ['F']:
        return 'grade-F'
    return 'grade-C'

def get_priority_class(priority: str) -> str:
    """Get priority class for content strategy - matches TypeScript"""
    priority_lower = priority.lower() if priority else 'medium'
    if priority_lower == 'critical':
        return 'status-critical'
    elif priority_lower == 'high':
        return 'status-high'
    elif priority_lower == 'medium':
        return 'status-medium'
    elif priority_lower == 'low':
        return 'status-low'
    return 'status-medium'

# ============================================================================
# SECTION BUILDERS
# ============================================================================

def build_example_queries_section(data: HtmlReportData) -> str:
    """Build example queries section - matches TypeScript exactly"""
    canvas_data = data.get('canvasData', {})
    query_results = canvas_data.get('mentionsCheck', {}).get('query_results', [])
    
    if not query_results:
        return ''
    
    # Get unique queries by dimension (max 10)
    by_dimension = {}
    for qr in query_results:
        query = qr.get('query', '')
        dimension = qr.get('dimension', '')
        if not query or not dimension:
            continue
        dim = dimension.lower()
        if dim not in by_dimension:
            by_dimension[dim] = []
        if query not in by_dimension[dim]:
            by_dimension[dim].append(query)
    
    # Take queries evenly from each dimension
    result = []
    dimensions = list(by_dimension.keys())
    round_num = 0
    
    while len(result) < 10 and dimensions:
        for dim in list(dimensions):
            if len(result) >= 10:
                break
            queries = by_dimension[dim]
            if round_num < len(queries):
                result.append({'query': queries[round_num], 'dimension': dim})
            else:
                dimensions.remove(dim)
        round_num += 1
    
    if not result:
        return ''
    
    num_queries = canvas_data.get('mentionsCheck', {}).get('numQueries', 50)
    is_fast_mode = num_queries <= 10
    
    query_rows = ''.join([
        QueryRow({'dimension': item['dimension'], 'query': item['query']})
        for item in result
    ])
    
    return f"""
    <div class="section">
      <h2 class="section-title">
        <span class="icon">{ICONS['clipboardList']}</span>
        Sample Queries We Test
      </h2>
      <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
        {len(result)} example queries for {escape_html(data.get('clientName', ''))} across different search intents:
      </p>
      {Grid2(query_rows)}
      {f'<p style="font-size: 11px; color: var(--text-muted); margin-top: 16px; font-style: italic;">Full analysis includes {num_queries}+ queries across 10 dimensions.</p>' if not is_fast_mode else ''}
    </div>
    """

def build_methodology_callout() -> str:
    """Build methodology explanation callout"""
    return f"""
    <div class="alert alert-info">
      <div class="alert-title">How We Test</div>
      <div class="alert-text">
        We query 5 major AI platforms (ChatGPT, Perplexity, Claude, Gemini, Mistral) with 
        {escape_html('50+')} real-world prompts across commercial, competitive, informational, and branded dimensions. 
        Each response is analyzed for brand mentions, competitor presence, and mention quality.
      </div>
    </div>
    """

def build_executive_summary(data: HtmlReportData) -> str:
    """Build executive summary section"""
    canvas_data = data.get('canvasData', {})
    health = canvas_data.get('aeoHealthCheck', {})
    mentions = canvas_data.get('mentionsCheck', {})
    
    grade = health.get('grade', 'N/A')
    health_score = health.get('healthScore', 0)
    visibility = mentions.get('visibility', 0)
    band = mentions.get('band', 'Unknown')
    total_mentions = mentions.get('chatgptPresence', 0)
    quality_score_raw = mentions.get('qualityScore', 0)
    quality_score = quality_score_raw * 10
    
    band_class = 'good' if band in ['Dominant', 'Strong'] else 'fair' if band == 'Moderate' else 'poor'
    
    return f"""
    <div class="section-secondary">
      <h2 class="section-title">
        <span class="icon">{ICONS['chartBar']}</span>
        Executive Summary
      </h2>
      
      <div class="score-grid">
        <div class="score-card">
          <div class="label">AEO Health Grade</div>
          <div class="grade-badge {get_grade_class(grade)}">{escape_html(grade)}</div>
          <div class="status {'bg-good' if health_score >= 70 else 'bg-fair' if health_score >= 50 else 'bg-poor'}">
            Score: {format_number(health_score)}
          </div>
        </div>
        
        <div class="score-card">
          <div class="label">AI Visibility</div>
          <div class="value score-{band_class}">{format_number(visibility)}<span class="unit">%</span></div>
          <div class="status bg-{band_class}">
            {escape_html(band)}
          </div>
        </div>
        
        <div class="score-card">
          <div class="label">Total Mentions</div>
          <div class="value score-{get_score_class(total_mentions, 40, 25, 10)}">{format_number(total_mentions)}</div>
          <div class="status bg-{get_score_class(total_mentions, 40, 25, 10)}">
            of {mentions.get('numQueries', 50)} queries
          </div>
        </div>
        
        <div class="score-card">
          <div class="label">Mention Quality</div>
          <div class="value score-{get_score_class(quality_score, 70, 50, 30)}">{quality_score_raw:.1f}<span class="unit">/10</span></div>
          <div class="status bg-{get_score_class(quality_score, 70, 50, 30)}">
            {'Primary recommendations' if quality_score >= 70 else 'Detailed mentions' if quality_score >= 50 else 'Brief mentions' if quality_score >= 20 else 'Name drops only'}
          </div>
        </div>
      </div>
    </div>
    """

def build_industry_benchmark(data: HtmlReportData) -> str:
    """Build industry benchmark comparison section"""
    canvas_data = data.get('canvasData', {})
    visibility = canvas_data.get('mentionsCheck', {}).get('visibility', 0)
    quality_score = canvas_data.get('mentionsCheck', {}).get('qualityScore', 0)
    industry = canvas_data.get('clientInfo', {}).get('industry', 'General')
    client_name = data.get('clientName', '')
    
    benchmark = get_industry_benchmark(industry)
    percentile = round(calculate_percentile(visibility, benchmark['avgVisibility'], benchmark['topPerformerVisibility']))
    quality_percentile = round(calculate_percentile(quality_score * 10, benchmark['avgMentionQuality'] * 10, 90))
    
    if percentile >= 90:
        position_text, position_class = 'Industry Leader', 'excellent'
    elif percentile >= 70:
        position_text, position_class = 'Above Average', 'good'
    elif percentile >= 50:
        position_text, position_class = 'Average', 'fair'
    elif percentile >= 30:
        position_text, position_class = 'Below Average', 'poor'
    else:
        position_text, position_class = 'Needs Improvement', 'poor'
    
    gap_to_top = max(0, benchmark['topPerformerVisibility'] - visibility)
    percentile_str = format_ordinal(percentile)
    
    default_note = ''
    if benchmark.get('isDefault'):
        default_note = f'<p class="text-muted text-sm" style="margin-top: 8px; font-style: italic;">Note: Using general industry benchmarks. Run company analysis for more accurate comparison.</p>'
    
    return f"""
    <div class="section industry-benchmark">
      <h2 class="section-title">
        <span class="icon">{ICONS['chartBar']}</span>
        Industry Position: {escape_html(benchmark['matchedIndustry'])}
      </h2>
      
      <div class="benchmark-summary">
        <div class="benchmark-position">
          <div class="percentile-badge {position_class}">
            <span class="percentile-value">{percentile_str}</span>
            <span class="percentile-label">Percentile</span>
          </div>
          <div class="position-text {position_class}">{position_text}</div>
        </div>
        
        <div class="benchmark-context">
          <p class="benchmark-description">
            {escape_html(client_name)} ranks in the <strong>{percentile_str} percentile</strong> for AI visibility 
            in the {escape_html(benchmark['matchedIndustry'])} industry.
            {'To reach top performer status, you need to increase visibility by <strong>' + f'{gap_to_top:.1f} percentage points</strong>.' if gap_to_top > 0 else "Congratulations! You're performing at or above top performer level."}
          </p>
          {default_note}
        </div>
      </div>
      
      <div class="benchmark-comparison">
        <h3 class="subsection-title">Visibility Comparison</h3>
        <div class="benchmark-bars">
          <div class="benchmark-bar-row">
            <div class="bar-label">{escape_html(client_name)}</div>
            <div class="bar-container">
              <div class="bar client-bar" style="width: {min(100, visibility)}%"></div>
              <span class="bar-value">{format_number(visibility)}%</span>
            </div>
          </div>
          <div class="benchmark-bar-row">
            <div class="bar-label">Industry Average</div>
            <div class="bar-container">
              <div class="bar avg-bar" style="width: {min(100, benchmark['avgVisibility'])}%"></div>
              <span class="bar-value">{format_number(benchmark['avgVisibility'])}%</span>
            </div>
          </div>
          <div class="benchmark-bar-row">
            <div class="bar-label">Top Performers</div>
            <div class="bar-container">
              <div class="bar top-bar" style="width: {min(100, benchmark['topPerformerVisibility'])}%"></div>
              <span class="bar-value">{format_number(benchmark['topPerformerVisibility'])}%</span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="benchmark-metrics">
        <div class="metric-item">
          <div class="metric-label">Visibility Percentile</div>
          <div class="metric-value {position_class}">{percentile_str}</div>
        </div>
        <div class="metric-item">
          <div class="metric-label">Quality Percentile</div>
          <div class="metric-value {'good' if quality_percentile >= 70 else 'fair' if quality_percentile >= 50 else 'poor'}">{format_ordinal(quality_percentile)}</div>
        </div>
        <div class="metric-item">
          <div class="metric-label">Gap to Top</div>
          <div class="metric-value {'excellent' if gap_to_top == 0 else 'good' if gap_to_top <= 15 else 'fair' if gap_to_top <= 30 else 'poor'}">
            {'✓ At Top' if gap_to_top == 0 else f'+{gap_to_top:.1f}pp needed'}
          </div>
        </div>
      </div>
    </div>
    """

def build_platform_breakdown(data: HtmlReportData) -> str:
    """Build platform breakdown section"""
    platform_stats = data.get('canvasData', {}).get('mentionsCheck', {}).get('platformStats', {})
    
    platform_configs = {
        'chatgpt': {'name': 'ChatGPT', 'logo': ICONS.get('chatgpt', '🤖')},
        'perplexity': {'name': 'Perplexity', 'logo': ICONS.get('perplexity', '🔍')},
        'claude': {'name': 'Claude', 'logo': ICONS.get('claude', '🧠')},
        'gemini': {'name': 'Gemini', 'logo': ICONS.get('gemini', '✨')},
        'mistral': {'name': 'Mistral', 'logo': ICONS.get('mistral', '⚡')},
    }
    
    active_platforms = [k for k in platform_stats.keys() if k.lower() in platform_configs]
    
    if not active_platforms:
        return ''
    
    platform_cards = []
    for key in active_platforms:
        config = platform_configs[key.lower()]
        stats = platform_stats[key]
        responses = stats.get('responses', 1)
        visibility = min(100, round((stats.get('mentions', 0) / responses) * 100))
        score_class = get_score_class(visibility, 60, 40, 20)
        
        platform_cards.append(f"""
          <div class="platform-card">
            <div class="platform-icon">{config['logo']}</div>
            <div class="platform-name">{config['name']}</div>
            <div class="platform-value score-{score_class}">{visibility}%</div>
            <div class="platform-label">{stats.get('mentions', 0)} mentions</div>
          </div>
        """)
    
    return f"""
    <div class="section">
      <h2 class="section-title">
        <span class="icon">{ICONS['cursorArrowRays']}</span>
        Platform Breakdown
      </h2>
      <div class="platform-grid">
        {''.join(platform_cards)}
      </div>
    </div>
    """

def build_competitor_comparison(data: HtmlReportData) -> str:
    """Build competitor comparison section"""
    canvas_data = data.get('canvasData', {})
    client_name = data.get('clientName', '')
    mentions = canvas_data.get('mentionsCheck', {}).get('chatgptPresence', 0)
    
    platform_stats = canvas_data.get('mentionsCheck', {}).get('platformStats', {})
    num_platforms = len(platform_stats) or 2
    num_queries = canvas_data.get('mentionsCheck', {}).get('numQueries', 10)
    total_checks = num_queries * num_platforms
    
    visibility = canvas_data.get('mentionsCheck', {}).get('visibility', min(100, round((mentions / max(total_checks, 1)) * 100)))
    
    rows = [CompetitorRow({
        'name': client_name,
        'mentions': mentions,
        'visibility': visibility,
        'isClient': True,
    })]
    
    competitors = canvas_data.get('competitors', [])
    if competitors:
        for comp in competitors:
            rows.append(CompetitorRow({
                'name': comp.get('name', ''),
                'mentions': comp.get('mentions', 0),
                'visibility': comp.get('visibility', 0),
            }))
    else:
        rows.append(f"""
          <tr>
            <td colspan="3" style="text-align: center; color: var(--text-muted); padding: 24px;">
              <div style="font-weight: 500; margin-bottom: 8px;">No competitor data available</div>
              <div style="font-size: 12px;">
                Competitor mentions are extracted from AI responses during mentions checks.
                Run more queries to discover who's competing for visibility in your space.
              </div>
            </td>
          </tr>
        """)
    
    return f"""
    <div class="section">
      <h2 class="section-title">
        <span class="icon">{ICONS['users']}</span>
        Competitor Comparison
      </h2>
      <p class="text-muted text-sm mb-md">
        How often each company is mentioned across {total_checks} AI responses
      </p>
      <table class="data-table">
        <thead>
          <tr>
            <th>Company</th>
            <th class="numeric">Mentions</th>
            <th>Presence Rate</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </div>
    """

def build_query_insights(data: HtmlReportData) -> str:
    """Build query insights section (highlights & opportunities)"""
    insights = data.get('queryInsights')
    
    def get_dimension_display(raw_dim: str) -> str:
        dim = (raw_dim or '').lower()
        if dim in ['recommendations', 'evaluation', 'feature-specific', 'use-case', 'problem-solution', 'commercial']:
            return 'commercial'
        if dim == 'competitive':
            return 'competitive'
        if dim == 'branded':
            return 'branded'
        return 'informational'
    
    highlights_content = ''
    highlights = insights.get('highlights', []) if insights else []
    if highlights:
        highlights_content = ''.join([
            f"""
            <div class="insight-item">
              <div class="query">
                "{escape_html(h['query'])}"
                <span class="platform">— {escape_html(h.get('platform', ''))}</span>
              </div>
              <div class="response">"{escape_html(h.get('responseExcerpt', ''))}"</div>
              <span class="opportunity-tag {get_dimension_display(h.get('dimension', ''))}">{get_dimension_display(h.get('dimension', ''))}</span>
            </div>
            """ for h in highlights
        ])
    else:
        highlights_content = '<div class="insight-item"><p class="text-muted text-italic">No highlights available yet. Run more queries to see where you\'re performing well.</p></div>'
    
    lowlight_titles = {
        'missed': 'Missed Opportunities',
        'platform_gap': 'Platform Coverage Gaps',
        'weak_mention': 'Mentions Need Improvement',
        'competitor_win': 'Competitor Advantages',
    }
    
    opportunities_title = 'Opportunities to Improve'
    opportunities_content = ''
    
    lowlights = insights.get('lowlights', []) if insights else []
    if lowlights:
        lowlight_type = insights.get('lowlightType', 'missed')
        opportunities_title = lowlight_titles.get(lowlight_type, 'Missed Opportunities')
        opportunities_content = ''.join([
            f"""
            <div class="insight-item">
              <div class="query">"{escape_html(l.get('query', ''))}"{' — <span class="platform">' + ', '.join(l.get('platformsChecked', [])) + '</span>' if l.get('platformsChecked') else ''}</div>
              <div class="reason">{escape_html(l.get('reason', ''))}</div>
              {'<div class="response">"' + escape_html(l.get('responseExcerpt', '')) + '"</div>' if l.get('responseExcerpt') else ''}
              <span class="opportunity-tag {l.get('opportunityType', '')}">{l.get('opportunityType', '')}</span>
            </div>
            """ for l in lowlights
        ])
    else:
        opportunities_content = '<div class="insight-item"><div class="query" style="color: var(--color-success);">Featured in all tested queries</div><p class="text-muted text-italic">Excellent visibility - mentioned prominently across all AI platforms. Focus on maintaining this position.</p></div>'
    
    return f"""
    <div class="section">
      <h2 class="section-title">
        <span class="icon">{ICONS['lightBulb']}</span>
        Query Insights
      </h2>
      <div class="insight-cards">
        <div class="insight-card highlight">
          <div class="card-header">
            <span class="icon">{ICONS['checkCircle']}</span>
            <h4>Where You Shine</h4>
          </div>
          {highlights_content}
        </div>
        <div class="insight-card lowlight">
          <div class="card-header">
            <span class="icon">{ICONS['exclamationTriangle']}</span>
            <h4>{opportunities_title}</h4>
          </div>
          {opportunities_content}
        </div>
      </div>
    </div>
    """

def build_technical_metrics(data: HtmlReportData) -> str:
    """Build technical metrics section"""
    insights = data.get('queryInsights')
    canvas_data = data.get('canvasData', {})
    health = canvas_data.get('aeoHealthCheck', {})
    
    category_score = insights.get('categoryClarity') if insights else health.get('categoryClarityScore', 0)
    entity_score = insights.get('entityStrength') if insights else health.get('entityStrengthScore', 0)
    authority_score = health.get('authoritySignalScore', 0)
    
    metrics_html = ''.join([
        MetricRow({
            'label': 'Category Clarity',
            'value': category_score,
            'description': 'Does AI correctly classify your business category?',
            'recommendation': 'Add clearer category signals to website' if category_score < 70 else None,
        }),
        MetricRow({
            'label': 'Entity Strength',
            'value': entity_score,
            'description': 'Is your brand recognized as unique?',
            'recommendation': 'Strengthen brand mentions across sources' if entity_score < 70 else None,
        }),
        MetricRow({
            'label': 'Authority Signal',
            'value': authority_score,
            'description': 'Do you have credible backlinks and social proof?',
            'recommendation': 'Build authority through reviews and press' if authority_score < 70 else None,
        }),
    ])
    
    return f"""
    <div class="section">
      <h2 class="section-title">
        <span class="icon">{ICONS['cog']}</span>
        Technical Metrics
      </h2>
      {metrics_html}
    </div>
    """

def build_dimension_breakdown(data: HtmlReportData) -> str:
    """Build dimension breakdown section"""
    insights = data.get('queryInsights')
    if not insights or not insights.get('dimensionStats'):
        return ''
    
    dimension_stats = insights['dimensionStats']
    total_queries = sum(s.get('queries', 0) for s in dimension_stats.values())
    num_platforms = 5
    total_checks = total_queries * num_platforms
    
    dimensions = [
        {'key': 'commercial', 'label': 'Commercial', 'description': '"Best tools", recommendations, features'},
        {'key': 'competitive', 'label': 'Competitive', 'description': '"X vs Y" comparison queries'},
        {'key': 'informational', 'label': 'Informational', 'description': 'ICP targeting, regional, educational'},
        {'key': 'branded', 'label': 'Branded', 'description': 'Direct brand name searches'},
    ]
    
    rows = []
    for dim in dimensions:
        stats = dimension_stats.get(dim['key'])
        if not stats or stats.get('queries', 0) == 0:
            continue
        
        visibility = stats.get('visibility', 0)
        score_class = get_score_class(visibility, 70, 50, 30)
        dim_total_checks = stats.get('queries', 0) * num_platforms
        
        rows.append(f"""
          <tr>
            <td>
              <strong class="text-primary">{dim['label']}</strong>
              <div class="text-xs text-muted">{dim['description']}</div>
            </td>
            <td class="numeric">{stats.get('queries', 0)}</td>
            <td class="numeric" style="color: var(--gray-600);">{dim_total_checks}</td>
            <td class="numeric">{stats.get('mentions', 0)}</td>
            <td>
              <div class="progress-cell">
                <div class="progress-bar">
                  <div class="fill {score_class}" style="width: {visibility}%"></div>
                </div>
                <span class="progress-value">{visibility}%</span>
              </div>
            </td>
          </tr>
        """)
    
    if not rows:
        return ''
    
    return f"""
    <div class="section">
      <h2 class="section-title">
        <span class="icon">{ICONS['chartPie']}</span>
        Performance by Query Type
      </h2>
      <p class="text-muted text-sm mb-md">
        {total_queries} unique prompts tested across {num_platforms} AI platforms ({total_checks} total API checks)
      </p>
      <table class="data-table">
        <thead>
          <tr>
            <th>Query Type</th>
            <th class="numeric">Prompts</th>
            <th class="numeric">API Checks</th>
            <th class="numeric">With Mentions</th>
            <th>Presence Rate</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </div>
    """

def build_quality_distribution(data: HtmlReportData) -> str:
    """Build quality distribution section"""
    insights = data.get('queryInsights')
    if not insights or not insights.get('qualityDistribution'):
        return ''
    
    dist = insights['qualityDistribution']
    total = dist.get('featured', 0) + dist.get('mentioned', 0) + dist.get('brief', 0) + dist.get('notMentioned', 0)
    if total == 0:
        return ''
    
    bars_html = ''.join([
        QualityBar({
            'label': 'Top Recommendation',
            'value': dist.get('featured', 0),
            'total': total,
            'color': 'var(--color-success)',
        }),
        QualityBar({
            'label': 'Detailed',
            'value': dist.get('mentioned', 0),
            'total': total,
            'color': 'var(--color-info)',
        }),
        QualityBar({
            'label': 'Brief',
            'value': dist.get('brief', 0),
            'total': total,
            'color': 'var(--color-warning)',
        }),
        QualityBar({
            'label': 'Not Mentioned',
            'value': dist.get('notMentioned', 0),
            'total': total,
            'color': 'var(--color-danger)',
        }),
    ])
    
    good_mentions = dist.get('featured', 0) + dist.get('mentioned', 0)
    good_pct = round((good_mentions / total) * 100) if total > 0 else 0
    
    return f"""
    <div class="section">
      <h2 class="section-title">
        <span class="icon">{ICONS['sparkles']}</span>
        Mention Quality
      </h2>
      <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
        {good_pct}% high-quality mentions (detailed or recommended)
      </p>
      {bars_html}
    </div>
    """

def build_top_opportunities(data: HtmlReportData) -> str:
    """Build top opportunities section"""
    insights = data.get('queryInsights')
    if not insights or not insights.get('topOpportunities'):
        return ''
    
    top_opportunities = insights['topOpportunities']
    if not top_opportunities:
        return ''
    
    rows = []
    for idx, opp in enumerate(top_opportunities):
        competitor_badges = ''
        if opp.get('competitorsMentioned'):
            competitor_badges = ''.join([
                f'<span class="tag-danger">{escape_html(c)}</span>'
                for c in opp['competitorsMentioned']
            ])
        else:
            competitor_badges = '<span style="color: var(--gray-500); font-size: 11px;">—</span>'
        
        platforms_display = ''
        if opp.get('platforms'):
            platforms_display = ''.join([
                f'<span class="platform-badge">{escape_html(p)}</span>'
                for p in opp['platforms']
            ])
        else:
            platforms_display = '<span style="color: var(--gray-500); font-size: 11px;">—</span>'
        
        rows.append(f"""
          <tr>
            <td style="font-weight: 500; color: var(--gray-50);">{idx + 1}. "{escape_html(opp.get('query', ''))}"</td>
            <td><span class="opportunity-tag {opp.get('dimension', '')}">{opp.get('dimension', '')}</span></td>
            <td>{platforms_display}</td>
            <td>{competitor_badges}</td>
            <td style="font-size: 12px; color: var(--gray-400);">{escape_html(opp.get('whyItMatters', ''))}</td>
          </tr>
        """)
    
    return f"""
    <div class="section">
      <h2 class="section-title">
        <span class="icon">{ICONS['rocketLaunch']}</span>
        Top Opportunities to Target
      </h2>
      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 25%;">Query</th>
            <th>Type</th>
            <th>Platforms</th>
            <th>Competitors</th>
            <th style="width: 25%;">Why It Matters</th>
          </tr>
        </thead>
        <tbody>
          {''.join(rows)}
        </tbody>
      </table>
    </div>
    """

def build_priority_actions(data: HtmlReportData) -> str:
    """Build Priority Actions section"""
    insights = data.get('queryInsights')
    health = data.get('canvasData', {}).get('aeoHealthCheck', {})
    
    actions = []
    
    # Action 1: Based on worst non-branded dimension
    if insights and insights.get('dimensionStats'):
        dimension_stats = insights['dimensionStats']
        dimensions = [
            {'key': 'commercial', 'label': 'commercial queries', 'stats': dimension_stats.get('commercial', {})},
            {'key': 'competitive', 'label': 'comparison queries', 'stats': dimension_stats.get('competitive', {})},
            {'key': 'informational', 'label': 'informational queries', 'stats': dimension_stats.get('informational', {})},
        ]
        dimensions = [d for d in dimensions if d['stats'].get('queries', 0) > 0]
        
        if dimensions:
            worst_dim = sorted(dimensions, key=lambda x: x['stats'].get('visibility', 0))[0]
            if worst_dim['stats'].get('visibility', 0) < 60:
                example_opp = None
                if insights.get('topOpportunities'):
                    for opp in insights['topOpportunities']:
                        opp_dim = (opp.get('dimension') or '').lower()
                        if (opp_dim == worst_dim['key'] or
                            (worst_dim['key'] == 'commercial' and opp_dim in ['recommendations', 'evaluation', 'feature-specific'])):
                            example_opp = opp
                            break
                
                example = None
                if example_opp:
                    query = example_opp.get('query', '')
                    example = f'Target: "{query[:50]}{"..." if len(query) > 50 else ""}"'
                
                actions.append({
                    'title': f"Improve {worst_dim['label']}",
                    'reason': f"Only {worst_dim['stats'].get('visibility', 0)}% visibility on {worst_dim['label']} — these drive buying decisions",
                    'example': example,
                    'urgent': worst_dim['stats'].get('visibility', 0) < 30,
                })
    
    # Action 2: Based on competitor beating us
    competitor_gap = None
    if insights and insights.get('topOpportunities'):
        for opp in insights['topOpportunities']:
            if opp.get('competitorsMentioned'):
                competitor_gap = opp
                break
    
    if competitor_gap:
        competitor = competitor_gap['competitorsMentioned'][0]
        query_short = competitor_gap.get('query', '')
        if len(query_short) > 45:
            query_short = query_short[:42] + '...'
        
        actions.append({
            'title': f'Outrank {competitor}',
            'reason': f'They\'re mentioned on "{query_short}" — you\'re not',
            'example': competitor_gap.get('whyItMatters'),
            'urgent': True,
        })
    
    # Action 3: Based on technical metrics
    category_score = health.get('categoryClarityScore', 100)
    entity_score = health.get('entityStrengthScore', 100)
    
    if category_score < 70:
        actions.append({
            'title': 'Clarify your category',
            'reason': f'AI is {100 - category_score}% unsure what category you\'re in — this hurts discovery',
            'example': 'Add clear category signals to your homepage and About page',
            'urgent': category_score < 50,
        })
    elif entity_score < 70:
        actions.append({
            'title': 'Strengthen brand recognition',
            'reason': 'Your brand name isn\'t strongly recognized — AI might confuse you with others',
            'example': 'Ensure consistent brand naming across all online sources',
            'urgent': entity_score < 50,
        })
    
    # If less than 3 actions, add generic ones
    if len(actions) < 3 and insights and insights.get('qualityDistribution'):
        quality_dist = insights['qualityDistribution']
        not_mentioned = quality_dist.get('notMentioned', 0)
        total = (not_mentioned + quality_dist.get('brief', 0) +
                quality_dist.get('mentioned', 0) + quality_dist.get('featured', 0))
        missed_pct = round((not_mentioned / total) * 100) if total > 0 else 0
        
        if missed_pct > 30:
            actions.append({
                'title': 'Expand content coverage',
                'reason': f'You\'re missing from {missed_pct}% of queries — more authoritative content needed',
                'example': 'Create in-depth guides targeting your key use cases',
                'urgent': missed_pct > 50,
            })
    
    if not actions:
        return f"""
        <div class="section">
          <h2 class="section-title">
            <span class="icon">{ICONS['clipboardList']}</span>
            Priority Actions
          </h2>
          <p style="font-size: 13px; color: var(--text-muted);">
            Your AI visibility is solid. Focus on maintaining your presence and monitoring competitors.
          </p>
        </div>
        """
    
    action_items = ''.join([
        ActionItem({
            'number': idx + 1,
            'title': action['title'],
            'reason': action['reason'],
            'example': action.get('example'),
        })
        for idx, action in enumerate(actions[:3])
    ])
    
    return f"""
    <div class="section">
      <h2 class="section-title">
        <span class="icon">{ICONS['clipboardList']}</span>
        Priority Actions
      </h2>
      {action_items}
    </div>
    """

def build_executive_tldr(data: HtmlReportData) -> str:
    """Build Executive TL;DR section - 30-second glanceable summary"""
    canvas_data = data.get('canvasData', {})
    visibility = canvas_data.get('mentionsCheck', {}).get('visibility', 0)
    insights = data.get('queryInsights')
    competitors = canvas_data.get('competitors', [])
    
    if visibility >= 60:
        verdict, verdict_class = 'Strong Foundation', 'excellent'
    elif visibility >= 40:
        verdict, verdict_class = 'Growing Presence', 'good'
    elif visibility >= 20:
        verdict, verdict_class = 'Needs Work', 'warning'
    else:
        verdict, verdict_class = 'Invisible to AI', 'danger'
    
    competitor_gaps = 0
    if insights and insights.get('topOpportunities'):
        competitor_gaps = len([opp for opp in insights['topOpportunities'] if opp.get('competitorsMentioned')])
    
    top_win = insights.get('highlights', [{}])[0] if insights and insights.get('highlights') else {}
    top_win_display = top_win.get('query', 'No strong wins yet')
    top_win_context = f"via {top_win.get('platform', '')}" if top_win.get('platform') else 'Run more queries'
    
    top_loss = (insights.get('lowlights', [{}])[0] if insights and insights.get('lowlights') else None) or (insights.get('topOpportunities', [{}])[0] if insights and insights.get('topOpportunities') else {})
    top_loss_display = top_loss.get('query', 'No major gaps found') if top_loss else 'No major gaps found'
    top_loss_context = ''
    if top_loss and top_loss.get('competitorsMentioned'):
        top_loss_context = f"{top_loss['competitorsMentioned'][0]} mentioned instead"
    elif top_loss:
        top_loss_context = 'Opportunity to capture'
    
    top_competitor = next((c for c in competitors if c.get('visibility', 0) > visibility), None)
    
    return f"""
    <div class="section-primary tldr-section">
      <h2 class="section-title">
        <span class="icon">{ICONS['bolt']}</span>
        30-Second Summary
      </h2>
      <table class="tldr-table">
        <tr>
          <td class="tldr-label">Your AI Visibility</td>
          <td class="tldr-value">{format_number(visibility)}%</td>
          <td class="tldr-context">
            <span class="tldr-badge {verdict_class}">{verdict}</span>
          </td>
        </tr>
        <tr>
          <td class="tldr-label">Competitors Beating You</td>
          <td class="tldr-value score-{'poor' if competitor_gaps > 0 else 'good'}">{competitor_gaps}</td>
          <td class="tldr-context">
            {'On high-value queries' + (f' ({escape_html(top_competitor["name"])} leads)' if top_competitor else '') if competitor_gaps > 0 else 'You are holding your ground'}
          </td>
        </tr>
        <tr>
          <td class="tldr-label">Biggest Win</td>
          <td class="tldr-value" style="font-size: 14px; font-weight: 500;">"{escape_html(top_win_display)}"</td>
          <td class="tldr-context">{escape_html(top_win_context)}</td>
        </tr>
        <tr>
          <td class="tldr-label">Biggest Gap</td>
          <td class="tldr-value" style="font-size: 14px; font-weight: 500; color: var(--color-danger);">"{escape_html(top_loss_display)}"</td>
          <td class="tldr-context">{escape_html(top_loss_context)}</td>
        </tr>
      </table>
    </div>
    """

def build_shock_opener(data: HtmlReportData) -> str:
    """Build shock opener section - shows most impactful missed opportunity"""
    insights = data.get('queryInsights')
    client_name = data.get('clientName', '').lower()
    canvas_data = data.get('canvasData', {})
    visibility = canvas_data.get('mentionsCheck', {}).get('visibility', 0)
    
    def is_irrelevant_comparison(query: str) -> bool:
        lower_query = query.lower()
        if ' vs ' not in lower_query and ' versus ' not in lower_query:
            return False
        return client_name not in lower_query
    
    valid_opportunities = []
    if insights and insights.get('topOpportunities'):
        valid_opportunities = [
            opp for opp in insights['topOpportunities']
            if opp.get('competitorsMentioned') and not is_irrelevant_comparison(opp.get('query', ''))
        ]
    
    if valid_opportunities:
        valid_opportunities.sort(key=lambda x: len(x.get('query', '')) + (x.get('query', '').count(',') * 20))
        shock_opp = valid_opportunities[0]
        competitor = shock_opp['competitorsMentioned'][0]
        query = shock_opp.get('query', '')
        
        return f"""
        <div class="shock-card">
          <div class="shock-label">
            {ICONS['fire']}
            Key Finding
          </div>
          <div class="shock-query">
            Query: "{escape_html(query)}"
          </div>
          <div class="shock-main">
            Mentioned: <span class="shock-competitor">{escape_html(competitor)}</span> (not you)
          </div>
          <div class="shock-context">
            {f'{len(shock_opp["competitorsMentioned"])} competitors in this response.' if len(shock_opp.get('competitorsMentioned', [])) > 1 else ''}
          </div>
        </div>
        """
    elif visibility < 50:
        return f"""
        <div class="shock-card">
          <div class="shock-label">
            {ICONS['fire']}
            Key Finding
          </div>
          <div class="shock-main">
            AI visibility: <span class="shock-competitor">{visibility}%</span> of relevant queries
          </div>
        </div>
        """
    return ''

def build_content_strategy(data: HtmlReportData) -> str:
    """Build Content Architecture section"""
    strategy = data.get('contentStrategy')
    if not strategy or not strategy.get('pillars'):
        return f"""
        <div class="section">
          <h2 class="section-title">
            <span class="icon">{ICONS['bookOpen']}</span>
            Content Architecture
          </h2>
          <div class="empty-state">
            <div class="empty-state-icon">📝</div>
            <div class="empty-state-title">Content Strategy Not Available</div>
            <div class="empty-state-text">
              Run company analysis to auto-generate a content strategy based on your
              pain points, use cases, and product offerings.
            </div>
          </div>
        </div>
        """
    
    pillars = strategy.get('pillars', [])
    priority_content = strategy.get('priorityContent', [])
    
    pillars_rows = ''.join([
        f"""
        <tr>
          <td>
            <strong>{escape_html(p.get('name', ''))}</strong>
            <div class="text-xs text-muted">{escape_html(p.get('subtitle', ''))}</div>
          </td>
          <td style="color: var(--gray-400);">{', '.join([escape_html(c) for c in p.get('clusters', [])])}</td>
        </tr>
        """ for p in pillars
    ])
    
    content_rows = ''.join([
        f"""
        <tr>
          <td>
            <strong>{escape_html(c.get('title', ''))}</strong>
            <div class="text-xs text-muted">{escape_html(c.get('description', ''))}</div>
          </td>
          <td class="numeric">{escape_html(c.get('wordCount', ''))}</td>
          <td><span class="status {get_priority_class(c.get('priority', ''))}">{escape_html(c.get('priority', ''))}</span></td>
          <td style="color: var(--gray-400);">{', '.join([escape_html(s) for s in c.get('schema', [])])}</td>
        </tr>
        """ for c in priority_content
    ])
    
    return f"""
    <div class="section">
      <h2 class="section-title">
        <span class="icon">{ICONS['bookOpen']}</span>
        Content Architecture
      </h2>
      <p style="color: var(--gray-400); margin-bottom: 24px;">
        Strategic content structure built around topic clusters to establish category authority and improve AI visibility.
      </p>
      <h3 style="color: var(--gray-200); font-size: 14px; margin-bottom: 12px; font-weight: 500;">Pillar & Cluster Model</h3>
      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 30%;">Pillar Topic</th>
            <th>Clusters</th>
          </tr>
        </thead>
        <tbody>
          {pillars_rows}
        </tbody>
      </table>
      {f'''
        <h3 style="color: var(--gray-200); font-size: 14px; margin: 24px 0 12px 0; font-weight: 500;">Priority Content Pieces</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 40%;">Article</th>
              <th class="numeric">Words</th>
              <th>Priority</th>
              <th>Schema</th>
            </tr>
          </thead>
          <tbody>
            {content_rows}
          </tbody>
        </table>
      ''' if priority_content else ''}
      {f'''
        <p style="color: var(--gray-500); font-size: 12px; margin-top: 16px;">
          Monthly capacity: {escape_html(strategy.get('monthlyCapacity', ''))}
        </p>
      ''' if strategy.get('monthlyCapacity') else ''}
    </div>
    """


# Simon Wilhelm photo (base64 encoded)
SIMON_PHOTO_BASE64 = 'data:image/jpeg;base64,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ICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAg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'

def build_book_strategy_session(data: HtmlReportData) -> str:
    """Build Book Strategy Session CTA section"""
    default_cta = {
        'name': 'Simon Wilhelm',
        'title': 'Co-Founder, SCAILE',
        'description': f"Let's discuss how SCAILE can help {data.get('clientName', '')} dominate AI search visibility.",
        'calendlyLink': 'https://calendly.com/scaile/strategy',
        'linkedinLink': 'https://linkedin.com/in/simonwilhelm',
        'photoBase64': SIMON_PHOTO_BASE64,
    }
    cta = {**default_cta, **(data.get('ctaConfig') or {})}
    
    return f"""
    <div class="section cta-block" style="text-align: center;">
      <h2 class="section-title" style="justify-content: center;">
        <span class="icon">{ICONS['calendar']}</span>
        Book Your Strategy Session
      </h2>
      <div class="cta-block" style="margin-top: 24px;">
        {f'<img src="{escape_html(cta.get("photoBase64", ""))}" alt="{escape_html(cta["name"])}" class="avatar" />' if cta.get('photoBase64') else ''}
        <div style="color: var(--gray-50); font-weight: 500; font-size: 16px;">{escape_html(cta['name'])}</div>
        <div style="color: var(--gray-400); font-size: 13px; margin-bottom: 16px;">{escape_html(cta['title'])}</div>
        <p style="color: var(--gray-400); font-size: 14px; max-width: 500px; margin: 0 auto 24px;">
          {escape_html(cta['description'])}
        </p>
        <div class="flex flex-center flex-wrap gap-md">
          <a href="{escape_html(cta['calendlyLink'])}" target="_blank" class="btn-primary">
            {ICONS['calendar']}
            Schedule a Call
          </a>
          {f'''
            <a href="{escape_html(cta['linkedinLink'])}" target="_blank" class="btn-secondary">
              🔗
              Connect on LinkedIn
            </a>
          ''' if cta.get('linkedinLink') else ''}
        </div>
      </div>
    </div>
    """

def build_what_this_means(data: HtmlReportData) -> str:
    """Build What This Means section - matches TypeScript exactly"""
    canvas_data = data.get('canvasData', {})
    visibility = canvas_data.get('mentionsCheck', {}).get('visibility', 0)
    insights = data.get('queryInsights')
    competitors = canvas_data.get('competitors', [])
    
    top_competitor = next((c for c in competitors if c.get('visibility', 0) > visibility), None)
    competitor_gap = (top_competitor.get('visibility', 0) - visibility) if top_competitor else 0
    missed_opportunities = len(insights.get('topOpportunities', [])) if insights else 0
    
    if visibility < 20:
        impact_level = 'critical'
        impact_message = 'Low AI visibility'
        impact_context = 'You appear in less than 20% of relevant AI queries. Competitors are mentioned significantly more often.'
    elif visibility < 40:
        impact_level = 'significant'
        impact_message = 'Below average AI visibility'
        impact_context = 'Competitors appear in AI responses more frequently. There is significant room for improvement.'
    elif visibility < 60:
        impact_level = 'moderate'
        impact_message = 'Moderate AI visibility'
        impact_context = 'You have a foundation, but competitors still appear more often on key commercial queries.'
    else:
        impact_level = 'low'
        impact_message = 'Strong AI visibility'
        impact_context = 'You appear in the majority of relevant AI queries. Focus on maintaining position and closing remaining gaps.'
    
    impact_color = {
        'critical': 'var(--color-danger)',
        'significant': 'var(--color-warning)',
        'moderate': 'var(--color-primary)',
        'low': 'var(--color-success)',
    }[impact_level]
    
    gap_card = f'''
      <div class="metric-card">
        <div class="metric-label">Gap to Leader</div>
        <div class="metric-value" style="color: var(--color-warning);">+{format_number(competitor_gap)}pp</div>
        <div class="metric-context">{escape_html(top_competitor.get('name', ''))} is {format_number(competitor_gap)} points ahead</div>
      </div>
    ''' if top_competitor else ''
    
    return f"""
    <h2 class="section-title">
      <span class="icon">{ICONS['lightBulb']}</span>
      What This Means for Your Business
    </h2>
    
    <div style="padding: 24px; background: var(--bg-secondary); border-radius: var(--border-radius); border-left: 4px solid {impact_color}; margin-bottom: 24px;">
      <h3 style="margin: 0 0 12px 0; color: var(--text-primary);">{escape_html(impact_message)}</h3>
      <p style="margin: 0; color: var(--text-secondary); line-height: 1.6;">{escape_html(impact_context)}</p>
    </div>
    
    <div class="metric-grid" style="margin-bottom: 24px;">
      <div class="metric-card">
        <div class="metric-label">Missed Queries</div>
        <div class="metric-value" style="color: var(--color-danger);">{missed_opportunities}</div>
        <div class="metric-context">Queries where competitors appear instead of you</div>
      </div>
      {gap_card}
    </div>
    """

def build_competitive_position(data: HtmlReportData) -> str:
    """Build Competitive Position section - matches TypeScript exactly"""
    canvas_data = data.get('canvasData', {})
    client_name = data.get('clientName', '')
    visibility = canvas_data.get('mentionsCheck', {}).get('visibility', 0)
    competitors = canvas_data.get('competitors', [])
    insights = data.get('queryInsights')
    
    # Sort competitors by visibility
    sorted_competitors = sorted(competitors, key=lambda c: c.get('visibility', 0), reverse=True)
    
    # Find your rank
    all_players = [
        {'name': client_name, 'visibility': visibility, 'isYou': True},
    ] + [{'name': c.get('name', ''), 'visibility': c.get('visibility', 0), 'isYou': False} for c in sorted_competitors]
    all_players.sort(key=lambda p: p['visibility'], reverse=True)
    
    your_rank = next((i+1 for i, p in enumerate(all_players) if p['isYou']), len(all_players))
    total_players = len(all_players)
    
    # Get key competitive insights
    competitor_wins = [opp for opp in (insights.get('topOpportunities', []) if insights else []) if opp.get('competitorsMentioned')]
    
    # Count which competitors appear most
    competitor_mentions = {}
    for opp in competitor_wins:
        for comp in opp.get('competitorsMentioned', []):
            competitor_mentions[comp] = competitor_mentions.get(comp, 0) + 1
    
    top_threats = sorted(competitor_mentions.items(), key=lambda x: x[1], reverse=True)[:3]
    
    leaderboard_html = ''.join([
        f'''
            <div style="display: flex; align-items: center; gap: 12px; padding: 8px 12px; background: {'rgba(99, 102, 241, 0.15)' if player['isYou'] else 'transparent'}; border-radius: var(--border-radius-sm); {'border: 1px solid var(--color-primary);' if player['isYou'] else ''}">
              <div style="font-weight: 600; color: {'var(--color-success)' if idx == 0 else 'var(--text-secondary)'}; width: 24px;">#{idx + 1}</div>
              <div style="flex: 1; color: var(--text-primary); {'font-weight: 600;' if player['isYou'] else ''}">{escape_html(player['name'])} {'(You)' if player['isYou'] else ''}</div>
              <div style="font-weight: 500; color: {'var(--color-success)' if player['visibility'] >= 50 else 'var(--color-warning)' if player['visibility'] >= 30 else 'var(--color-danger)'};">{format_number(player['visibility'])}%</div>
            </div>
        '''
        for idx, player in enumerate(all_players[:5])
    ])
    
    threats_html = f'''
    <div style="padding: 20px; background: rgba(239, 68, 68, 0.1); border-radius: var(--border-radius); border-left: 4px solid var(--color-danger);">
      <h4 style="margin: 0 0 12px 0; color: var(--text-primary);">⚠️ Top Competitive Threats</h4>
      <p style="margin: 0; color: var(--text-secondary);">
        {' • '.join([f"<strong>{escape_html(name)}</strong> appears instead of you on {count} quer{'y' if count == 1 else 'ies'}" for name, count in top_threats])}
      </p>
    </div>
    ''' if top_threats else ''
    
    rank_color = 'var(--color-success)' if your_rank <= 2 else 'var(--color-warning)' if your_rank <= 3 else 'var(--color-danger)'
    
    return f"""
    <h2 class="section-title">
      <span class="icon">{ICONS['trophy']}</span>
      Your Competitive Position
    </h2>
    
    <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 24px; margin-bottom: 24px;">
      <div style="padding: 24px; background: var(--bg-secondary); border-radius: var(--border-radius); text-align: center;">
        <div style="font-size: 48px; font-weight: 700; color: {rank_color};">
          #{your_rank}
        </div>
        <div style="color: var(--text-secondary); margin-top: 8px;">of {total_players} in your space</div>
      </div>
      
      <div style="padding: 24px; background: var(--bg-secondary); border-radius: var(--border-radius);">
        <h4 style="margin: 0 0 16px 0; color: var(--text-primary);">Leaderboard</h4>
        <div style="display: flex; flex-direction: column; gap: 12px;">
          {leaderboard_html}
        </div>
      </div>
    </div>
    
    {threats_html}
    """

def build_aeo_report_html(data: HtmlReportData) -> str:
    """Main function to build complete AEO report HTML"""
    client_name = data.get('clientName', '')
    website_url = data.get('websiteUrl', '')
    logo_url = data.get('logoUrl', '')
    generated_at = data.get('generatedAt') or datetime.now()
    theme = data.get('theme', 'dark')
    
    date_str = generated_at.strftime('%B %d, %Y')
    styles = get_styles()
    
    canvas_data = data.get('canvasData', {})
    visibility = canvas_data.get('mentionsCheck', {}).get('visibility', 0)
    show_shock_opener = visibility < 50
    
    # Build all sections
    shock_opener = build_shock_opener(data) if show_shock_opener else ''
    executive_tldr = build_executive_tldr(data)
    executive_summary = build_executive_summary(data)
    what_this_means = build_what_this_means(data)
    competitive_position = build_competitive_position(data)
    industry_benchmark = build_industry_benchmark(data)
    example_queries = build_example_queries_section(data)
    methodology_callout = build_methodology_callout()
    platform_breakdown = build_platform_breakdown(data)
    query_insights = build_query_insights(data)
    quality_deep_dive = build_quality_distribution(data)
    priority_actions = build_priority_actions(data)
    dimension_breakdown = build_dimension_breakdown(data)
    top_opportunities = build_top_opportunities(data)
    technical_metrics = build_technical_metrics(data)
    content_strategy = build_content_strategy(data)
    strategy_session = build_book_strategy_session(data)
    
    # Build section groups
    summary_group = f"""
      <div id="section-summary" class="section-group">
        <div class="section-primary">
          {executive_tldr}
        </div>
        <div class="section-primary">
          {executive_summary}
        </div>
        {f'<div class="section-secondary">{industry_benchmark}</div>' if industry_benchmark else ''}
      </div>
    """
    
    impact_group = f"""
      <div id="section-impact" class="section-group">
        <div class="section-primary">
          {what_this_means}
        </div>
        <div class="section-primary">
          {competitive_position}
        </div>
      </div>
    """
    
    findings_group = f"""
      <div id="section-findings" class="section-group">
        <h2 class="section-group-title">Key Findings</h2>
        <div class="section-secondary">
          {platform_breakdown}
        </div>
        <div class="section-secondary">
          {query_insights}
        </div>
      </div>
    """
    
    opportunities_group = f"""
      <div id="section-opportunities" class="section-group">
        <h2 class="section-group-title">Opportunities & Actions</h2>
        {f'<div class="section-secondary">{top_opportunities}</div>' if top_opportunities else ''}
        <div class="section-secondary">
          {priority_actions}
        </div>
      </div>
    """
    
    details_group = f"""
      <div id="section-details" class="section-group">
        <h2 class="section-group-title">Detailed Analysis</h2>
        {f'<div class="section-tertiary">{example_queries}</div>' if example_queries else ''}
        {f'<div class="section-tertiary">{quality_deep_dive}</div>' if quality_deep_dive else ''}
        {f'<div class="section-tertiary">{dimension_breakdown}</div>' if dimension_breakdown else ''}
        {f'<div class="section-tertiary">{technical_metrics}</div>' if technical_metrics else ''}
      </div>
    """
    
    strategy_group = f"""
      <div id="section-strategy" class="section-group">
        <h2 class="section-group-title">Strategy & Methodology</h2>
        {f'<div class="section-secondary">{content_strategy}</div>' if content_strategy else ''}
        <div class="section-tertiary">
          {methodology_callout}
        </div>
      </div>
    """
    
    # Build table of contents
    toc_items = [
        {'title': 'Executive Summary', 'id': 'section-summary'},
        {'title': 'Business Impact', 'id': 'section-impact'},
        {'title': 'Key Findings', 'id': 'section-findings'},
        {'title': 'Opportunities & Actions', 'id': 'section-opportunities'},
        {'title': 'Detailed Analysis', 'id': 'section-details'},
        {'title': 'Strategy & Methodology', 'id': 'section-strategy'},
    ]
    toc = build_table_of_contents({'items': toc_items})
    
    top_cta = ''
    if show_shock_opener and visibility < 30:
        top_cta = f"""
        <div class="section-primary" style="text-align: center; background: var(--color-danger-bg); border: 1px solid var(--color-danger);">
          <h3 style="margin-bottom: 16px;">Ready to Fix This?</h3>
          <p style="margin-bottom: 24px; color: var(--text-secondary);">Book a strategy session to discuss how SCAILE can help you dominate AI search visibility.</p>
          <a href="https://calendly.com/scaile/strategy" target="_blank" class="btn-primary">
            {ICONS['calendar']}
            Schedule a Call
          </a>
        </div>
        """
    
    bg_color = '#ffffff' if theme == 'light' else '#18181b'
    theme_attr = ' data-theme="light"' if theme == 'light' else ''
    
    return f"""<!DOCTYPE html>
<html lang="en"{theme_attr} style="background:{bg_color};margin:0;padding:0;min-height:100%;">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="AEO Analysis Report for {escape_html(client_name)}">
  <title>AEO Analysis Report - {escape_html(client_name)}</title>
  {styles}
  <style>
    html {{ scroll-behavior: smooth; }}
  </style>
</head>
<body style="background:{bg_color};margin:0;padding:0;">
  <div style="position:fixed;top:0;left:0;width:100vw;height:100vh;background:{bg_color};z-index:-9999;print-color-adjust:exact;-webkit-print-color-adjust:exact;"></div>
  <div class="report-wrapper" style="background:{bg_color};position:relative;z-index:1;">
    <div class="report-container">
      <header class="report-header branded">
        <div class="header-brand">
          {f'<img src="{escape_html(logo_url)}" alt="{escape_html(client_name)}" class="header-logo">' if logo_url else f'<div class="logo-placeholder">{escape_html(client_name[0].upper() if client_name else "C")}</div>'}
          <div>
            <div class="header-brand-text">{escape_html(client_name)}</div>
            {f'<div class="header-brand-tagline">{escape_html(website_url)}</div>' if website_url else ''}
          </div>
        </div>
        <div class="header-client">
          <h1>AEO Visibility Report</h1>
          <div class="date">{date_str}</div>
        </div>
      </header>

      <main class="report-content">
        {shock_opener}
        {top_cta}
        {toc}
        {summary_group}
        <hr class="section-group-divider" />
        {impact_group}
        <hr class="section-group-divider" />
        {findings_group}
        <hr class="section-group-divider" />
        {opportunities_group}
        <hr class="section-group-divider" />
        {details_group}
        <hr class="section-group-divider" />
        {strategy_group}
        {strategy_session}
      </main>

      {build_footer({'clientName': client_name})}
    </div>
  </div>
</body>
</html>"""
