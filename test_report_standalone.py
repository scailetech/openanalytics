"""
Test HTML Report Generation - Standalone (No API Keys Required)

Generates an HTML report using sample data - no external API calls.
"""

import sys
from pathlib import Path
from datetime import datetime

# Add reports to path
sys.path.insert(0, str(Path(__file__).parent))

from reports.html_generator import build_aeo_report_html


def get_sample_data(company_name: str = "Telli"):
    """Get rich sample AEO analysis data to mirror the full TypeScript report."""

    visibility = 52.6
    industry = "Data Analytics / Business Intelligence"

    return {
        'clientName': company_name,
        'websiteUrl': 'https://telli.com',
        'generatedAt': datetime.now(),
        'theme': 'dark',
        'canvasData': {
            'clientInfo': {
                'name': company_name,
                'website': 'https://telli.com',
                'industry': industry,
                'products': ['AI Call Agents', 'Voice AI Platform', 'Call Automation'],
                'services': ['Lead Qualification', 'Appointment Booking', 'Customer Engagement', 'Call Operations'],
            },
            'aeoHealthCheck': {
                'score': 45,
                'healthScore': 45,
                'grade': 'C',
                'categoryClarityScore': 34,
                'entityStrengthScore': 70,
                'authorityScore': 100,
            },
            'healthCheck': {
                'score': 45,
                'healthScore': 45,
                'grade': 'C',
                'categoryClarityScore': 34,
                'entityStrengthScore': 70,
                'authorityScore': 100,
            },
            'mentionsCheck': {
                'visibility': visibility,
                'band': 'Moderate',
                'qualityScore': 6.8,
                'chatgptPresence': 24,
                'totalMentions': 24,
                'numQueries': 10,
                'platformStats': {
                    'gemini': {'mentions': 6, 'responses': 10},
                    'chatgpt': {'mentions': 5, 'responses': 10},
                    'perplexity': {'mentions': 6, 'responses': 10},
                    'claude': {'mentions': 4, 'responses': 10},
                    'mistral': {'mentions': 3, 'responses': 10},
                }
            },
            'competitors': [
                {'name': 'Amplitude', 'visibility': 100},
                {'name': 'Mixpanel', 'visibility': 100},
                {'name': 'Heap', 'visibility': 36},
            ],
        },
        'industryBenchmark': {
            'industry': industry,
            'percentile': 86,
            'qualityPercentile': 68,
            'position': 'Above Average',
            'visibility': visibility,
            'industryAverage': 28,
            'topPerformers': 55,
            'gapToTop': 2.4,
            'contextNote': 'Note: Using general industry benchmarks. Run company analysis for more accurate comparison.'
        },
        'queryInsights': {
            'highlights': [
                {
                    'query': 'Mitzu vs Amplitude',
                    'platform': 'chatgpt',
                    'responseExcerpt': "Mitzu announced Firebolt support and concluded a pre-seed round Oct 2023.",
                    'dimension': 'competitive',
                },
                {
                    'query': 'Mitzu vs Mixpanel',
                    'platform': 'chatgpt',
                    'responseExcerpt': "Comparison of Mitzu and Mixpanel with general information on both.",
                    'dimension': 'competitive',
                },
            ],
            'lowlights': [
                {
                    'query': 'best Product Analytics for Product teams in Global',
                    'platformsChecked': ['gemini', 'chatgpt', 'perplexity'],
                    'reason': "Competitors (Amplitude, Mixpanel) are being recommended instead of you",
                    'responseExcerpt': 'Top-tier tools frequently recommended include Amplitude and Mixpanel.',
                    'opportunityType': 'commercial',
                    'competitorsMentioned': ['Amplitude', 'Mixpanel'],
                },
                {
                    'query': f'best Product Analytics {datetime.now().year}',
                    'platformsChecked': ['gemini', 'chatgpt', 'perplexity'],
                    'reason': "Competitors (Amplitude, Heap) are being recommended instead of you",
                    'responseExcerpt': 'Best product analytics tools highlighted: Amplitude, Heap.',
                    'opportunityType': 'recommendations',
                    'competitorsMentioned': ['Amplitude', 'Heap'],
                },
            ],
            'lowlightType': 'missed',
            'topOpportunities': [
                {
                    'query': 'best Product Analytics for Product teams in Global',
                    'dimension': 'commercial',
                    'platforms': ['gemini', 'chatgpt', 'perplexity'],
                    'competitorsMentioned': [],
                    'whyItMatters': 'Opportunity to capture',
                    'opportunityType': 'commercial',
                },
                {
                    'query': f'best Product Analytics {datetime.now().year}',
                    'dimension': 'recommendations',
                    'platforms': ['gemini', 'chatgpt', 'perplexity'],
                    'competitorsMentioned': ['Amplitude', 'Heap', 'Mixpanel'],
                    'whyItMatters': 'Competitors are being recommended instead of you',
                    'opportunityType': 'recommendations',
                },
                {
                    'query': 'best software for complex data pipelines',
                    'dimension': 'problem-solution',
                    'platforms': ['gemini', 'chatgpt', 'perplexity'],
                    'competitorsMentioned': ['Apache Airflow', 'Informatica PowerCenter', 'AWS Glue'],
                    'whyItMatters': 'Competitors are being recommended instead of you',
                    'opportunityType': 'problem-solution',
                },
                {
                    'query': 'best Product Analytics for Data analysts',
                    'dimension': 'informational',
                    'platforms': ['gemini', 'chatgpt', 'perplexity'],
                    'competitorsMentioned': ['Heap', 'Amplitude', 'Mixpanel'],
                    'whyItMatters': 'Competitors are being recommended instead of you',
                    'opportunityType': 'informational',
                },
                {
                    'query': f'top Product Analytics tools {datetime.now().year}',
                    'dimension': 'recommendations',
                    'platforms': ['gemini', 'chatgpt', 'perplexity'],
                    'competitorsMentioned': ['Amplitude', 'Mixpanel', 'Heap'],
                    'whyItMatters': 'Competitors are being recommended instead of you',
                    'opportunityType': 'recommendations',
                },
            ],
            'qualityDistribution': {
                'featured': 30,
                'mentioned': 0,
                'brief': 10,
                'notMentioned': 60,
            },
            'categoryClarity': 34,
            'entityStrength': 70,
        },
        'queryTypePerformance': [
            {'queryType': 'Commercial', 'description': '"Best tools", recommendations, features', 'prompts': 4, 'apiChecks': 20, 'withMentions': 0, 'presenceRate': 0},
            {'queryType': 'Competitive', 'description': '"X vs Y" comparison queries', 'prompts': 2, 'apiChecks': 10, 'withMentions': 2, 'presenceRate': 100},
            {'queryType': 'Informational', 'description': 'ICP targeting, regional, educational', 'prompts': 2, 'apiChecks': 10, 'withMentions': 0, 'presenceRate': 0},
            {'queryType': 'Branded', 'description': 'Direct brand name searches', 'prompts': 2, 'apiChecks': 10, 'withMentions': 2, 'presenceRate': 100},
        ],
        'sampleQueries': [
            {'type': 'Branded', 'query': 'what is Mitzu'},
            {'type': 'Competitive', 'query': 'Mitzu vs Amplitude'},
            {'type': 'ICP Targeting', 'query': 'best Product Analytics for Product teams in Global'},
            {'type': 'Recommendations', 'query': f'best Product Analytics {datetime.now().year}'},
            {'type': 'Problem Solution', 'query': 'best software for complex data pipelines'},
            {'type': 'Branded', 'query': 'Mitzu Product Analytics review'},
            {'type': 'Competitive', 'query': 'Mitzu vs Mixpanel'},
            {'type': 'ICP Targeting', 'query': 'best Product Analytics for Data analysts'},
            {'type': 'Recommendations', 'query': f'top Product Analytics tools {datetime.now().year}'},
            {'type': 'Problem Solution', 'query': 'how to solve slow analytics queries'},
        ],
        'mentionQuality': {
            'featured': 30,
            'detailed': 10,
            'brief': 0,
            'notMentioned': 60,
        },
        'contentStrategy': {
            'pillars': [
                {
                    'pillar': 'Problem-Solution Content',
                    'clusters': [
                        'How to solve: Complex data pipelines',
                        'How to solve: Slow analytics queries',
                        'How to solve: Data silos',
                        'How to solve: High costs of traditional analytics',
                    ],
                },
                {
                    'pillar': 'Use Case Deep Dives',
                    'clusters': [
                        'Mitzu for Track user journeys',
                        'Mitzu for Analyze conversion funnels',
                        'Mitzu for Measure product adoption',
                    ],
                },
                {
                    'pillar': 'Product & Feature Guides',
                    'clusters': [
                        'Complete guide to Warehouse-native analytics',
                        'Complete guide to Customer journey tracking',
                        'Complete guide to Event analytics',
                        'Complete guide to Product analytics',
                        'Complete guide to User behavior analysis',
                    ],
                },
                {
                    'pillar': 'Feature & Capability Guides',
                    'clusters': [
                        'product analytics explained',
                        'warehouse native explained',
                        'customer journey explained',
                        'event tracking explained',
                    ],
                },
            ],
            'priorityContent': [
                {
                    'title': 'The Complete Guide to Solving Complex data pipelines',
                    'description': 'Comprehensive guide addressing the #1 pain point for your target audience',
                    'words': '2,500-3,500',
                    'priority': 'Critical',
                    'schema': ['Article', 'HowTo', 'FAQPage'],
                },
                {
                    'title': 'Mitzu Warehouse-native analytics: Features, Benefits & Use Cases',
                    'description': 'Detailed breakdown of your primary offering for AI recommendation engines',
                    'words': '2,000-2,500',
                    'priority': 'High',
                    'schema': ['Product', 'Article', 'FAQPage'],
                },
                {
                    'title': 'How to Use Mitzu for Track user journeys',
                    'description': 'Step-by-step guide showing real-world application',
                    'words': '1,500-2,000',
                    'priority': 'High',
                    'schema': ['HowTo', 'Article'],
                },
                {
                    'title': 'Mitzu for Data Analytics / Business Intelligence: Complete Guide',
                    'description': 'Industry-focused content for vertical AI queries',
                    'words': '2,000-2,500',
                    'priority': 'Medium',
                    'schema': ['Article', 'HowTo'],
                },
            ],
            'monthlyCapacity': '4-6 articles',
        },
    }


def main():
    """Generate HTML report from sample data."""
    
    company_name = sys.argv[1] if len(sys.argv) > 1 else "Telli"
    
    print(f"\n🧪 Generating HTML Report (Standalone Test)")
    print(f"📊 Company: {company_name}")
    print()
    
    # Get sample data
    data = get_sample_data(company_name)
    
    # Generate HTML report
    print("⏳ Generating HTML report...")
    html = build_aeo_report_html(data)
    
    # Save to file
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    filename = f"test-report-{company_name.lower().replace(' ', '-')}-{timestamp}.html"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    size_kb = len(html) / 1024
    print(f"✅ HTML Report generated")
    print(f"   → Saved: {filename}")
    print(f"   → Size: {size_kb:.1f} KB")
    print()
    print(f"🌐 Open in browser:")
    print(f"   open {filename}")
    print()


if __name__ == '__main__':
    main()

