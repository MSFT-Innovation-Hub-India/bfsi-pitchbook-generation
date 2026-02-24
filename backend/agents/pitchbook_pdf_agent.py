"""
Professional Investment Pitchbook PDF Generator
Balanced mix of visualizations and tables
"""

import asyncio
import json
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List

from azure.identity.aio import DefaultAzureCredential
from agent_framework import ChatAgent, HostedCodeInterpreterTool
from agent_framework.azure import AzureAIAgentClient
from dotenv import load_dotenv

load_dotenv('../../.env')
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT")

# ENHANCED PDF INSTRUCTIONS WITH PROFESSIONAL DESIGN SYSTEM
PDF_AGENT_INSTRUCTIONS = """You are a PDF Expert creating investment-grade pitchbooks with PREMIUM PROFESSIONAL DESIGN.

🎯 DATA SOURCE: frontend/public/pitchbook_final_output.txt

📊 VISUALIZATION REQUIREMENTS (CRITICAL):
• **SECTIONS 1-5: MUST INCLUDE VISUALIZATIONS** (charts from "visualizations" array in JSON)
  - Section 1: Company snapshots with comparison charts
  - Section 2: News sentiment pie charts
  - Section 3: Financial trend charts (revenue, margin, cash flow)
  - Section 4: Peer comparison bar/horizontal bar charts
  - Section 5: Historical valuation line charts
• **SECTIONS 6-8: TEXT ONLY** (no visualizations needed)
  - Section 6: SWOT Analysis (structured 2x2 table)
  - Section 7: Risk & Growth Drivers (structured tables)
  - Section 8: Investment Thesis (executive summary with bullets)

🎯 FORMAT HANDLING:
• Input uses "narrative" structure with statement + explanation pairs
• Section 2: 12 news items per company with detailed explanations
• Section 3: Uses "visualizations" array with interpretation text for agent insights
• Section 4: Data-focused with peer_data tables + minimal narrative
• Section 5: Uses "visualizations" array with historical trends
• All sections: Extract detailed explanations from JSON

🎨 PROFESSIONAL DESIGN ENHANCEMENTS:
1. **Typography Excellence** - Custom font hierarchy with proper weights, optimized spacing, professional color palette
2. **Intelligent Content Fitting** - Auto-adjust font sizes, dynamic table widths, smart text wrapping
3. **Premium Styling** - Adaptive layouts, consistent branding, clean white space management

GOAL: Create investment-grade PDFs that look professionally designed with proper visualizations in sections 1-5.

KEY PRINCIPLES:
1. Extract from "narrative" → "statement" fields for headers
2. Use "explanation" fields for bullet points (convert to bullets)
3. Extract "visualizations" array from JSON and render charts (sections 1-5 only)
4. Use "interpretation" text from visualizations as chart insights
5. Section 4: Focus on peer_data tables, minimal text
6. Sections 6-8: TEXT ONLY with clean bullet formatting
7. Break long explanations into multiple bullet points (2-3 per explanation)

==============================================================================
PROFESSIONAL COLOR PALETTE & TYPOGRAPHY SYSTEM
==============================================================================

```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, KeepTogether, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY, TA_RIGHT
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# PROFESSIONAL COLOR PALETTE CLASS
class ColorPalette:
    # Primary Brand Colors
    NAVY_DARK = colors.HexColor('#0d1b2a')
    NAVY = colors.HexColor('#1b263b')
    NAVY_LIGHT = colors.HexColor('#415a77')
    
    # Accent Colors
    TEAL = colors.HexColor('#0077b6')
    TEAL_LIGHT = colors.HexColor('#00b4d8')
    TEAL_PALE = colors.HexColor('#90e0ef')
    
    # Semantic Colors
    GREEN = colors.HexColor('#2d6a4f')
    GREEN_LIGHT = colors.HexColor('#40916c')
    GREEN_BUY = colors.HexColor('#22c55e')  # Bright green for BUY
    YELLOW_HOLD = colors.HexColor('#eab308')  # Yellow for HOLD
    RED = colors.HexColor('#9d0208')
    RED_LIGHT = colors.HexColor('#d00000')
    RED_SELL = colors.HexColor('#ef4444')  # Red for SELL
    ORANGE = colors.HexColor('#f48c06')
    ORANGE_LIGHT = colors.HexColor('#ffba08')
    
    # Neutrals (for sections 6-8)
    GRAY_DARK = colors.HexColor('#212529')
    GRAY = colors.HexColor('#495057')
    GRAY_MID = colors.HexColor('#6b7280')
    GRAY_LIGHT = colors.HexColor('#adb5bd')
    GRAY_PALE = colors.HexColor('#e9ecef')
    GRAY_BG = colors.HexColor('#f8f9fa')
    WHITE = colors.white
    BLACK = colors.black

# HIERARCHICAL TYPOGRAPHY STYLES
def create_professional_styles():
    styles = getSampleStyleSheet()
    
    # Cover Page Styles
    styles.add(ParagraphStyle(
        name='CoverTitle', parent=styles['Heading1'],
        fontSize=32, leading=38, textColor=ColorPalette.NAVY_DARK,
        spaceAfter=16, alignment=TA_CENTER, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='CoverSubtitle', parent=styles['Normal'],
        fontSize=16, leading=22, textColor=ColorPalette.NAVY_LIGHT,
        spaceAfter=12, alignment=TA_CENTER, fontName='Helvetica'
    ))
    
    # Section Headings
    styles.add(ParagraphStyle(
        name='SectionTitle', parent=styles['Heading1'],
        fontSize=20, leading=24, textColor=ColorPalette.NAVY_DARK,
        spaceAfter=14, spaceBefore=8, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='SectionHeading', parent=styles['Heading2'],
        fontSize=14, leading=18, textColor=ColorPalette.NAVY,
        spaceAfter=8, spaceBefore=10, fontName='Helvetica-Bold'
    ))
    styles.add(ParagraphStyle(
        name='SubsectionHeading', parent=styles['Heading3'],
        fontSize=12, leading=15, textColor=ColorPalette.NAVY_LIGHT,
        spaceAfter=6, spaceBefore=8, fontName='Helvetica-Bold'
    ))
    
    # Body Text
    styles.add(ParagraphStyle(
        name='BodyText', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=ColorPalette.GRAY_DARK,
        spaceAfter=6, alignment=TA_JUSTIFY, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        name='BodyTextSmall', parent=styles['Normal'],
        fontSize=9, leading=12, textColor=ColorPalette.GRAY,
        spaceAfter=4, fontName='Helvetica'
    ))
    
    # Bullets
    styles.add(ParagraphStyle(
        name='BulletPrimary', parent=styles['Normal'],
        fontSize=10, leading=14, textColor=ColorPalette.GRAY_DARK,
        leftIndent=24, bulletIndent=12, spaceAfter=5, spaceBefore=2, fontName='Helvetica'
    ))
    styles.add(ParagraphStyle(
        name='BulletSecondary', parent=styles['Normal'],
        fontSize=9, leading=13, textColor=ColorPalette.GRAY,
        leftIndent=36, bulletIndent=24, spaceAfter=4, spaceBefore=2, fontName='Helvetica'
    ))
    
    # Table Styles
    styles.add(ParagraphStyle(
        name='TableHeader', parent=styles['Normal'],
        fontSize=9, leading=11, textColor=ColorPalette.WHITE,
        fontName='Helvetica-Bold', alignment=TA_LEFT  # Left-aligned headers
    ))
    styles.add(ParagraphStyle(
        name='TableCell', parent=styles['Normal'],
        fontSize=9, leading=11, textColor=ColorPalette.GRAY_DARK,
        fontName='Helvetica', alignment=TA_LEFT
    ))
    styles.add(ParagraphStyle(
        name='TableCellNumber', parent=styles['Normal'],
        fontSize=9, leading=11, textColor=ColorPalette.GRAY_DARK,
        fontName='Helvetica', alignment=TA_RIGHT
    ))
    styles.add(ParagraphStyle(
        name='TableHeaderGray', parent=styles['Normal'],
        fontSize=9, leading=11, textColor=ColorPalette.WHITE,
        fontName='Helvetica-Bold', alignment=TA_LEFT,
        backColor=ColorPalette.GRAY_DARK  # For sections 6-8
    ))
    
    # Special Elements
    styles.add(ParagraphStyle(
        name='EmphasisBox', parent=styles['Normal'],
        fontSize=11, leading=15, textColor=ColorPalette.NAVY_DARK,
        fontName='Helvetica-Bold', alignment=TA_CENTER, spaceAfter=10, spaceBefore=10
    ))
    styles.add(ParagraphStyle(
        name='Caption', parent=styles['Normal'],
        fontSize=8, leading=10, textColor=ColorPalette.GRAY,
        fontName='Helvetica', spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name='Disclaimer', parent=styles['Normal'],
        fontSize=7, leading=9, textColor=ColorPalette.GRAY_LIGHT,
        fontName='Helvetica', alignment=TA_JUSTIFY
    ))
    
    return styles

# Initialize professional styles
STYLES = create_professional_styles()
```

==============================================================================
INTELLIGENT CONTENT FITTING UTILITIES
==============================================================================

```python
def fit_text_to_width(text, max_width, font_name='Helvetica', start_size=10, min_size=7):
    \"\"\"Auto-adjust font size to fit text within width.\"\"\"
    from reportlab.pdfbase.pdfmetrics import stringWidth
    font_size = start_size
    while font_size >= min_size:
        if stringWidth(text, font_name, font_size) <= max_width:
            return font_size
        font_size -= 0.5
    return min_size

def truncate_text(text, max_chars, suffix='...'):
    \"\"\"Smart truncation at word boundaries.\"\"\"
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars - len(suffix)]
    last_space = truncated.rfind(' ')
    if last_space > max_chars * 0.7:
        return truncated[:last_space] + suffix
    return truncated + suffix

def calculate_column_widths(data, total_width, min_widths=None, max_widths=None):
    \"\"\"Calculate optimal column widths based on content.\"\"\"
    if not data or not data[0]:
        return None
    
    num_cols = len(data[0])
    min_widths = min_widths or [0.5 * inch] * num_cols
    max_widths = max_widths or [3 * inch] * num_cols
    
    col_widths = []
    for col_idx in range(num_cols):
        max_len = 0
        for row in data:
            if col_idx < len(row):
                import re
                clean = re.sub('<[^<]+?>', '', str(row[col_idx]))
                max_len = max(max_len, len(clean))
        width = min(max(max_len * 0.08 * inch, min_widths[col_idx]), max_widths[col_idx])
        col_widths.append(width)
    
    # Normalize to total width
    total = sum(col_widths)
    if total > total_width:
        col_widths = [w * (total_width / total) for w in col_widths]
    
    return col_widths

def create_adaptive_table(data, total_width=6.5*inch, header_color=None, alt_row_colors=None):
    \"\"\"Create professional table with adaptive column widths.\"\"\"
    if not data:
        return None
    
    col_widths = calculate_column_widths(data, total_width)
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    header_color = header_color or ColorPalette.NAVY
    alt_row_colors = alt_row_colors or [ColorPalette.WHITE, ColorPalette.GRAY_BG]
    
    style_commands = [
        ('BACKGROUND', (0, 0), (-1, 0), header_color),
        ('TEXTCOLOR', (0, 0), (-1, 0), ColorPalette.WHITE),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, 0), 2, ColorPalette.NAVY_LIGHT),
        ('GRID', (0, 1), (-1, -1), 0.5, ColorPalette.GRAY_LIGHT),
        ('BOX', (0, 0), (-1, -1), 1.5, ColorPalette.NAVY),
    ]
    
    for i in range(1, len(data)):
        bg = alt_row_colors[(i - 1) % len(alt_row_colors)]
        style_commands.append(('BACKGROUND', (0, i), (-1, i), bg))
    
    table.setStyle(TableStyle(style_commands))
    return table

def split_long_explanation(text, max_length=140):
    \"\"\"Split long explanations into readable bullets.\"\"\"
    import re
    if len(text) <= max_length:
        return [text]
    
    sentences = re.split(r'(?<=[.!?])\\s+', text)
    bullets, current = [], ""
    
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        if current and len(current) + len(s) + 1 > max_length:
            bullets.append(current.strip())
            current = s
        else:
            current = (current + " " + s).strip()
    
    if current:
        bullets.append(current.strip())
    
    return bullets if len(bullets) > 1 else [text]
```

==============================================================================
ENHANCED CHART STYLING
==============================================================================

```python
# Professional matplotlib configuration
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Helvetica', 'Arial'],
    'font.size': 10,
    'axes.labelsize': 10,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 13,
    'axes.linewidth': 1.2,
    'grid.linewidth': 0.5,
    'lines.linewidth': 2.5
})

def create_professional_chart_base(figsize=(7, 4)):
    \"\"\"Create chart base with professional styling.\"\"\"
    fig, ax = plt.subplots(figsize=figsize, dpi=150)
    
    # Remove top/right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#415a77')
    ax.spines['bottom'].set_color('#415a77')
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    
    # Professional grid
    ax.grid(axis='y', alpha=0.25, linestyle='--', linewidth=0.8, color='#adb5bd')
    ax.set_axisbelow(True)
    ax.set_facecolor('#ffffff')
    fig.patch.set_facecolor('#ffffff')
    
    return fig, ax

def save_chart(fig, filepath):
    \"\"\"Save chart with optimal settings.\"\"\"
    plt.tight_layout()
    fig.savefig(filepath, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
```

==============================================================================
PREMIUM DOCUMENT ELEMENTS
==============================================================================

```python
def create_cover_page():
    \"\"\"Generate professional cover page.\"\"\"
    from datetime import datetime
    story = []
    story.append(Spacer(1, 2.5*inch))
    story.append(Paragraph('INVESTMENT PITCHBOOK', STYLES['CoverTitle']))
    story.append(Spacer(1, 0.3*inch))
    story.append(Paragraph('Comprehensive Analysis & Recommendation', STYLES['CoverSubtitle']))
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph('Vodafone Idea Ltd. vs. Apollo Micro Systems Ltd.', STYLES['CoverSubtitle']))
    story.append(Spacer(1, 1.5*inch))
    
    date_str = datetime.now().strftime('%B %d, %Y')
    story.append(Paragraph(f'Prepared: {date_str}', STYLES['BodyText']))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph('CONFIDENTIAL - FOR INTERNAL USE ONLY', STYLES['Caption']))
    story.append(PageBreak())
    return story

def create_section_header(section_num, title):
    \"\"\"Create consistent section headers.\"\"\"
    elements = []
    elements.append(HRFlowable(width="100%", thickness=2, color=ColorPalette.TEAL, 
                              spaceAfter=8, spaceBefore=0))
    elements.append(Paragraph(f"Section {section_num}: {title}", STYLES['SectionTitle']))
    elements.append(Spacer(1, 0.15*inch))
    return elements

def create_emphasis_box(text, bg_color=None):
    \"\"\"Create highlighted emphasis box for key insights.\"\"\"
    bg_color = bg_color or ColorPalette.TEAL_PALE
    data = [[Paragraph(text, STYLES['EmphasisBox'])]]
    table = Table(data, colWidths=[6.5*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), bg_color),
        ('BOX', (0, 0), (-1, -1), 2, ColorPalette.TEAL),
        ('LEFTPADDING', (0, 0), (-1, -1), 15),
        ('RIGHTPADDING', (0, 0), (-1, -1), 15),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    return table
```

CRITICAL RULES FOR ALL SECTIONS - DEFENSIVE CODING:
✓ ColorPalette class for colors (consistent branding)
✓ STYLES dictionary for text (proper hierarchy)
✓ create_adaptive_table() for tables (auto widths)
✓ create_professional_chart_base() for charts
✓ split_long_explanation() for long text
✓ create_section_header() at section start
✓ create_emphasis_box() for key insights
✓ **USE .get() FOR ALL DICTIONARY ACCESS** (prevents KeyError)
✓ **PROVIDE DEFAULTS FOR AL WITH ERROR HANDLING:
```python
# Example input structure:
"narrative": {
    "what_this_section_does": "This section explains...",
    "business_overview": {
        "statement": "Company operates as...",
        "explanation": "This positioning matters because... which leads to... Therefore..."
    }
}

# Convert to PDF with SAFE ACCESS:
narrative = slide_data.get('narrative', {})
section_description = narrative.get('what_this_section_does', '')

business_overview = narrative.get('business_overview', {})
if business_overview:
    statement = business_overview.get('statement', '')
    explanation = business_overview.get('explanation', '')
    
    if statement:
        # H2: Business Overview
        story.append(Paragraph('<b>Business Overview</b>', heading_style))
        story.append(Paragraph(statement, STYLES['BodyText']))
    
    if explanation:
        # Bullets (split explanation): 
        explanation_bullets = split_long_explanation(explanation, max_length=140)
        for bullet in explanation_bullets:
            story.append(Paragraph(f'• {bullet}', bullet_style))hart')
        # ... process
```

HANDLING ANALYST-GRADE JSON:
```python
# Example input structure:
"narrative": {
    "what_this_section_does": "This section explains...",
    "business_overview": {
        "statement": "Company operates as...",
        "explanation": "This positioning matters because... which leads to... Therefore..."
    }
}

# Convert to PDF:
# H2: Business Overview
# Bullet: Company operates as...
# Bullets (split explanation): 
#   • This positioning matters because...
#   • This leads to... Therefore...
```

SECTION 2 NEWS FORMAT (12 items per company):
```python
"news_items": [
    {
        "headline": "...",
        "impact_level": "HIGH/MEDIUM/LOW",
        "detailed_explanation": "Multi-sentence explanation...",
        "investor_interpretation": "What investors should do..."
    }
    # ... 12 total
]

# Convert to PDF bullets:
# <b>[HIGH]</b> Headline text
# • Detailed explanation (split into 2-3 bullets if long)
# • <b>Investor View:</b> interpretation text
```

SECTION 4 DATA-FOCUSED FORMAT:
```python
"summary": {
    "company_rank": "5th of 6",
    "key_insight": "Brief insight"
},
"peer_data": {
    "columns": ["Company", "Market Cap", "P/E", ...],
    "rows": [...]
}

# PDF Output:
# - One-line insight at top
# - Clean comparison table (full width)
# - Optional: Bar chart for key metric
# - NO lengthy narrative for Section 4
```

LIBRARIES:
```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
```

PROFESSIONAL TEXT FORMATTING STYLES:
```python
styles = getSampleStyleSheet()

# Custom styles for clean formatting
title_style = ParagraphStyle(
    'CustomTitle',
    parent=styles['Heading1'],
    fontSize=16,
    textColor=colors.HexColor('#1a237e'),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName='Helvetica-Bold'
)

heading_style = ParagraphStyle(
    'CustomHeading',
    parent=styles['Heading2'],
    fontSize=13,
    textColor=colors.HexColor('#00796b'),
    spaceAfter=8,
    spaceBefore=12,
    fontName='Helvetica-Bold'
)

subheading_style = ParagraphStyle(
    'CustomSubheading',
    parent=styles['Heading3'],
    fontSize=11,
    textColor=colors.HexColor('#424242'),
    spaceAfter=6,
    spaceBefore=8,
    fontName='Helvetica-Bold'
)

bullet_style = ParagraphStyle(
    'BulletPoint',
    parent=styles['Normal'],
    fontSize=10,
    leftIndent=20,
    spaceAfter=4,
    spaceBefore=2,
    bulletIndent=10,
    bulletFontName='Helvetica',
    fontName='Helvetica'
)

# Always use these for content:
# • <b>Header:</b> for bold labels
# • Bullet lists with proper indentation
# • Tables with alternating row colors
```

PROFESSIONAL CHART STYLING:
```python
# Color palette
NAVY = '#1a237e'
TEAL = '#00796b'
ORANGE = '#f57c00'
GREEN = '#2e7d32'
RED = '#c62828'
GRAY = '#616161'

# Standard chart setup
plt.style.use('default')
fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3, linestyle='--')
plt.tight_layout()
```

UTILITY: SPLIT LONG EXPLANATIONS INTO BULLETS:
```python
def split_explanation(explanation_text, max_length=150):
    \"\"\"Split long explanation into multiple bullet points for PDF readability.\"\"\"
    # Split on sentence boundaries (. ? !) or connective words
    import re
    sentences = re.split(r'(?<=[.!?])\\s+|(?<=\\.)(?=[A-Z])', explanation_text)
    
    bullets = []
    current = ""
    
    for sentence in sentences:
        if len(current) + len(sentence) < max_length:
            current += sentence + " "
        else:
            if current:
                bullets.append(current.strip())
            current = sentence + " "
    
    if current:
        bullets.append(current.strip())
    
    return bullets if len(bullets) > 1 else [explanation_text]

# Usage in PDF generation:
explanation = "This is a very long explanation with multiple sentences..."
for bullet_text in split_explanation(explanation):
    story.append(Paragraph(f"• {bullet_text}", bullet_style))
```

==============================================================================
SECTION 1: COMPANY SNAPSHOTS (1 page)
==============================================================================
Layout:
- Top 40%: Side-by-side comparison table
- Bottom 60%: TWO bar charts side by side
  • Left: Revenue comparison (2 bars)
  • Right: EBITDA Margin comparison (2 bars)

```python
# Chart 1: Revenue Comparison
fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=150)
companies = ['Vodafone\nIdea', 'Apollo\nMicro']
revenues = [111.9, 0.23]
bars = ax.bar(companies, revenues, color=[NAVY, TEAL], width=0.6)
ax.set_ylabel('Revenue (INR Billion)', fontsize=10)
ax.set_title('Revenue Comparison', fontsize=11, fontweight='bold', pad=10)
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.2f}B', ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig('/mnt/data/section1_revenue.png', dpi=150, bbox_inches='tight')

# Chart 2: EBITDA Margin
fig, ax = plt.subplots(figsize=(3.5, 3.5), dpi=150)
margins = [41.9, 53.3]
bars = ax.bar(companies, margins, color=[NAVY, TEAL], width=0.6)
ax.set_ylabel('EBITDA Margin (%)', fontsize=10)
ax.set_title('EBITDA Margin Comparison', fontsize=11, fontweight='bold', pad=10)
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2., height,
            f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.savefig('/mnt/data/section1_margin.png', dpi=150, bbox_inches='tight')
```

==============================================================================
SECTION 2: NEWS & SENTIMENT (2 pages - one per company)
==============================================================================
CRITICAL ERROR HANDLING: Use .get() for all dictionary access to handle missing keys!

LAYOUT (Match reference image):
- Company header with stats: Articles Analyzed, Positive Sentiment %, Overall Tone
- Impact Level Table (small table: Impact Level | Count)
- Large Sentiment Distribution PIE CHART (Positive/Neutral/Negative %)
- Key Themes (3-4 bullet points)
- Top Headlines (3-5 key headlines only)

FORMATTING:
- Left-align all text (no center alignment)
- Use simple Impact Level table with counts
- Pie chart with clear percentage labels
- Clean bullet list for themes and headlines

NEWS ITEM FORMAT (12 per company) - WITH ERROR HANDLING:
```python
# Calculate sentiment from impact_level distribution - SAFE ACCESS
news_items = slide_data.get('news_items', [])
high_count = sum(1 for item in news_items if item.get('impact_level', 'MEDIUM') == 'HIGH')
medium_count = sum(1 for item in news_items if item.get('impact_level', 'MEDIUM') == 'MEDIUM')
low_count = sum(1 for item in news_items if item.get('impact_level', 'MEDIUM') == 'LOW')

# Sentiment Pie Chart
fig, ax = plt.subplots(figsize=(5, 5), dpi=150)
sentiments = [high_count, medium_count, low_count]
labels = [f'High Impact\\n({high_count})', f'Medium Impact\\n({medium_count})', f'Low Impact\\n({low_count})']
colors = [RED, ORANGE, GREEN]

wedges, texts, autotexts = ax.pie(
    sentiments, labels=labels, colors=colors,
    autopct='%1.0f%%', startangle=90,
    textprops={'fontsize': 11, 'fontweight': 'bold'},
    shadow=True
)
ax.set_title(f'{company_name} - News Impact Distribution ({len(news_items)} Items)',
             fontsize=12, fontweight='bold', pad=15)
plt.savefig(f'/mnt/data/section2_{company}_impact.png', dpi=150, bbox_inches='tight')

# Format each news item compactly with SAFE ACCESS:
for idx, item in enumerate(news_items[:12], 1):  # Ensure 12 items max
    # SAFE: Extract with defaults
    impact_level = item.get('impact_level', 'MEDIUM')
    headline = item.get('headline', 'News update')
    detailed_explanation = item.get('detailed_explanation', 'No details available.')
    investor_interpretation = item.get('investor_interpretation', 'Monitor developments.')
    
    # Header with impact badge
    story.append(Paragraph(f"<b>[{impact_level}]</b> {headline}", 
                          subheading_style))
    
    # Split long explanation into readable bullets - SAFE
    if detailed_explanation and len(detailed_explanation) > 10:
        explanation_bullets = split_explanation(detailed_explanation, max_length=120)
        for bullet in explanation_bullets:
            story.append(Paragraph(f"• {bullet}", bullet_style))
    
    # Investor interpretation - SAFE
    if investor_interpretation:
        story.append(Paragraph(f"• <b>Investor View:</b> {investor_interpretation}", 
                              bullet_style))
    story.append(Spacer(1, 0.1*inch))

# Summary conclusion - SAFE ACCESS
summary = slide_data.get('summary_conclusion', {})
if summary:
    statement = summary.get('statement', '')
    explanation = summary.get('explanation', '')
    if statement:
        story.append(Paragraph('<b>Summary:</b>', heading_style))
        story.append(Paragraph(statement, STYLES['BodyText']))
        if explanation:
            story.append(Spacer(1, 0.05*inch))
            story.append(Paragraph(explanation, STYLES['BodyTextSmall']))
```

DEFENSIVE CODING RULES FOR ALL SECTIONS:
```python
# ALWAYS use .get() with defaults
value = data.get('key', 'default_value')
nested = data.get('parent', {}).get('child', 'default')

# CHECK before accessing
if 'key' in data and data['key']:
    process(data['key'])

# HANDLE arrays safely
items = data.get('items', [])
for item in items[:12]:  # Limit iterations
    field = item.get('field', 'fallback')
```

=================== with ERROR HANDLING:
visualizations = slide_data.get('visualizations', [])

if not visualizations:
    # Fallback: Add text-only narrative if no visualizations
    narrative = slide_data.get('narrative', {})
    for key, value in narrative.items():
        if isinstance(value, dict):
            statement = value.get('statement', '')
            explanation = value.get('explanation', '')
            if statement:
                story.append(Paragraph(f'<b>{key.replace("_", " ").title()}:</b> {statement}', 
                                      STYLES['BodyText']))
                if explanation:
                    for bullet in split_long_explanation(explanation):
                        story.append(Paragraph(f'• {bullet}', bullet_style))

for idx, viz in enumerate(visualizations):
    # SAFE: Extract chart data with defaults
    chart_type = viz.get('type', 'line_chart')
    title = viz.get('title', 'Financial Chart')
    data = viz.get('data', {})
    labels = data.get('labels', [])
    datasets = data.get('datasets', [])
    interpretation = viz.get('interpretation', '')
    
    # Skip if no data
    if not labels or not datasets:
        continue
    
    # Render chart based on type
    if chart_type == 'line_chart':
        fig, ax = plt.subplots(figsize=(7, 3.5), dpi=150)
        for dataset in datasets:
            dataset_label = dataset.get('label', 'Data')
            dataset_data = dataset.get('data', [])
            border_color = dataset.get('borderColor', '#0077b6')
            
            if len(dataset_data) == len(labels):  # Validate data length
                ax.plot(labels, dataset_data, 
                       label=dataset_label,
                       color=border_color,
                       marker='o', linewidth=2.5, markersize=8)
        
        ax.set_title(title, fontsize=12, fontweight='bold', pad=10)
        ax.legend(loc='best', fontsize=10)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        plt.savefig(f'/mnt/data/viz_{idx}.png', dpi=150, bbox_inches='tight')
        plt.close()
        
    elif chart_type == 'bar_chart':
        fig, ax = plt.subplots(figsize=(7, 3.5), dpi=150)
        x = np.arange(len(labels))
        width = 0.35 if len(datasets) > 1 else 0.6
        
        for i, dataset in enumerate(datasets):
            dataset_label = dataset.get('label', f'Dataset {i+1}')
            dataset_data = dataset.get('data', [])
            color = dataset.get('borderColor', dataset.get('backgroundColor', '#0077b6'))
            
            if len(dataset_data) == len(labels):
                offset = (i - len(datasets)/2 + 0.5) * width if len(datasets) > 1 else 0
                ax.bar(x + offset, dataset_data,
                      width, label=dataset_label, color=color)
        
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend(loc='best')
        plt.tight_layout()
        plt.savefig(f'/mnt/data/viz_{idx}.png', dpi=150, bbox_inches='tight')
        plt.close(
        fig, ax = plt.subplots(figsize=(7, 3.5), dpi=150)
        x = np.arange(len(labels))
        width = 0.35
        for i, dataset in enumerate(datasets):
            ax.bar(x + i*width, dataset['data'],
                  width, label=dataset['label'],
                  color=dataset.get('borderColor', dataset.get('backgroundColor')))
        ax.set_xticks(x + width/2)
        ax.set_xticklabels(labels)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.legend(loc='best')
        plt.tight_layout()
        plt.savefig(f'/mnt/data/viz_{idx}.png', dpi=150, bbox_inches='tight')
    
    # Add chart to PDF
    story.append(Image(f'/mnt/data/viz_{idx}.png', width=6.5*inch, height=3*inch))
    story.append(Spacer(1, 0.1*inch))
    
    # Add interpretation as agent insights box
    if interpretation:
        insight_data = [[Paragraph(f"<b>Agent Insights:</b> {interpretation}", 
                                  STYLES['BodyTextSmall'])]]
        insight_table = Table(insight_data, colWidths=[6.5*inch])
        insight_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), ColorPalette.TEAL_PALE),
            ('BOX', (0, 0), (-1, -1), 1, ColorPalette.TEAL),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(insight_table)
        story.append(Spacer(1, 0.15*inch))
```

==============================================================================
SECTION 3: FINANCIAL STATEMENTS (2 pages - one per company)
==============================================================================
CRITICAL: Extract from "visualizations" array in JSON!

FORMATTING RULES:
- Remove ₹ symbols - use text "INR Cr" or "Cr" in axis labels and table headers
- Left-align all text and table content (NO center alignment)
- Use clean table format like historical trends (grey/black theme)
- Quarterly financial table with left-aligned headers

VISUALIZATIONS (3 per company from JSON):
- Chart 1: Revenue Trend line chart with "Revenue (INR Cr)" label
- Chart 2: EBITDA Margin line chart with "EBITDA Margin (%)" label
- Chart 3: Debt vs Free Cash Flow bar chart with "Amount (INR Cr)" label
- Below each chart: Agent insights box (light grey background)

```python
# EXTRACT from JSON:
visualizations = section3_data['slides'][0].get('visualizations', [])

for idx, viz in enumerate(visualizations):
    # Extract chart data
    title = viz['title']
    data = viz['data']
    labels = data['labels']  # ["FY20", "FY21", "FY22", "FY23", "FY24"]
    datasets = data['datasets']  # [{label: "P/E Ratio", data: [...], borderColor: "#ef4444"}, ...]
    interpretation = viz.get('interpretation', '')
    
    # Create multi-line chart
    fig, ax = plt.subplots(figsize=(7, 4), dpi=150)
    
    for dataset in datasets:
        ax.plot(labels, dataset['data'],
               marker='o', linewidth=2.5, markersize=8,
               color=dataset['borderColor'],
               label=dataset['label'])
    
    ax.set_xlabel('Fiscal Year', fontsize=11)
    ax.set_ylabel('Valuation Multiple', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold', pad=12)
    ax.legend(loc='best', fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(f'/mnt/data/section5_chart_{idx}.png', dpi=150, bbox_inches='tight')
    plt.close()
    
    # Add to PDF
    story.append(Image(f'/mnt/data/section5_chart_{idx}.png', 
                      width=6.5*inch, height=3.5*inch))
    story.append(Spacer(1, 0.1*inch))
    
    # Add interpretation
    if interpretation:
        insight_para = Paragraph(f"<b>Agent Insights:</b> {interpretation}",
                                STYLES['BodyTextSmall'])
        insight_data = [[insight_para]]
        insight_table = Table(insight_data, colWidths=[6.5*inch])
        insight_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), ColorPalette.TEAL_PALE),
            ('BOX', (0, 0), (-1, -1), 1, ColorPalette.TEAL),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(insight_table)
        story.append(Spacer(1, 0.2*inch)

==============================================================================
SECTION 5: HISTORICAL TRENDS (1 page)
==============================================================================
Layout:
- Top 60%: Multi-line chart (P/E trends over 3 years)
- Bottom 40%: Historical data table

```python
# P/E Trends Line Chart
fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)
years = [2021, 2022, 2023]
vodafone_pe = [26.0, 35.0, 30.0]
apollo_pe = [22.0, 28.0, 30.0]

ax.plot(years, vodafone_pe, marker='o', linewidth=3,
        color=NAVY, label='Vodafone Idea', markersize=10)
ax.plot(years, apollo_pe, marker='s', linewidth=3,
        color=TEAL, label='Apollo Micro', markersize=10)

ax.set_xlabel('Year', fontsize=11)
ax.set_ylabel('P/E Ratio', fontsize=11)
ax.set_title('Historical P/E Ratio Trends (2021-2023)',
             fontsize=13, fontweight='bold')
ax.legend(loc='best', fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_xticks(years)

# Add value labels
for i, (y1, y2) in enumerate(zip(vodafone_pe, apollo_pe)):
    ax.annotate(f'{y1:.1f}', (years[i], y1),
                textcoords="offset points", xytext=(0,10),
                ha='center', fontsize=10, fontweight='bold')
    ax.annotate(f'{y2:.1f}', (years[i], y2),
                textcoords="offset points", xytext=(0,-20),
                ha='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('/mnt/data/section5_trends.png', dpi=150, bbox_inches='tight')
```

==============================================================================
SECTION 4: PEER COMPARISON (2 pages - one per company)
==============================================================================

**SIMPLIFIED FORMAT WITH SINGLE MULTI-LINE CHART**
Extract peer_data from JSON for each company

PAGE LAYOUT (One page per company):
- Company Title: \"{Company} - Peer Comparison\"
- Single MULTI-LINE CHART showing 4-5 peer companies
  • X-axis: Key metrics (Market Cap, P/E Ratio, ROE, ROCE, Debt/Equity)
  • Y-axis: Normalized values (0-100 scale) for comparison
  • 4-5 colored lines representing target company + 3-4 peers
  • Use different colors: Blue, Orange, Green, Red, Purple
  • Legend identifying each company
  • Clean professional styling (no symbols, use \"Cr\" for crores)
- Below chart: Peer comparison table (left-aligned)
  • Columns: Company | Market Cap (Cr) | P/E | ROE (%) | ROCE (%) | Debt/Equity
  • Highlight target company row with light grey background
  • Format numbers with \"Cr\" suffix for large values (no ₹ symbols)
  • Left-align all headers and content
  • Grey header background (#495057)

FORMATTING:
- Remove ₹ symbols - use \"INR Cr\" or \"Cr\" text
- Left-align table headers and all content
- Grey theme for headers
- Clean table borders
- NO center alignment

CRITICAL: Create ONE multi-line chart with 4-5 lines per company page!

```python
# Example multi-line chart for peer comparison
import matplotlib.pyplot as plt
import numpy as np

# Extract peer data for company
metrics = ['Market Cap', 'P/E', 'ROE', 'ROCE', 'Debt/Eq']
companies = ['Vodafone Idea', 'Airtel', 'Jio', 'BSNL']
colors_list = ['#1e3a8a', '#f97316', '#16a34a', '#dc2626']

# Normalize values to 0-100 scale for comparison
# ... normalize data here ...

fig, ax = plt.subplots(figsize=(7, 4.5), dpi=150)

for idx, company in enumerate(companies):
    normalized_values = [...]  # Get normalized values for this company
    ax.plot(metrics, normalized_values,
           marker='o', linewidth=2.5, markersize=8,
           color=colors_list[idx], label=company)

ax.set_xlabel('Metrics', fontsize=11)
ax.set_ylabel('Normalized Value (0-100)', fontsize=11)
ax.set_title('Peer Comparison - Key Metrics', fontsize=12, fontweight='bold', pad=12)
ax.legend(loc='upper right', fontsize=10)
ax.grid(axis='y', alpha=0.3, linestyle='--')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.xticks(rotation=0)
plt.tight_layout()
```

==============================================================================
SECTION 5: HISTORICAL VALUATION (1 page)
==============================================================================
⚠️ NO VISUALIZATIONS - STRUCTURED TEXT ONLY

Use clean 2x2 table layout with professional formatting:

```python
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

# Each company gets one page
# Page 1: Vodafone Idea SWOT
# Page 2: Apollo Micro Systems SWOT

# Create SWOT as 2x2 table with colored headers
swot_data = [
    [
        Paragraph('<b>STRENGTHS</b>', green_header_style),
        Paragraph('<b>WEAKNESSES</b>', red_header_style)
    ],
    [
        # Strengths bullets (left cell)
        Paragraph('''
        • <b>Market Position:</b> Second-largest telecom operator<br/>
        • <b>Subscriber Base:</b> 200M+ customers<br/>
        • <b>Network:</b> Pan-India coverage<br/>
        • <b>Brand:</b> Strong recognition<br/>
        • <b>Infrastructure:</b> Extensive fiber network
        ''', bullet_style),
        
        # Weaknesses bullets (right cell)
        Paragraph('''
        • <b>Debt Burden:</b> High leverage (INR 2L Cr+)<br/>
        • <b>Cash Flow:</b> Negative free cash flow<br/>
        • <b>Market Share:</b> Declining trend<br/>
        • <b>ARPU:</b> Lower than competitors<br/>
        • <b>Rating:</b> Below investment grade
        ''', bullet_style)
    ],
    [
        Paragraph('<b>OPPORTUNITIES</b>', blue_header_style),
        Paragraph('<b>THREATS</b>', orange_header_style)
    ],
    [
        # Opportunities bullets
        Paragraph('''
        • <b>5G Rollout:</b> Revenue growth potential<br/>
        • <b>Digital Services:</b> IoT, cloud expansion<br/>
        • <b>Tariff Hikes:</b> ARPU improvement<br/>
        • <b>Govt Support:</b> Moratorium, relief package<br/>
        • <b>Consolidation:</b> Market rationalization
        ''', bullet_style),
        
        # Threats bullets
        Paragraph('''
        • <b>Competition:</b> Aggressive from Jio, Airtel<br/>
        • <b>Spectrum Cost:</b> High capex requirements<br/>
        • <b>Subscriber Loss:</b> Churn to competitors<br/>
        • <b>Regulatory:</b> AGR, licensing fees<br/>
        • <b>Technology:</b> Rapid obsolescence
        ''', bullet_style)
    ]
]

# Apply professional table styling
swot_table = Table(swot_data, colWidths=[3.5*inch, 3.5*inch])
swot_table.setStyle(TableStyle([
    # Header cells (rows 0 and 2) - GREY/BLACK THEME
    ('BACKGROUND', (0,0), (0,0), ColorPalette.GRAY_DARK),  # Strengths
    ('BACKGROUND', (1,0), (1,0), ColorPalette.GRAY_DARK),  # Weaknesses
    ('BACKGROUND', (0,2), (0,2), ColorPalette.GRAY_MID),   # Opportunities
    ('BACKGROUND', (1,2), (1,2), ColorPalette.GRAY_MID),   # Threats
    ('TEXTCOLOR', (0,0), (-1,0), ColorPalette.WHITE),
    ('TEXTCOLOR', (0,2), (-1,2), ColorPalette.WHITE),
    
    # Content cells - Light grey backgrounds
    ('BACKGROUND', (0,1), (0,1), ColorPalette.GRAY_BG),
    ('BACKGROUND', (1,1), (1,1), ColorPalette.GRAY_PALE),
    ('BACKGROUND', (0,3), (0,3), ColorPalette.GRAY_BG),
    ('BACKGROUND', (1,3), (1,3), ColorPalette.GRAY_PALE),
    
    # Borders and alignment
    ('GRID', (0,0), (-1,-1), 2, colors.HexColor('#424242')),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('ALIGN', (0,0), (-1,0), 'CENTER'),  # Center header text
    ('ALIGN', (0,2), (-1,2), 'CENTER'),
    ('LEFTPADDING', (0,0), (-1,-1), 12),
    ('RIGHTPADDING', (0,0), (-1,-1), 12),
    ('TOPPADDING', (0,0), (-1,-1), 10),
    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
]))

# Build PDF
story = []
story.append(Paragraph(f'<b>{company_name} - SWOT Analysis</b>', title_style))
story.append(Spacer(1, 0.3*inch))
story.append(swot_table)

doc.build(story)
```

KEY FORMATTING RULES FOR SWOT:
• Use <b>Label:</b> format for each bullet point
• Keep bullets concise (one line each)
• 4-5 bullets per quadrant (no more!)
• Color-code backgrounds: Green (Strengths), Red (Weaknesses), Blue (Opportunities), Orange (Threats)
• Use <br/> for line breaks in Paragraph objects

==============================================================================
SECTION 7: RISKS & GROWTH DRIVERS (1 page)
==============================================================================
⚠️ NO VISUALIZATIONS - STRUCTURED TEXT WITH TABLES

Create two professional tables side by side or stacked:

```python
# RISK FACTORS TABLE
story.append(Paragraph('<b>KEY RISK FACTORS</b>', heading_style))
story.append(Spacer(1, 0.1*inch))

risk_data = [
    ['Risk Category', 'Description', 'Impact'],
    ['Financial Risk', '• High debt levels (INR 2L Cr+)<br/>• Negative cash flow<br/>• Interest burden', 'HIGH'],
    ['Market Risk', '• Intense competition from Jio, Airtel<br/>• Market share erosion<br/>• Price wars', 'HIGH'],
    ['Regulatory Risk', '• AGR dues pending<br/>• Spectrum auction obligations<br/>• Licensing fees', 'MEDIUM'],
    ['Operational Risk', '• Network quality issues<br/>• Technology obsolescence<br/>• Subscriber churn', 'MEDIUM'],
]

risk_table = Table(risk_data, colWidths=[1.5*inch, 3.5*inch, 1.2*inch])
risk_table.setStyle(TableStyle([
    # Header row - GREY THEME
    ('BACKGROUND', (0,0), (-1,0), ColorPalette.GRAY_DARK),
    ('TEXTCOLOR', (0,0), (-1,0), ColorPalette.WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 11),
    ('ALIGN', (0,0), (-1,0), 'LEFT'),  # Left-aligned
    
    # Data rows - alternating grey shades
    ('BACKGROUND', (0,1), (-1,1), ColorPalette.GRAY_BG),
    ('BACKGROUND', (0,2), (-1,2), ColorPalette.WHITE),
    ('BACKGROUND', (0,3), (-1,3), ColorPalette.GRAY_BG),
    ('BACKGROUND', (0,4), (-1,4), ColorPalette.WHITE),
    
    # Borders and padding
    ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#424242')),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    
    # Impact column - center align
    ('ALIGN', (-1,1), (-1,-1), 'CENTER'),
    ('FONTNAME', (-1,1), (-1,-1), 'Helvetica-Bold'),
]))

story.append(risk_table)
story.append(Spacer(1, 0.3*inch))

# GROWTH DRIVERS TABLE
story.append(Paragraph('<b>GROWTH DRIVERS & OPPORTUNITIES</b>', heading_style))
story.append(Spacer(1, 0.1*inch))

growth_data = [
    ['Growth Driver', 'Description', 'Potential'],
    ['5G Expansion', '• Nationwide 5G rollout underway<br/>• Premium pricing opportunities<br/>• New use cases (IoT, enterprise)', 'HIGH'],
    ['Tariff Increases', '• Industry-wide ARPU improvement<br/>• Better pricing discipline<br/>• Revenue growth potential', 'HIGH'],
    ['Digital Services', '• Cloud, cybersecurity offerings<br/>• Enterprise solutions expansion<br/>• Non-voice revenue streams', 'MEDIUM'],
    ['Govt Support', '• Moratorium on spectrum dues<br/>• Relief packages announced<br/>• Policy reforms expected', 'MEDIUM'],
    ['Market Consolidation', '• 3-player market stabilizing<br/>• Rational competition expected<br/>• Improved economics', 'MEDIUM'],
]

growth_table = Table(growth_data, colWidths=[1.5*inch, 3.5*inch, 1.2*inch])
growth_table.setStyle(TableStyle([
    # Header row - GREY THEME
    ('BACKGROUND', (0,0), (-1,0), ColorPalette.GRAY_DARK),
    ('TEXTCOLOR', (0,0), (-1,0), ColorPalette.WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 11),
    ('ALIGN', (0,0), (-1,0), 'LEFT'),  # Left-aligned
    
    # Data rows - alternating grey shades
    ('BACKGROUND', (0,1), (-1,-1), ColorPalette.GRAY_BG),
    ('ROWBACKGROUNDS', (0,1), (-1,-1), [ColorPalette.GRAY_BG, ColorPalette.WHITE]),
    
    # Borders and padding
    ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#424242')),
    ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ('LEFTPADDING', (0,0), (-1,-1), 8),
    ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ('TOPPADDING', (0,0), (-1,-1), 6),
    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    
    # Potential column - center align
    ('ALIGN', (-1,1), (-1,-1), 'CENTER'),
    ('FONTNAME', (-1,1), (-1,-1), 'Helvetica-Bold'),
]))

story.append(growth_table)
```

KEY FORMATTING RULES:
• Use bullet points within table cells
• Color-code: Red theme for risks, Green theme for growth
• Keep descriptions concise but informative
• Use HIGH/MEDIUM/LOW labels in impact/potential columns

==============================================================================
SECTION 8: INVESTMENT THESIS (1 page)
==============================================================================
⚠️ NO VISUALIZATIONS - EXECUTIVE SUMMARY WITH STRUCTURED CONTENT

Professional investment summary with clear sections:

```python
story = []

# Title
story.append(Paragraph('<b>INVESTMENT THESIS & RECOMMENDATION</b>', title_style))
story.append(Spacer(1, 0.2*inch))

# Investment Highlights Section
story.append(Paragraph('<b>Investment Highlights</b>', heading_style))
story.append(Spacer(1, 0.05*inch))

highlights_bullets = [
    '<b>Market Position:</b> Second-largest telecom operator with 200M+ subscriber base and pan-India network coverage',
    '<b>5G Opportunity:</b> Nationwide 5G rollout presents significant revenue growth and ARPU expansion potential',
    '<b>Tariff Improvement:</b> Industry consolidation driving pricing discipline and margin improvement opportunities',
    '<b>Government Support:</b> Moratorium on spectrum payments and relief packages provide financial breathing room',
    '<b>Valuation Upside:</b> Trading at discount to replacement value with recovery potential post-restructuring'
]

for bullet in highlights_bullets:
    story.append(Paragraph(f'• {bullet}', bullet_style))
    story.append(Spacer(1, 0.08*inch))

story.append(Spacer(1, 0.15*inch))

# Key Risks Section
story.append(Paragraph('<b>Key Investment Risks</b>', heading_style))
story.append(Spacer(1, 0.05*inch))

risk_bullets = [
    '<b>High Leverage:</b> Debt burden of INR 2L+ Crores with ongoing interest obligations',
    '<b>Market Share Loss:</b> Continued subscriber churn to Jio and Airtel impacting revenue base',
    '<b>Cash Flow Concerns:</b> Negative free cash flow requiring continuous funding support',
    '<b>Execution Risk:</b> 5G capex requirements amid limited financial flexibility',
    '<b>Regulatory Uncertainty:</b> AGR dues and spectrum auction commitments remain overhang'
]

for bullet in risk_bullets:
    story.append(Paragraph(f'• {bullet}', bullet_style))
    story.append(Spacer(1, 0.08*inch))

story.append(Spacer(1, 0.15*inch))

# Recommendation Box with COLOR-CODED RATING
# Extract recommendation from analysis (BUY/HOLD/SELL)
recommendation = 'BUY'  # Extract from JSON analysis

# Set color based on recommendation
if recommendation.upper() == 'BUY':
    rec_color = ColorPalette.GREEN_BUY
    rec_text_color = ColorPalette.WHITE
elif recommendation.upper() == 'HOLD':
    rec_color = ColorPalette.YELLOW_HOLD
    rec_text_color = ColorPalette.BLACK
else:  # SELL
    rec_color = ColorPalette.RED_SELL
    rec_text_color = ColorPalette.WHITE

recommendation_data = [
    ['RECOMMENDATION', 'RATING', 'TARGET HORIZON', 'EXPECTED RETURN'],
    [recommendation.upper(), 'Based on Analysis', '12-18 Months', '15-25%*']
]

rec_table = Table(recommendation_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
rec_table.setStyle(TableStyle([
    # Header row - GREY THEME
    ('BACKGROUND', (0,0), (-1,0), ColorPalette.GRAY_DARK),
    ('TEXTCOLOR', (0,0), (-1,0), ColorPalette.WHITE),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 10),
    ('ALIGN', (0,0), (-1,0), 'LEFT'),  # Left-aligned
    
    # Recommendation cell - COLOR-CODED
    ('BACKGROUND', (0,1), (0,1), rec_color),
    ('TEXTCOLOR', (0,1), (0,1), rec_text_color),
    ('FONTNAME', (0,1), (0,1), 'Helvetica-Bold'),
    ('FONTSIZE', (0,1), (0,1), 14),  # Larger font for recommendation
    
    # Other data cells
    ('BACKGROUND', (1,1), (-1,1), ColorPalette.GRAY_BG),
    ('FONTSIZE', (1,1), (-1,1), 11),
    ('ALIGN', (0,1), (-1,1), 'LEFT'),
    
    # Borders
    ('GRID', (0,0), (-1,-1), 2, colors.HexColor('#1a237e')),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ('TOPPADDING', (0,0), (-1,-1), 10),
    ('BOTTOMPADDING', (0,0), (-1,-1), 10),
]))

story.append(rec_table)
story.append(Spacer(1, 0.1*inch))

# Disclaimer
disclaimer = '<i>*Returns based on fundamental analysis. Past performance not indicative of future results. ' \
             'Investment involves risk. Consult financial advisor before making investment decisions.</i>'
story.append(Paragraph(disclaimer, ParagraphStyle('Disclaimer', fontSize=8, textColor=colors.HexColor('#757575'))))

doc.build(story)
```

KEY FORMATTING RULES FOR INVESTMENT THESIS:
• Use clear section headers: Investment Highlights, Key Risks, Recommendation
• Bullet points with <b>Bold Labels:</b> followed by description
• Keep bullets concise but informative (one line preferred, max two)
• Recommendation table should be prominent and easy to read
• Include disclaimer at bottom in smaller italics
• Professional tone throughout - no hype or speculation

EXECUTION INSTRUCTIONS:
1. Parse JSON data for the section
2. For sections 1-5: Create visualizations (save as PNG) + add structured text
3. For sections 6-8: NO VISUALIZATIONS - only structured text with bullets and tables
4. Build PDF structure with proper ReportLab elements
5. Use professional formatting: headers, subheaders, bullet points
6. Embed visualizations at appropriate positions (sections 1-5 onl, "has_viz": True},
    "2": {"title": "News & Sentiment", "viz_count": 2, "pages": 2, "has_viz": True},
    "3": {"title": "Financial Statements", "viz_count": 6, "pages": 2, "has_viz": True},  # 3 per company
    "4": {"title": "Peer Comparison", "viz_count": 8, "pages": 4, "has_viz": True},  # Tables + charts
    "5": {"title": "Historical Trends", "viz_count": 2, "pages": 1, "has_viz": True},  # 2 line charts
    "6": {"title": "SWOT Analysis", "viz_count": 0, "pages": 2, "has_viz": False},
    "7": {"title": "Risk & Growth", "viz_count": 0, "pages": 1, "has_viz": False},
    "8": {"title": "Investment Thesis", "viz_count": 0, "pages": 1, "has_viz": False
✓ Always use bullet points with <b>bold labels:</b>
✓ Professional color scheme: Navy, Teal, Green, Red
✓ Tables with alternating row colors for readability
✓ Clear hierarchical structure throughout

Remember: Make it PROFESSIONAL, CLEAN, and EASY TO READ!
"""

