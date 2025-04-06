# GPT Researcher Prompt Engineering Guide

## Table of Contents
- [GPT Researcher Prompt Engineering Guide](#gpt-researcher-prompt-engineering-guide)
  - [Table of Contents](#table-of-contents)
  - [Execution Paths in GPT Researcher](#execution-paths-in-gpt-researcher)
    - [Main Execution Paths](#main-execution-paths)
    - [Report Type Paths](#report-type-paths)
    - [Research Source Paths](#research-source-paths)
    - [Modifying Workflow Paths](#modifying-workflow-paths)
    - [Specific Prompt Modifications by Path](#specific-prompt-modifications-by-path)
      - [LinkedIn Post Generation](#linkedin-post-generation)
      - [Deep Research Report](#deep-research-report)
      - [Agent Role Customization](#agent-role-customization)
      - [Web Research Query Optimization](#web-research-query-optimization)
  - [1. Search Query Generation](#1-search-query-generation)
    - [1.1 Search Queries Prompt](#11-search-queries-prompt)
  - [2. Report Generation Prompts](#2-report-generation-prompts)
    - [2.1 Main Report Prompt](#21-main-report-prompt)
    - [2.2 Resource Report Prompt](#22-resource-report-prompt)
    - [2.3 Outline Report Prompt](#23-outline-report-prompt)
    - [2.4 Deep Research Prompt](#24-deep-research-prompt)
    - [2.5 Report Introduction Prompt](#25-report-introduction-prompt)
    - [2.6 Report Conclusion Prompt](#26-report-conclusion-prompt)
  - [3. Content Refinement Prompts](#3-content-refinement-prompts)
    - [3.1 Source Curation Prompt](#31-source-curation-prompt)
    - [3.2 Draft Section Titles Prompt](#32-draft-section-titles-prompt)
    - [3.3 Subtopics Generation Prompt](#33-subtopics-generation-prompt)
    - [3.4 Subtopic Report Prompt](#34-subtopic-report-prompt)
  - [4. Agent Prompts](#4-agent-prompts)
    - [4.1 Auto Agent Instructions](#41-auto-agent-instructions)
  - [5. Summary Prompts](#5-summary-prompts)
    - [5.1 Summary Prompt](#51-summary-prompt)
  - [6. Implementation in Action Files](#6-implementation-in-action-files)
    - [6.1 Report Generation Action](#61-report-generation-action)
    - [6.2 Introduction Generation Action](#62-introduction-generation-action)
    - [6.3 Conclusion Generation Action](#63-conclusion-generation-action)
  - [Key Findings](#key-findings)
  - [Modification Strategy](#modification-strategy)

This document provides a comprehensive breakdown of all prompts used in the core GPT-Researcher system (found in the `gpt_researcher` directory), their locations, functions, and how modifications would affect behavior.

## Execution Paths in GPT Researcher

### Main Execution Paths

The GPT Researcher system offers several execution paths depending on how it's invoked:

1. **Web Server (main.py)**: 
   - Primary entry point that starts a FastAPI server 
   - Processes requests through HTTP endpoints or WebSockets
   - Supports multiple report types and formats

2. **CLI Interface (cli.py)**:
   - Command-line interface for direct execution
   - Imports and uses the GPTResearcher class

3. **Direct Import (GPTResearcher class)**:
   - Used in custom applications like the LinkedIn post generator
   - Most flexible approach for programmatic usage

### Report Type Paths

The system supports multiple report types that use different prompt flows:

1. **Basic Report (`ReportType.ResearchReport.value`)**:
   - Uses `generate_report_prompt()` to create single comprehensive reports
   - Entry point: `basic_report.py` → `GPTResearcher.write_report()` → `report_generation.py:generate_report()`
   - Key prompts: search queries prompt, report prompt, source curation prompt

2. **Detailed Report (`ReportType.DetailedReport.value`)**:
   - Creates more structured reports with subtopics and sections
   - Entry point: `detailed_report.py` → hierarchical research flow
   - Additional prompts: subtopics prompt, section titles prompt, introduction/conclusion prompts

3. **Deep Research (`ReportType.DeepResearch.value`)**:
   - Performs extensive hierarchical research with recursive exploration
   - Entry point: `GPTResearcher._handle_deep_research()` → `deep_research.py`
   - Uses specialized `generate_deep_research_prompt()` and recursive search queries

4. **Custom Reports (various formats)**:
   - Resource reports, outline reports, LinkedIn posts generation
   - Each uses specialized prompts like `generate_resource_report_prompt()` or custom formats

### Research Source Paths

The system handles different content sources that affect prompt selection:

1. **Web Research (`ReportSource.Web.value`)**:
   - Conducts internet searches using search APIs (Tavily, etc.)
   - Includes URL citation in prompts
   - Entry point: `ResearchConductor.conduct_research()` → web search flow

2. **Document Research (`ReportSource.Documents.value`)**:
   - Analyzes local documents or uploaded files
   - Modified citation format in prompts
   - Entry point: `ContextManager` handles document loading/processing

3. **Vector Store Research**:
   - Uses pre-embedded knowledge from vector databases
   - Entry point: `VectorStoreWrapper` handles retrieval

### Modifying Workflow Paths

To modify the behavior of these execution paths:

1. **Changing Search Strategy**:
   - Modify `generate_search_queries_prompt()` to alter how queries are constructed
   - Adjust parameters in `research_conductor.py` like search depth or number of sources

2. **Altering Report Structure and Format**:
   - Customize report type-specific prompts in `prompts.py`
   - Customize report type-specific prompts in `linkedin_prompts.py`
   - Modify `generate_report()` function parameters (tone, word count, format)

3. **Customizing Agent Roles**:
   - Update `auto_agent_instructions()` to change how agent roles are selected
   - Modify the role descriptions in configuration to alter agent expertise and style

4. **Changing Research Depth and Breadth**:
   - For deep research: adjust breadth/depth parameters in `DeepResearchSkill`
   - For basic research: modify the number of search queries or source limits

5. **Custom Applications (like LinkedIn Generator)**:
   - Create specialized report formats by extending the existing prompts
   - Example: LinkedIn generator uses the standard research flow but with social media-optimized output formatting

### Specific Prompt Modifications by Path

Here are concrete examples of how to modify prompts for specific paths:

#### LinkedIn Post Generation

The LinkedIn post generator (as seen in `linkedin_generator.py`) uses this workflow:
1. Initializes `GPTResearcher` with `ReportType.ResearchReport.value` and `report_source="web"`
2. Calls `conduct_research()` to gather information
3. Calls `write_report()` to generate posts

To optimize for LinkedIn content:
```python
# In prompts.py, and linkedin_prompts.py you could modify the report prompt:
def generate_report_prompt(
    question: str,
    context,
    report_source: str,
    report_format="apa",
    total_words=1000,
    tone=None,
    language="english",
):
    # Specialized for LinkedIn
    return f"""
Using the information: "{context}"
Create 3 different LinkedIn post options about: "{question}"

Each LinkedIn post should:
1. Be between 800-1200 characters (approximately 150-225 words)
2. Start with a strong hook to capture attention
3. Include one key statistic, insight, or data point from the research
4. End with a thought-provoking question or call-to-action
5. Include 3-5 relevant hashtags
6. {tone_prompt}

Format each post option as:
POST 1:
[The complete post content]

POST 2:
[The complete post content]

POST 3:
[The complete post content]
"""
```

#### Deep Research Report

For deep research with more comprehensive coverage:
```python
# In prompts.py and linkedin_prompts.py
def generate_deep_research_prompt(
    question: str,
    context: str,
    report_source: str,
    report_format="apa",
    tone=None,
    total_words=3000,  # Increased word count
    language: str = "english"
):
    return f"""
Based on the hierarchical research data: "{context}"
Generate a comprehensive report addressing: "{question}"

Your report must:
1. Present findings in a logical hierarchical structure
2. Analyze connections between subtopics thoroughly
3. Include detailed evidence for each claim
4. Present competing perspectives where applicable
5. Reach a minimum of {total_words} words
6. Include ALL relevant source citations

The report should follow this structure:
1. Executive Summary (brief overview)
2. Introduction (scope, objectives)
3. Methodology (research approach)
4. Findings (hierarchical presentation)
5. Analysis (connections between findings)
6. Implications (significance of findings)
7. Conclusion (synthesis and recommendations)
8. References (all sources cited)
"""
```

#### Agent Role Customization

To create a specialized agent role:
```python
# Modify the choose_agent function behavior by updating auto_agent_instructions()
def auto_agent_instructions():
    return """
Based on the research task, select the MOST suitable AI agent role from the options below:

- Data Scientist: Statistical analysis, trend identification, numerical insights
- Industry Analyst: Market dynamics, competitive landscape, industry evolution
- Academic Researcher: Theoretical foundations, scholarly perspectives, rigorous methodology
- Technical Expert: Practical implementation, technical specifications, how-to guidance
- Futurist: Emerging trends, predictions, long-term implications
- Historian: Historical context, evolution of concepts, longitudinal analysis

NEW SPECIALIZED ROLES:
- SEO Specialist: Search engine optimization, keyword analysis, content strategy
- Product Manager: Market fit, user needs, feature prioritization, roadmap planning
- UX Researcher: User behavior, usability concerns, experience design principles
- Compliance Officer: Regulatory requirements, legal implications, risk assessment

Return ONLY the role name that is most appropriate.
"""
```

#### Web Research Query Optimization

To improve web search quality:
```python
# Modify the search queries prompt for better precision
def generate_search_queries_prompt(
    question: str,
    parent_query: str,
    report_type: str,
    max_iterations: int = 5,  # Increased from 3
    context: List[Dict[str, Any]] = [],
):
    return f"""
Generate {max_iterations} highly specific search queries about: "{question}"

Your queries should:
1. Use precise terminology relevant to the domain
2. Include specific qualifiers (e.g., years, version numbers, technical terms)
3. Target diverse aspects (statistics, case studies, expert opinions, methodologies)
4. Use advanced search operators when helpful (site:, filetype:, etc.)
5. Focus on authoritative sources (academic, industry, government)

Assume the current date is {datetime.now(timezone.utc).strftime('%B %d, %Y')}

You must respond with a list of strings: ["query 1", "query 2", ...]
"""
```

## 1. Search Query Generation

### 1.1 Search Queries Prompt
- **Location**: `gpt_researcher/prompts.py:generate_search_queries_prompt()`
  - **Location**: `gpt_researcher/linkedin_prompts.py:generate_search_queries_prompt()`
- **Description**: Generates search queries to find relevant information for a research task.
- **Components**:
  - Dynamic context inclusion for real-time web information
  - Specific formatting instructions for the output (list of strings)
  - Current date information for time-sensitive queries
- **How Modification Affects Behavior**:
  - Changing the number of queries (`max_iterations`) affects research breadth
  - Modifying the context handling affects how real-time information shapes queries
  - Adjusting search query specificity affects what content is discovered

## 2. Report Generation Prompts

### 2.1 Main Report Prompt
- **Location**: `gpt_researcher/prompts.py:generate_report_prompt()`
- **Location**: `gpt_researcher/linkedin_prompts.py:generate_report_prompt()`
- **Description**: Creates a comprehensive research report based on collected information.
- **Components**:
  - Research context and original query
  - Detailed guidelines for report structure and formatting
  - Source citation instructions based on report_source
  - Tone setting for report style
- **How Modification Affects Behavior**:
  - Changing citation requirements affects academic rigor
  - Modifying formatting guidelines changes report presentation
  - Adjusting tone parameters changes writing style
  - Changing word count requirements affects detail level

### 2.2 Resource Report Prompt
- **Location**: `gpt_researcher/prompts.py:generate_resource_report_prompt()`
- **Location**: `gpt_researcher/linkedin_prompts.py:generate_resource_report_prompt()`
- **Description**: Generates bibliography-focused report analyzing recommended resources.
- **Components**:
  - Focus on resource evaluation and relevance
  - Source citation format instructions
  - Specific formatting for bibliography entries
- **How Modification Affects Behavior**:
  - Adjusting evaluation criteria changes how sources are assessed
  - Modifying citation format affects reference style
  - Changing relevance parameters affects source selection

### 2.3 Outline Report Prompt
- **Location**: `gpt_researcher/prompts.py:generate_outline_report_prompt()`
- **Location**: `gpt_researcher/linkedin_prompts.py:generate_outline_report_prompt()`
- **Description**: Creates a structured outline framework for a research report.
- **Components**:
  - Instructions for markdown formatting
  - Section/subsection structure guidelines
  - Framework for key points
- **How Modification Affects Behavior**:
  - Changing structure guidance affects outline organization
  - Modifying detail requirements affects outline depth
  - Adjusting markdown formatting changes presentation

### 2.4 Deep Research Prompt
- **Location**: `gpt_researcher/prompts.py:generate_deep_research_prompt()`
- **Location**: `gpt_researcher/linkedin_prompts.py:generate_deep_research_prompt()`
- **Description**: Specialized prompt for handling hierarchical research with detailed citations.
- **Components**:
  - Hierarchical research context handling
  - Detailed citation requirements
  - Advanced structure for complex topics
- **How Modification Affects Behavior**:
  - Changing hierarchical handling affects depth relationships
  - Modifying citation approach affects reference quality
  - Adjusting complexity parameters affects detail handling

### 2.5 Report Introduction Prompt
- **Location**: `gpt_researcher/prompts.py:generate_report_introduction()`
- **Location**: `gpt_researcher/linkedin_prompts.py:generate_report_introduction()`
- **Description**: Creates an introduction section for research reports.
- **Components**:
  - Context for the research question
  - Formatting guidelines for introduction
  - Language specification
- **How Modification Affects Behavior**:
  - Changing introduction structure affects how topics are framed
  - Modifying tone parameters affects reader engagement
  - Adjusting formality affects academic style

### 2.6 Report Conclusion Prompt
- **Location**: `gpt_researcher/prompts.py:generate_report_conclusion()`
- **Location**: `gpt_researcher/linkedin_prompts.py:generate_report_conclusion()`
- **Description**: Creates a conclusion section synthesizing research findings.
- **Components**:
  - Instructions for summarizing key findings
  - Guidelines for conclusion structure
  - Parameters for addressing the original query
- **How Modification Affects Behavior**:
  - Changing synthesis requirements affects conclusion quality
  - Modifying the connection to the original query affects relevance
  - Adjusting recommendation guidance affects practical applications

## 3. Content Refinement Prompts

### 3.1 Source Curation Prompt
- **Location**: `gpt_researcher/prompts.py:curate_sources()`
- **Location**: `gpt_researcher/linkedin_prompts.py:curate_sources()`
- **Description**: Evaluates and curates scraped content prioritizing relevance and quality.
- **Components**:
  - Detailed evaluation guidelines for sources
  - Prioritization criteria for content selection
  - Content retention parameters
- **How Modification Affects Behavior**:
  - Changing relevance criteria affects what sources are included
  - Modifying prioritization factors affects content balance
  - Adjusting retention parameters affects information preservation

### 3.2 Draft Section Titles Prompt
- **Location**: `gpt_researcher/prompts.py:generate_draft_titles_prompt()`
- **Location**: `gpt_researcher/linkedin_prompts.py:generate_draft_titles_prompt()`
- **Description**: Generates section titles for a subtopic within a larger research task.
- **Components**:
  - Context for subtopic positioning
  - Guidelines for title creation and organization
  - Parameters for title specificity
- **How Modification Affects Behavior**:
  - Changing specificity requirements affects section focus
  - Modifying organization guidelines affects report structure
  - Adjusting subtopic handling affects relationships between sections

### 3.3 Subtopics Generation Prompt
- **Location**: `gpt_researcher/prompts.py:generate_subtopics_prompt()`
- **Location**: `gpt_researcher/linkedin_prompts.py:generate_subtopics_prompt()`
- **Description**: Identifies key subtopics for a research task to create a structured approach.
- **Components**:
  - Instructions for breaking down complex topics
  - Guidelines for subtopic selection
  - Parameters for subtopic relevance
- **How Modification Affects Behavior**:
  - Changing decomposition approach affects research organization
  - Modifying selection criteria affects content coverage
  - Adjusting relevance parameters affects subtopic focus

### 3.4 Subtopic Report Prompt
- **Location**: `gpt_researcher/prompts.py:generate_subtopic_report_prompt()`
- **Location**: `gpt_researcher/linkedin_prompts.py:generate_subtopic_report_prompt()`
- **Description**: Creates a report for a specific subtopic within larger research.
- **Components**:
  - Context for how subtopic fits into main research
  - Existing content integration instructions
  - Formatting for subtopic-specific content
- **How Modification Affects Behavior**:
  - Changing context integration affects narrative flow
  - Modifying existing content handling affects consistency
  - Adjusting subtopic formatting affects readability

## 4. Agent Prompts

### 4.1 Auto Agent Instructions
- **Location**: `gpt_researcher/prompts.py:auto_agent_instructions()`
- **Location**: `gpt_researcher/linkedin_prompts.py:auto_agent_instructions()`
- **Description**: Provides instructions for automatically selecting an appropriate agent role.
- **Components**:
  - Task analysis parameters
  - Agent role selection criteria
  - Output format requirements
- **How Modification Affects Behavior**:
  - Changing role criteria affects agent personality selection
  - Modifying task analysis affects role-task matching
  - Adjusting reasoning requirements affects decision quality

## 5. Summary Prompts

### 5.1 Summary Prompt
- **Location**: `gpt_researcher/prompts.py:generate_summary_prompt()`
- **Location**: `gpt_researcher/linkedin_prompts.py:generate_summary_prompt()`
- **Description**: Creates concise summaries of research content.
- **Components**:
  - Guidelines for information distillation
  - Structure for summaries
  - Priority factors for content selection
- **How Modification Affects Behavior**:
  - Changing distillation parameters affects summary length
  - Modifying priority factors affects what information is preserved
  - Adjusting structure affects summary readability

## 6. Implementation in Action Files

### 6.1 Report Generation Action
- **Location**: `gpt_researcher/actions/report_generation.py:generate_report()`
- **Description**: Implements the actual report generation using the appropriate prompt.
- **Components**:
  - Prompt selection based on report type
  - Agent role context
  - LLM parameter configuration
- **How Modification Affects Behavior**:
  - Changing temperature affects creativity/consistency balance
  - Modifying token limits affects report length
  - Adjusting model selection affects output quality

### 6.2 Introduction Generation Action
- **Location**: `gpt_researcher/actions/report_generation.py:write_report_introduction()`
- **Description**: Implements introduction generation using the introduction prompt.
- **Components**:
  - Agent role context
  - Introduction prompt application
  - LLM streaming configuration
- **How Modification Affects Behavior**:
  - Changing temperature affects introduction style
  - Modifying agent role affects introduction tone
  - Adjusting token limits affects introduction depth

### 6.3 Conclusion Generation Action
- **Location**: `gpt_researcher/actions/report_generation.py:write_conclusion()`
- **Description**: Implements conclusion generation using the conclusion prompt.
- **Components**:
  - Agent role context
  - Conclusion prompt application
  - LLM configuration
- **How Modification Affects Behavior**:
  - Changing temperature affects conclusion style
  - Modifying agent role affects conclusion authority
  - Adjusting token limits affects conclusion comprehensiveness

## Key Findings

1. **Centralized Prompt Architecture**: All main prompts are defined in a centralized `prompts.py` file, making modification easier.

2. **Function-Based Design**: Prompts are implemented as functions with parameters, allowing dynamic content insertion.

3. **Hierarchical Research Approach**: The system uses a sophisticated hierarchy of prompts for different levels of research (main query → subtopics → sections).

4. **High Customization**: Prompts include parameters for tone, language, format, and source handling for extensive customization.

5. **Quality Control Mechanisms**: Multiple prompts focus on evaluation, curation, and refinement of content.

6. **Content Source Adaptability**: Different prompt variations exist based on whether content comes from web, local files, or vector stores.

## Modification Strategy

To modify GPT Researcher behavior:

1. **Research Direction**: Adjust `generate_search_queries_prompt()` to change how the system explores topics.

2. **Output Quality**: Modify the report generation prompts to change structure, detail level, and formatting.

3. **Source Handling**: Change `curate_sources()` to adjust how the system evaluates and prioritizes information.

4. **Research Depth**: Modify hierarchical handling in deep research and subtopic prompts to change exploration depth.

5. **Agent Personality**: Adjust agent role selection criteria for different research approaches.

The centralized prompt architecture makes targeted modifications straightforward, and the function-based design allows for extensive parameter customization without changing the core prompts themselves. 