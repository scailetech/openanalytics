"""
SCAILE Design System - Reusable Components - Python Port

Production-level component library for consistent UI across all reports.
Each component is a pure function that returns HTML string.
"""

from typing import Literal, Optional
try:
    from .design_system import escape_html, ICONS, get_score_class
except ImportError:
    from design_system import escape_html, ICONS, get_score_class

# ============================================================================
# TYPES
# ============================================================================

StatusColor = Literal['success', 'warning', 'danger', 'info', 'muted']
Size = Literal['sm', 'md', 'lg']

# ============================================================================
# PROGRESS BAR
# ============================================================================

def get_status_color(value: float, thresholds: Optional[dict] = None) -> StatusColor:
    """Get status color based on value thresholds"""
    if thresholds is None:
        thresholds = {'good': 70, 'fair': 50, 'poor': 30}
    if value >= thresholds['good']:
        return 'success'
    if value >= thresholds['fair']:
        return 'info'
    if value >= thresholds['poor']:
        return 'warning'
    return 'danger'


def _get_color_hex(color: StatusColor) -> str:
    """Get hex color for status"""
    colors: dict[StatusColor, str] = {
        'success': '#4ade80',
        'info': '#60a5fa',
        'warning': '#fbbf24',
        'danger': '#f87171',
        'muted': '#71717a',
    }
    return colors.get(color, '#71717a')


def ProgressBar(props: dict) -> str:
    """
    Consistent progress bar component. Accepts dict props like TypeScript.
    
    Example:
        ProgressBar({'value': 75})
        ProgressBar({'value': 30, 'color': 'danger', 'label': 'Category Clarity'})
    """
    value = props.get('value', 0)
    color = props.get('color')
    show_value = props.get('showValue', props.get('show_value', True))
    size = props.get('size', 'md')
    label = props.get('label')
    
    color = color or get_status_color(value)
    color_hex = _get_color_hex(color)
    clamped_value = min(100, max(0, value))
    
    heights: dict[Size, str] = {'sm': '4px', 'md': '8px', 'lg': '12px'}
    height = heights[size]
    
    label_html = f'<span class="ds-progress-label" style="min-width: 100px; font-size: 13px; color: var(--text-secondary);">{escape_html(label)}</span>' if label else ''
    value_html = f'<span class="ds-progress-value" style="min-width: 45px; text-align: right; font-size: 13px; font-weight: 500; color: {color_hex};">{round(clamped_value)}%</span>' if show_value else ''
    
    return f'''
    <div class="ds-progress" style="display: flex; align-items: center; gap: 12px;">
      {label_html}
      <div class="ds-progress-track" style="flex: 1; height: {height}; background: var(--gray-800); border-radius: 4px; overflow: hidden;">
        <div class="ds-progress-fill" style="width: {clamped_value}%; height: 100%; background: {color_hex}; border-radius: 3px; transition: width 0.3s ease;"></div>
      </div>
      {value_html}
    </div>
    '''


# ============================================================================
# BADGE
# ============================================================================

DIMENSION_COLORS: dict[str, dict[str, str]] = {
    'branded': {'bg': 'rgba(96, 165, 250, 0.15)', 'text': '#60a5fa'},
    'competitive': {'bg': 'rgba(248, 113, 113, 0.15)', 'text': '#f87171'},
    'commercial': {'bg': 'rgba(74, 222, 128, 0.15)', 'text': '#4ade80'},
    'informational': {'bg': 'rgba(251, 191, 36, 0.15)', 'text': '#fbbf24'},
    'icp-targeting': {'bg': 'rgba(167, 139, 250, 0.15)', 'text': '#a78bfa'},
    'recommendations': {'bg': 'rgba(45, 212, 191, 0.15)', 'text': '#2dd4bf'},
    'problem-solution': {'bg': 'rgba(251, 146, 60, 0.15)', 'text': '#fb923c'},
    'use-case': {'bg': 'rgba(236, 72, 153, 0.15)', 'text': '#ec4899'},
    'regional': {'bg': 'rgba(34, 211, 238, 0.15)', 'text': '#22d3ee'},
    'industry': {'bg': 'rgba(132, 204, 22, 0.15)', 'text': '#84cc16'},
    'integration': {'bg': 'rgba(168, 162, 158, 0.15)', 'text': '#a8a29e'},
    'technical': {'bg': 'rgba(99, 102, 241, 0.15)', 'text': '#6366f1'},
}


