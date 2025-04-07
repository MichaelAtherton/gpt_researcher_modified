from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

def generate_search_queries_prompt(
    question: str,
    parent_query: str,
    report_type: str,
    max_iterations: int = 3,
    context: List[Dict[str, Any]] = [],
):
    """Generates the search queries prompt for the given question.
    Args:
        question (str): The question to generate the search queries prompt for
        parent_query (str): The main question (only relevant for detailed reports)
        report_type (str): The report type
        max_iterations (int): The maximum number of search queries to generate
        context (str): Context for better understanding of the task with realtime web information

    Returns: str: The search queries prompt for the given question
    """

    if (
        report_type == ReportType.DetailedReport.value
        or report_type == ReportType.SubtopicReport.value
    ):
        task = f"{parent_query} - {question}"
    else:
        task = question

    context_prompt = f"""
You are a seasoned research assistant tasked with generating search queries to find relevant information for the following task: "{task}".
Context: {context}

Use this context to inform and refine your search queries. The context provides real-time web information that can help you generate more specific and relevant queries. Consider any current events, recent developments, or specific details mentioned in the context that could enhance the search queries.
""" if context else ""

    dynamic_example = ", ".join([f'"query {i+1}"' for i in range(max_iterations)])

    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    today_str = today.strftime('%B %d, %Y')
    yesterday_str = yesterday.strftime('%B %d, %Y')

    return f"""Write {max_iterations} specific search queries to find the MOST RECENT information (from the last 24-48 hours) about: "{task}"

Your goal is to discover NEW developments, updates, or changes that have occurred within the last day or two.

IMPORTANT: 
- Focus exclusively on recent information (published on {yesterday_str} or {today_str})
- Include date limiters in your queries where appropriate (e.g., "last 24 hours", "today", "since {yesterday_str}")
- Target news sources, recent updates, and time-sensitive information
- Aim to discover what has CHANGED or is NEW about this topic

Assume the current date is {today_str}.

{context_prompt}
You must respond with a list of strings in the following format: [{dynamic_example}].
The response should contain ONLY the list.
""" 

def generate_report_prompt(
    question: str,
    context,
    report_source: str,
    report_format="apa",
    total_words=1000,
    tone=None,
    language="english",
    previous_report="",
):
    """Generates the daily intelligence briefing prompt for the given question and research.
    Args: 
        question (str): The question/topic to generate the intelligence briefing for
        context (str): The research data to generate the briefing from
        report_source (str): The source of the research data
        report_format (str): The format of the report
        total_words (int): The minimum word count for the report
        tone (Tone): The tone of the report
        language (str): The language to write the report in
        previous_report (str): The previous day's report content (if available)
    Returns: str: The intelligence briefing prompt
    """

    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f"""
You MUST write all used source urls at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each.
Every url should be hyperlinked: [url website](url)
Additionally, you MUST include hyperlinks to the relevant URLs wherever they are referenced in the report: 

eg: Author, A. A. (Year, Month Date). Title of web page. Website Name. [url website](url)
"""
    else:
        reference_prompt = f"""
You MUST write all used source document names at the end of the report as references, and make sure to not add duplicated sources, but only one reference for each."
"""

    tone_prompt = f"Write the report in a {tone.value} tone." if tone else "Write the report in a concise, executive-friendly tone that focuses on business implications."
    
    previous_report_comparison = ""
    if previous_report:
        previous_report_comparison = f"""
CRITICAL - AVOID DUPLICATION:
Previous report content is provided below. You MUST NOT repeat information that was already covered in this previous report unless it's necessary for context. Focus exclusively on what is NEW since this report was created.

Previous Report:
---
{previous_report}
---

In your report, include a specific section called "NEW DEVELOPMENTS" that explicitly highlights what has changed since the previous report.
"""

    today = datetime.now(timezone.utc)
    today_str = today.strftime('%B %d, %Y')

    return f"""
Information: "{context}"
---
Using the above information from {today_str}, prepare a DAILY INTELLIGENCE BRIEFING on: "{question}"

{previous_report_comparison}

This intelligence briefing is for a CEO who needs actionable insights on recent developments. The briefing should:

1. Focus EXCLUSIVELY on NEW information and developments from the LAST 24-48 HOURS
2. Highlight CHANGES, TRENDS, and EMERGING issues since the last briefing
3. Provide CLEAR, ACTIONABLE insights that offer competitive advantage
4. Analyze potential BUSINESS IMPLICATIONS of these developments
5. Be well-structured, concise, and approximately {total_words} words

FORMAT REQUIREMENTS:
- Create a "KEY HIGHLIGHTS" section at the top with 3-5 bullet points of the most important new developments
- Use a "NEW DEVELOPMENTS" section to detail what has changed since the previous report
- If relevant, include a "MARKET MOVEMENTS" section for any significant changes in relevant metrics
- Include an "ACTIONABLE INSIGHTS" section with specific recommendations
- Use clear, scannable headings and bullet points where appropriate
- Present information in order of business importance, not chronologically
- {tone_prompt}
- Write in markdown format and {report_format} citation style

INTELLIGENCE STANDARDS:
- VERIFY contradictory information and address discrepancies
- PRIORITIZE authoritative and reliable sources
- NOTE levels of certainty/uncertainty for each insight
- DISTINGUISH between facts, analysis, and speculation
- {reference_prompt}

You MUST write the report in the following language: {language}.
Assume that the current date is {today_str}.
""" 