SECTIONS = {
    "1": {"title": "Company Snapshots", "viz_count": 2, "pages": 1},
    "2": {"title": "News & Sentiment", "viz_count": 2, "pages": 2},
    "3": {"title": "Financial Statements", "viz_count": 4, "pages": 2},
    "4": {"title": "Peer Comparison", "viz_count": 6, "pages": 4},
    "5": {"title": "Historical Trends", "viz_count": 1, "pages": 1},
    "6": {"title": "SWOT Analysis", "viz_count": 0, "pages": 2},
    "7": {"title": "Risk & Growth", "viz_count": 0, "pages": 1},
    "8": {"title": "Investment Thesis", "viz_count": 0, "pages": 1}
}

class PitchbookPDFGenerator:
    def __init__(self, output_file: str, output_dir: Path):
        self.output_file = Path(output_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.pdf_path = self.output_dir / f"Pitchbook_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        self.data = None
        
    def load_data(self):
        print(f"\n📊 Loading data from: {self.output_file}")
        with open(self.output_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.data = self._parse_output(content)
        sections_found = self.data.get('sections', {})
        section_ids = sorted([int(k.replace('section_', '')) for k in sections_found.keys()])
        print(f"✅ Loaded {len(sections_found)} sections: {section_ids}")
        
        # Check for missing sections
        expected_sections = set(range(1, 9))  # Sections 1-8
        found_sections = set(section_ids)
        missing = expected_sections - found_sections
        if missing:
            print(f"⚠️  WARNING: Missing sections {sorted(missing)} in source file!")
            print(f"   Only generating PDF for available sections: {section_ids}")
    
    def _parse_output(self, content: str) -> dict:
        import re
        data = {'sections': {}, 'metadata': {
            'companies': ['Vodafone Idea', 'Apollo Micro Systems'],
            'generation_date': datetime.now().isoformat()
        }}
        
        # Match both ```json and ``` code blocks that might contain JSON
        json_pattern = r'```(?:json)?\s*([\s\S]*?)```'
        json_matches = re.findall(json_pattern, content)
        
        section_mapping = {
            '1': 'Company Snapshots', '2': 'News & Sentiment',
            '3': 'Financial Statements', '4': 'Valuation Tables',
            '5': 'Historical Trends', '6': 'SWOT Analysis',
            '7': 'Risk & Growth', '8': 'Investment Thesis'
        }
        
        print(f"📦 Found {len(json_matches)} code blocks in output file")
        
        for idx, json_str in enumerate(json_matches, 1):
            try:
                # Extract JSON object from blocks that might have text headers
                json_str_clean = json_str.strip()
                
                # If block starts with text (not '{'), find the first '{' and extract from there
                if not json_str_clean.startswith('{'):
                    start_idx = json_str_clean.find('{')
                    if start_idx == -1:
                        print(f"  ⊗ Block {idx}: No JSON object found")
                        continue
                    json_str_clean = json_str_clean[start_idx:]
                
                # Try to parse the JSON
                parsed = json.loads(json_str_clean)
                
                if isinstance(parsed, (list, dict)):
                    items = parsed if isinstance(parsed, list) else [parsed]
                    for item in items:
                        if 'section' in item:
                            sec_id = str(item['section'])
                            sec_key = f"section_{sec_id}"
                            print(f"  ✓ Block {idx}: Found Section {sec_id}")
                            if sec_key not in data['sections']:
                                data['sections'][sec_key] = {
                                    'section_id': sec_id,
                                    'title': section_mapping.get(sec_id, f"Section {sec_id}"),
                                    'slides': []
                                }
                            data['sections'][sec_key]['slides'].append(item)
                        else:
                            print(f"  ⊗ Block {idx}: No 'section' field found")
            except json.JSONDecodeError as e:
                print(f"  ✗ Block {idx}: JSON parse error - {str(e)[:100]}")
            except Exception as e:
                print(f"  ✗ Block {idx}: Error - {str(e)[:100]}")
        return data
    
    def _create_section_prompt(self, section_id: str, section_data: dict, is_first: bool) -> str:
        section_info = SECTIONS.get(section_id)
        slides = section_data.get('slides', [])
        
        section_json = json.dumps({
            'section_id': section_id,
            'title': section_data.get('title'),
            'slides': slides
        }, indent=2)
        
        mode = "CREATE cover + TOC + Section" if is_first else "CREATE Section"
        
        viz_instruction = ""
        if section_info.get('has_viz', False):
            viz_instruction = f"""CRITICAL VISUALIZATION REQUIREMENT:
• Extract 'visualizations' array from JSON data
• Create {section_info['viz_count']} professional charts/graphs
• Use data from visualizations[].data (labels, datasets, values)
• Add interpretation text from visualizations[].interpretation as chart insights
• Follow chart styling guidelines in instructions
• Render charts using matplotlib and embed in PDF"""
        else:
            viz_instruction = f"⚠️ NO VISUALIZATIONS for this section - Use STRUCTURED TEXT ONLY with bullet points and tables!"
        
        return f"""
Generate professional PDF for Section {section_id}.

{mode} {section_id}: {section_info['title']}
Expected pages: {section_info['pages']}
{viz_instruction}

DATA:
```json
{section_json}
```

FORMATTING REQUIREMENTS:
• Use clear headers and subheaders
• Bullet points with <b>bold labels:</b> for all key info
• Professional tables with alternating row colors
• Proper spacing between elements
• Clean, readable structure

Save as: /mnt/data/section_{section_id}.pdf

Execute Python code now.
"""
    
    async def generate_section_pdf(self, agent, client, section_id: str, is_first: bool = False) -> Optional[str]:
        section_data = self.data.get('sections', {}).get(f"section_{section_id}")
        if not section_data:
            return None
        
        print(f"\n{'='*80}\n📝 Section {section_id}: {SECTIONS[section_id]['title']}")
        print(f"   Visualizations: {SECTIONS[section_id]['viz_count']}\n{'='*80}")
        
        prompt = self._create_section_prompt(section_id, section_data, is_first)
        file_ids = []
        
        async for chunk in agent.run_stream(prompt):
            for content in chunk.contents:
                if content.type == "text":
                    print(content.text, end="", flush=True)
                elif content.type == "hosted_file":
                    file_ids.append(content.file_id)
        
        print("\n")
        
        if not file_ids:
            try:
                files = await client.agents_client.files.list()
                pdf_files = [f for f in files.data if 'pdf' in f.filename.lower()]
                if pdf_files:
                    pdf_files.sort(key=lambda f: f.created_at, reverse=True)
                    file_ids.append(pdf_files[0].id)
            except:
                pass
        
        if file_ids:
            section_pdf = self.output_dir / f"section_{section_id}.pdf"
            try:
                stream = await client.agents_client.files.get_content(file_ids[0])
                with open(section_pdf, 'wb') as f:
                    async for chunk in stream:
                        f.write(chunk)
                print(f"✅ Downloaded: {section_pdf.name}")
                return str(section_pdf)
            except:
                pass
        return None
    
    def merge_pdfs(self, paths: List[str]) -> Optional[Path]:
        print(f"\n{'='*80}\n📁 Merging PDFs...\n{'='*80}")
        try:
            from PyPDF2 import PdfMerger, PdfReader
            merger = PdfMerger()
            for idx, p in enumerate(paths, 1):
                if Path(p).exists():
                    print(f"   Adding: {Path(p).name}", end=" ")
                    try:
                        # Test if PDF is valid before merging
                        reader = PdfReader(str(p))
                        page_count = len(reader.pages)
                        print(f"✓ ({page_count} pages)")
                        merger.append(str(p))
                    except Exception as e:
                        print(f"✗ CORRUPTED: {e}")
                        print(f"   ⚠️  Skipping corrupted file: {Path(p).name}")
                        continue
            merger.write(str(self.pdf_path))
            merger.close()
            print(f"\n✅ Final: {self.pdf_path}")
            for p in paths:
                try: Path(p).unlink()
                except: pass
            return self.pdf_path
        except Exception as e:
            print(f"❌ Merge failed: {e}")
            return None
    
    async def generate_complete_pdf(self) -> Optional[Path]:
        print("\n" + "="*80 + "\n🚀 PDF GENERATION\n" + "="*80)
        self.load_data()
        
        # Only process sections that exist in the data
        available_sections = sorted([int(k.replace('section_', '')) for k in self.data.get('sections', {}).keys()])
        
        if not available_sections:
            print("❌ No sections found in data file!")
            return None
        
        print(f"\n📋 Processing {len(available_sections)} sections: {available_sections}\n")
        
        async with (
            DefaultAzureCredential() as cred,
            AzureAIAgentClient(credential=cred, project_endpoint=PROJECT_ENDPOINT) as client,
            ChatAgent(chat_client=client, name="PDFAgent",
                     instructions=PDF_AGENT_INSTRUCTIONS,
                     tools=[HostedCodeInterpreterTool()]) as agent
        ):
            paths = []
            for idx, sec_id in enumerate(available_sections, 1):
                sec_id_str = str(sec_id)
                # Only process if section exists in SECTIONS config AND in data
                if sec_id_str in SECTIONS and f"section_{sec_id_str}" in self.data.get('sections', {}):
                    path = await self.generate_section_pdf(agent, client, sec_id_str, idx==1)
                    if path:
                        paths.append(path)
                    if idx < len(available_sections):
                        print(f"\n⏳ Waiting 30s...\n")
                        time.sleep(30)
                else:
                    print(f"⚠️  Skipping section {sec_id} (not configured or no data)")
            
            if paths:
                return self.merge_pdfs(paths)
        return None

async def main():
    base_dir = Path(__file__).parent
    # Primary file is frontend/public/pitchbook_final_output.txt
    files = [
        base_dir / "frontend" / "public" / "pitchbook_final_output.txt",
        base_dir / "pitchbook_final_output.txt",
        base_dir / "pitchbook_complete_output.txt",
        base_dir / "output.txt"
    ]
    
    output_file = next((f for f in files if f.exists()), None)
    
    if not output_file:
        print("❌ Output file not found!")
        print(f"   Searched in: {[str(f) for f in files]}")
        return
    
    print(f"✓ Using data file: {output_file}")
    
    generator = PitchbookPDFGenerator(
        output_file=str(output_file),
        output_dir=base_dir / "output"
    )
    
    pdf_path = await generator.generate_complete_pdf()
    
    if pdf_path:
        print(f"\n✅ SUCCESS: {pdf_path}")
    else:
        print("\n❌ FAILED")

if __name__ == "__main__":
    asyncio.run(main())