def Badge(
    text: str,
    variant: Literal['default', 'status', 'dimension'] = 'default',
    color: StatusColor | str = 'muted'
) -> str:
    """
    Consistent badge component
    
    Example:
        Badge('Excellent', variant='status', color='success')
        Badge('Branded', variant='dimension', color='branded')
    """
    bg_color = 'var(--badge-bg)'
    text_color = 'var(--text-secondary)'
    
    if variant == 'status' and isinstance(color, str):
        status_colors: dict[str, dict[str, str]] = {
            'success': {'bg': 'rgba(74, 222, 128, 0.15)', 'text': '#4ade80'},
            'warning': {'bg': 'rgba(251, 191, 36, 0.15)', 'text': '#fbbf24'},
            'danger': {'bg': 'rgba(248, 113, 113, 0.15)', 'text': '#f87171'},
            'info': {'bg': 'rgba(96, 165, 250, 0.15)', 'text': '#60a5fa'},
            'muted': {'bg': 'var(--badge-bg)', 'text': 'var(--text-secondary)'},
        }
        colors = status_colors.get(color, status_colors['muted'])
        bg_color = colors['bg']
        text_color = colors['text']
    elif variant == 'dimension' and isinstance(color, str):
        dim_key = color.lower().replace('_', '-').replace(' ', '-')
        colors = DIMENSION_COLORS.get(dim_key, {'bg': 'var(--badge-bg)', 'text': 'var(--text-secondary)'})
        bg_color = colors['bg']
        text_color = colors['text']
    
    return f'<span class="ds-badge" style="display: inline-block; padding: 3px 8px; border-radius: 4px; font-size: 10px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.3px; background: {bg_color}; color: {text_color};">{escape_html(text)}</span>'


# ============================================================================
# CARD
# ============================================================================

def Card(
    children: str,
    variant: Literal['default', 'highlight', 'action'] = 'default',
    padding: Size = 'md'
) -> str:
    """Consistent card component"""
    paddings: dict[Size, str] = {
        'sm': 'var(--space-sm) var(--space-md)',
        'md': 'var(--space-md) var(--space-lg)',
        'lg': 'var(--space-lg) var(--space-xl)',
    }
    
    border_style = '1px solid var(--border-color)'
    if variant == 'highlight':
        border_style = '1px solid var(--brand-primary)'
    elif variant == 'action':
        border_style = '1px solid var(--border-color); border-left: 3px solid var(--brand-primary)'
    
    return f'''
    <div class="ds-card ds-card-{variant}" style="background: var(--bg-card); border-radius: var(--border-radius); padding: {paddings[padding]}; border: {border_style};">
      {children}
    </div>
    '''


# ============================================================================
# METRIC ROW
# ============================================================================

def MetricRow(props: dict) -> str:
    """Cursor-style metric row - grayscale only. Accepts dict props like TypeScript."""
    label = props.get('label', '')
    value = props.get('value', 0)
    description = props.get('description')
    recommendation = props.get('recommendation')
    
    color = get_status_color(value)
    color_hex = _get_color_hex(color)
    
    desc_html = f'<div style="font-size: 11px; color: var(--text-muted); margin-top: 2px;">{escape_html(description)}</div>' if description else ''
    rec_html = f'<div style="font-size: 11px; color: var(--color-danger); margin-top: 6px;">→ {escape_html(recommendation)}</div>' if recommendation else ''
    
    return f'''
    <div class="ds-metric-row" style="padding: 12px 16px; border-bottom: 1px solid var(--border-color);">
      <div style="display: flex; align-items: center; gap: 16px;">
        <div style="flex: 1;">
          <div style="font-size: 13px; color: var(--text-primary);">{escape_html(label)}</div>
          {desc_html}
        </div>
        <div style="width: 150px; display: flex; align-items: center; gap: 8px;">
          <div style="flex: 1; height: 4px; background: var(--gray-800); border-radius: 2px; overflow: hidden;">
            <div style="width: {value}%; height: 100%; background: {color_hex};"></div>
          </div>
          <span style="font-size: 12px; color: {color_hex}; min-width: 35px; text-align: right;">{value}%</span>
        </div>
      </div>
      {rec_html}
    </div>
    '''


# ============================================================================
# ACTION ITEM
# ============================================================================

def ActionItem(props: dict) -> str:
    """Cursor-style action item - minimal, clean, no colored accents. Accepts dict props like TypeScript."""
    number = props.get('number', 0)
    title = props.get('title', '')
    reason = props.get('reason', '')
    example = props.get('example')
    example_html = f'<div style="font-size: 12px; color: var(--text-muted); margin-top: 6px; padding-left: 12px; border-left: 2px solid var(--border-color);">{escape_html(example)}</div>' if example else ''
    
    return f'''
    <div class="ds-action-item" style="display: flex; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--border-color);">
      <span style="color: var(--text-muted); font-size: 13px; font-weight: 500; min-width: 20px;">{number}.</span>
      <div style="flex: 1;">
        <div style="font-weight: 500; font-size: 14px; color: var(--text-primary);">{escape_html(title)}</div>
        <div style="font-size: 13px; color: var(--text-muted); margin-top: 4px;">{escape_html(reason)}</div>
        {example_html}
      </div>
    </div>
    '''


# ============================================================================
# COMPETITOR ROW
# ============================================================================