def curate_sources(query, sources, max_results=10, previous_report=""):
    """Curates sources for a daily intelligence briefing.
    
    Args:
        query (str): The research query
        sources (list): The sources to curate
        max_results (int): The maximum number of sources to return
        previous_report (str): Previous report content to avoid duplication
        
    Returns:
        str: The prompt for curating sources
    """
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)
    
    return f"""Your goal is to evaluate and curate the provided scraped content for the DAILY INTELLIGENCE BRIEFING on: "{query}" 
    while STRICTLY PRIORITIZING RECENT INFORMATION (published within the last 24-48 hours).

CRITICAL: The content will be used for a CEO's daily intelligence briefing that focuses EXCLUSIVELY on NEW developments.

EVALUATION CRITERIA (in priority order):
1. RECENCY: 
   - Content from {yesterday.strftime('%B %d, %Y')} or {today.strftime('%B %d, %Y')} gets HIGHEST priority
   - Older content is ONLY included if it contains critical information not available in newer sources
   - Discard any information older than 48 hours unless it's absolutely essential context

2. NOVELTY:
   - Information that represents NEW developments, changes, or updates gets highest priority
   - Information that was likely covered in previous reports is DEPRIORITIZED
   - If previous report content is provided, avoid duplicating information already covered

3. BUSINESS RELEVANCE:
   - Prioritize content with clear business implications, competitive intelligence, or actionable insights
   - Focus on information a CEO would find valuable for decision-making
   - Quantitative data, metrics, and concrete facts are especially valuable

4. SOURCE QUALITY:
   - Favor authoritative business, industry, and news sources
   - Prioritize primary sources over commentary
   - Seek a balance of perspectives when appropriate

PREVIOUS REPORT AWARENESS:
{f"Review this previous report content to AVOID selecting sources that cover the same information:" + previous_report if previous_report else "No previous report available, but still focus on finding the NEWEST information only."}

SOURCES LIST TO EVALUATE:
{sources}

You MUST return your response in the EXACT sources JSON list format as the original sources.
The response MUST not contain any markdown format or additional text (like ```json), just the JSON list!
""" 