def CompetitorRow(props: dict) -> str:
    """Cursor-style competitor row - minimal, mostly grayscale. Accepts dict props like TypeScript."""
    name = props.get('name', '')
    mentions = props.get('mentions', 0)
    visibility = props.get('visibility', 0)
    is_client = props.get('isClient', props.get('is_client', False))
    
    color = get_status_color(visibility)
    color_hex = _get_color_hex(color)
    client_label = ' <span style="color: var(--text-muted);">(You)</span>' if is_client else ''
    
    return f'''
    <tr>
      <td style="padding: 10px 16px; font-size: 13px; color: var(--text-primary);">
        {escape_html(name)}{client_label}
      </td>
      <td style="padding: 10px 16px; text-align: center; font-size: 13px; color: var(--text-muted); font-variant-numeric: tabular-nums;">{mentions}</td>
      <td style="padding: 10px 16px;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <div style="flex: 1; height: 4px; background: var(--gray-800); border-radius: 2px; overflow: hidden;">
            <div style="width: {min(visibility, 100)}%; height: 100%; background: {color_hex};"></div>
          </div>
          <span style="min-width: 40px; text-align: right; font-size: 12px; color: {color_hex};">{round(visibility)}%</span>
        </div>
      </td>
    </tr>
    '''


# ============================================================================
# QUERY ROW
# ============================================================================

def QueryRow(props: dict) -> str:
    """Cursor-style query row - simple, grayscale badge. Accepts dict props like TypeScript."""
    dimension = props.get('dimension', '')
    query = props.get('query', '')
    
    dim_label = dimension.replace('_', ' ').replace('-', ' ').title()
    
    return f'''
    <div class="ds-query-row" style="display: flex; align-items: center; gap: 12px; padding: 6px 0; border-bottom: 1px solid var(--border-color);">
      <span style="min-width: 90px; padding: 3px 6px; border-radius: 3px; font-size: 10px; font-weight: 500; text-transform: uppercase; text-align: center; background: var(--gray-800); color: var(--text-muted);">{escape_html(dim_label)}</span>
      <span style="flex: 1; font-size: 13px; color: var(--text-secondary);">{escape_html(query)}</span>
    </div>
    '''


# ============================================================================
# QUALITY BAR
# ============================================================================

def QualityBar(props: dict) -> str:
    """Cursor-style quality bar - subtle grayscale. Accepts dict props like TypeScript."""
    label = props.get('label', '')
    value = props.get('value', 0)
    total = props.get('total', 1)
    color = props.get('color', 'var(--gray-500)')
    
    pct = round((value / total) * 100) if total > 0 else 0
    
    return f'''
    <div class="ds-quality-bar" style="display: flex; align-items: center; gap: 12px; padding: 6px 0;">
      <span style="min-width: 120px; font-size: 13px; color: var(--text-muted);">{escape_html(label)}</span>
      <div style="flex: 1; height: 4px; background: var(--gray-800); border-radius: 2px; overflow: hidden;">
        <div style="width: {pct}%; height: 100%; background: {color};"></div>
      </div>
      <span style="min-width: 40px; text-align: right; font-size: 12px; color: {color};">{pct}%</span>
    </div>
    '''


# ============================================================================
# TABLE OF CONTENTS
# ============================================================================

def Grid2(children: str) -> str:
    """Grid2 component - 2 column grid"""
    return f'<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px 16px;">{children}</div>'


def build_table_of_contents(props: dict) -> str:
    """Build table of contents navigation"""
    items = props.get('items', [])
    title = props.get('title', 'Table of Contents')
    
    # Only show TOC for reports with 4+ major sections
    if len(items) < 4:
        return ''
    
    toc_items = []
    for idx, item in enumerate(items):
        indent = 'padding-left: 24px;' if item.get('level') == 2 else ''
        toc_items.append(f'''
      <a href="#{escape_html(item.get('id', ''))}" class="toc-link" style="display: flex; align-items: center; gap: 12px; padding: 8px 0; text-decoration: none; color: var(--text-secondary); transition: color 0.2s; {indent}">
        <span class="toc-number" style="font-weight: 500; color: var(--text-muted); min-width: 24px;">{idx + 1}</span>
        <span class="toc-title" style="flex: 1;">{escape_html(item.get('title', ''))}</span>
      </a>
    ''')
    
    return f'''
    <div class="section-secondary" style="background: var(--bg-card); border-radius: var(--border-radius-lg); border: 1px solid var(--border-color);">
      <h2 class="section-title" style="margin-bottom: 20px;">
        <span class="icon">{ICONS['documentText']}</span>
        {escape_html(title)}
      </h2>
      <nav class="toc-nav" style="display: flex; flex-direction: column;">
        {''.join(toc_items)}
      </nav>
      <style>
        .toc-link:hover {{
          color: var(--text-primary);
        }}
      </style>
    </div>
    '''