def generate_daily_intelligence_briefing(
    question: str,
    context,
    report_source: str,
    report_format="apa",
    total_words=1000,
    tone=None,
    language="english",
    previous_report="",
):
    """Generates a specialized daily intelligence briefing focused on recent developments.
    
    Args:
        question (str): The topic to generate the briefing for
        context (str): The research context
        report_source (str): The source of the research
        report_format (str): The format of the report
        total_words (int): The target word count
        tone (Tone): The tone of the report
        language (str): The language of the report
        previous_report (str): Previous report content to avoid duplication
        
    Returns:
        str: The daily intelligence briefing prompt
    """
    
    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = """
You MUST write all used source urls at the end of the report as references.
Every url should be hyperlinked: [url website](url)
Additionally, include hyperlinks to the relevant URLs wherever they are referenced in the report.
"""
    else:
        reference_prompt = """
You MUST write all used source document names at the end of the report as references.
"""

    tone_prompt = f"Write the report in a {tone.value} tone." if tone else "Write the report in a decisive, action-oriented executive tone."
    
    previous_report_comparison = ""
    if previous_report:
        previous_report_comparison = f"""
CRITICAL - AVOID DUPLICATION:
Previous report content is provided below. You MUST NOT repeat information that was already covered in this previous report unless it's necessary for context. Focus exclusively on what is NEW since this report was created.

Previous Report:
{previous_report}

In your report, include a specific section called "NEW DEVELOPMENTS" that explicitly highlights what has changed since the previous report.
"""

    today = datetime.now(timezone.utc)
    today_str = today.strftime('%B %d, %Y')

    return f"""
Information: "{context}"
---
Using the above information from {today_str}, prepare an EXECUTIVE DECISION SUPPORT BRIEFING on: "{question}"

{previous_report_comparison}

This briefing is for a CEO who needs to make immediate strategic decisions. The briefing MUST:

1. EXECUTIVE SUMMARY (Top of Report):
   - 3-5 bullet points of CRITICAL developments requiring immediate attention
   - Clear "GO/NO-GO" recommendations for each point
   - Risk level (High/Medium/Low) for each decision point

2. For EACH Major Trend/Development:
   a) COMPETITIVE INTELLIGENCE
      - Which competitors are already moving on this
      - Market share impact if we act/don't act
      - First-mover advantage window
      - Defensive strategies needed
   
   b) FINANCIAL IMPACT
      - Implementation cost ranges
      - Expected ROI timeframes
      - Resource requirements
      - Risk-adjusted return estimates
   
   c) ACTION PLAN
      - Immediate Actions (Next 30 days)
      - Strategic Moves (90-day plan)
      - Success Metrics to Track
      - Key Performance Indicators (KPIs)

3. RISK ANALYSIS
   - Opportunity cost of delay
   - Competitive threats
   - Implementation challenges
   - Mitigation strategies

FORMAT REQUIREMENTS:
- Create a "DECISION REQUIRED" section for items needing immediate CEO attention
- Use clear, decisive language focused on actions and outcomes
- Present information in order of urgency and impact
- Include specific metrics and timelines
- {tone_prompt}
- Write in markdown format and {report_format} citation style

INTELLIGENCE STANDARDS:
- VERIFY all competitive intelligence claims
- PRIORITIZE quantifiable data over qualitative assessments
- NOTE certainty levels for predictions and estimates
- DISTINGUISH between verified facts and market speculation
- {reference_prompt}

You MUST write the report in the following language: {language}.
Assume that the current date is {today_str}.
"""

# Update the report_type_mapping to include our new report type
report_type_mapping = {
    ReportType.ResearchReport.value: generate_report_prompt,
    ReportType.ResourceReport.value: generate_resource_report_prompt,
    ReportType.OutlineReport.value: generate_outline_report_prompt,
    ReportType.CustomReport.value: generate_custom_report_prompt,
    ReportType.SubtopicReport.value: generate_subtopic_report_prompt,
    ReportType.DeepResearch.value: generate_deep_research_prompt,
    "daily_intelligence_briefing": generate_daily_intelligence_briefing,
} 

def generate_summary_prompt(query, data, previous_report=""):
    """Generates the summary prompt for the given question and text.
    Args: 
        query (str): The question to generate the summary prompt for
        data (str): The text to generate the summary prompt for
        previous_report (str): Previous report content to avoid duplication
    Returns: 
        str: The summary prompt for the given question and text
    """
    previous_content_prompt = ""
    if previous_report:
        previous_content_prompt = f"""
IMPORTANT: Below is the content of a previous report on this topic. 
DO NOT summarize information that is already covered in this previous report unless it's essential for context.
FOCUS exclusively on identifying NEW information, updates, or changes.

PREVIOUS REPORT:
---
{previous_report}
---
"""

    return f"""
{previous_content_prompt}
Your task is to extract and summarize ONLY the NEWEST and MOST RELEVANT information from the following text in relation to this query: "{query}"

TEXT TO ANALYZE:
{data}

SUMMARY REQUIREMENTS:
1. FOCUS exclusively on information that appears to be from the last 24-48 hours
2. PRIORITIZE information with business relevance, competitive intelligence value, and actionable insights
3. EXTRACT specific facts, figures, statistics, and quantitative data
4. HIGHLIGHT changes, trends, and developments that would interest a CEO
5. IGNORE general background information that isn't time-sensitive
6. CAPTURE the most important quotes from key figures or organizations
7. PRESERVE source attribution for key facts and claims
8. SPECIFY publication dates of information when available

IF the text contains no recent or relevant information for this query, briefly state that no significant new developments were found.

Your summary should provide clear business intelligence that could offer competitive advantage.
""" 