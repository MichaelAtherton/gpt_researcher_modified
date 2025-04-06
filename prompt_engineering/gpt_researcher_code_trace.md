# GPT Researcher Code Trace Guide

## Table of Contents
- [GPT Researcher Code Trace Guide](#gpt-researcher-code-trace-guide)
  - [Table of Contents](#table-of-contents)
  - [Entry Points and Core Components](#entry-points-and-core-components)
    - [Primary Entry Points](#primary-entry-points)
    - [Core Structure Exploration Path](#core-structure-exploration-path)
  - [Prompt System Architecture](#prompt-system-architecture)
    - [Prompt Definition Location](#prompt-definition-location)
    - [Key Prompt Functions](#key-prompt-functions)
    - [Prompt Usage Path](#prompt-usage-path)
  - [Agent System](#agent-system)
    - [Agent Selection and Creation](#agent-selection-and-creation)
    - [Skills and Components](#skills-and-components)
  - [Action Points for Modification](#action-points-for-modification)
    - [Creating a New Agent Role](#creating-a-new-agent-role)
    - [Adding a New Report Type](#adding-a-new-report-type)
    - [Modifying Search Behavior](#modifying-search-behavior)
    - [Custom Output Format (e.g., LinkedIn posts)](#custom-output-format-eg-linkedin-posts)
  - [Multi-Agent System Integration](#multi-agent-system-integration)
  - [Configuration and Environment](#configuration-and-environment)
  - [Implementation Examples](#implementation-examples)
  - [Key Relationship Points](#key-relationship-points)
  - [Working with Multiple Prompt Files](#working-with-multiple-prompt-files)
    - [Key Import Locations](#key-import-locations)
    - [Adding a New Prompts File](#adding-a-new-prompts-file)
    - [Best Practices for Prompt File Management](#best-practices-for-prompt-file-management)
  - [Creating Custom Entry Points](#creating-custom-entry-points)
    - [Entry Point and Prompt File Relationship](#entry-point-and-prompt-file-relationship)
    - [Steps to Create a New Application](#steps-to-create-a-new-application)
    - [Example: LinkedIn Generator Analysis](#example-linkedin-generator-analysis)
    - [Entry Point Configuration Guide](#entry-point-configuration-guide)

This document serves as a navigational map to help you understand the GPT Researcher codebase structure, allowing you to modify prompts, create new agents, and develop custom workflows.

## Entry Points and Core Components

### Primary Entry Points
1. **Server Entry Point**: `/main.py`
   - Starts a FastAPI server
   - Connects to `/backend/server/server.py` for endpoint handling

2. **Programmatic Entry Point**: `/gpt_researcher/agent.py`
   - Contains `GPTResearcher` class definition
   - Main interface for programmatic interactions

3. **CLI Entry Point**: `/cli.py`
   - Command-line interface implementation

### Core Structure Exploration Path

To understand the core functionality, follow this sequence:

1. **Begin at the Class Definition**: 
   - `/gpt_researcher/__init__.py` → imports from `agent.py`
   - `/gpt_researcher/agent.py` → defines `GPTResearcher` class

2. **Research Flow**: 
   - `GPTResearcher.conduct_research()` → triggers research process
   - `GPTResearcher.write_report()` → generates output

3. **API Handler**:
   - `/backend/server/websocket_manager.py` → contains `run_agent()` function
   - Pay attention to how `run_agent()` initializes different report types

4. **Report Types**:
   - `/backend/report_type/basic_report/basic_report.py`
   - `/backend/report_type/detailed_report/detailed_report.py`
   - `/backend/report_type/deep_research/main.py`

## Prompt System Architecture

### Prompt Definition Location
- **Primary Location**: `/gpt_researcher/prompts.py`
  - Contains all prompt template functions
  - Organized by output type (e.g., search queries, reports, etc.)

### Key Prompt Functions

1. **Search Query Generation**: 
   - `generate_search_queries_prompt()` → creates queries for web searches

2. **Report Generation**:
   - `generate_report_prompt()` → standard research report
   - `generate_resource_report_prompt()` → bibliography-style report
   - `generate_outline_report_prompt()` → structural outline
   - `generate_deep_research_prompt()` → comprehensive hierarchical report
   - `generate_custom_report_prompt()` → for user-defined formats

3. **Component Prompts**:
   - `generate_report_introduction()` → report introductions
   - `generate_report_conclusion()` → report conclusions
   - `curate_sources()` → evaluates source quality
   - `generate_subtopics_prompt()` → breaks down complex topics

### Prompt Usage Path

1. **Prompt → Action Flow**:
   - Prompts defined in `prompts.py`
   - Used in `/gpt_researcher/actions/report_generation.py`
   - Example: `generate_report()` function uses prompts via `get_prompt_by_report_type()`

2. **Report Type Selection**:
   - `/gpt_researcher/utils/enum.py` → defines `ReportType` and `ReportSource` enums
   - These enums determine which prompts are used in different contexts

## Agent System

### Agent Selection and Creation
- `/gpt_researcher/actions/agent_creator.py` → contains `choose_agent()`
- Look at how `auto_agent_instructions()` in `prompts.py` guides agent selection

### Skills and Components
Each skill represents a specific capability:

1. **Researcher Skill**: `/gpt_researcher/skills/researcher.py`
   - `ResearchConductor` class orchestrates the research process

2. **Writer Skill**: `/gpt_researcher/skills/writer.py`
   - `ReportGenerator` class creates reports using prompts

3. **Browser Manager**: `/gpt_researcher/skills/browser.py`
   - Handles web content retrieval

4. **Context Manager**: `/gpt_researcher/skills/context_manager.py`
   - Manages research context and embedding

5. **Source Curator**: `/gpt_researcher/skills/curator.py`
   - Filters and prioritizes sources

6. **Deep Research Skill**: `/gpt_researcher/skills/deep_research.py`
   - Handles recursive, hierarchical research

## Action Points for Modification

### Creating a New Agent Role
1. **Edit Agent Instructions**: 
   - Modify `auto_agent_instructions()` in `prompts.py`
   - Add new role definitions to the selection options

2. **Configuration Update**:
   - Update configurations in `gpt_researcher/config/config.py`

### Adding a New Report Type
1. **Enum Definition**:
   - Add new enum value in `/gpt_researcher/utils/enum.py`

2. **Create Prompt Function**:
   - Add a new prompt function in `prompts.py`

3. **Update Prompt Selection**:
   - Modify `get_prompt_by_report_type()` in `prompts.py`

4. **Create Handler**:
   - Add flow in `/backend/report_type/` (following existing patterns)

### Modifying Search Behavior
1. **Query Generation**:
   - Edit `generate_search_queries_prompt()` in `prompts.py`

2. **Search Parameters**:
   - Check `/gpt_researcher/retrievers/` directory for search implementations

### Custom Output Format (e.g., LinkedIn posts)
1. **Report Prompt**:
   - Modify `generate_report_prompt()` in `prompts.py`
   - Or create a specialized prompt function

2. **Output Parsing**:
   - Add formatters in `/gpt_researcher/actions/report_generation.py`

## Multi-Agent System Integration

For integrating with the multi-agent system:

1. **Multi-Agent Entry Point**:
   - `/multi_agents/main.py` → `run_research_task()`

2. **Agent Definitions**:
   - `/multi_agents/agents/` directory
   - `researcher.py` shows how GPTResearcher is used within a larger system

3. **Graph Integration**:
   - `/multi_agents/graphs/research_graph.py`

## Configuration and Environment

Configuration aspects:

1. **Configuration Class**:
   - `/gpt_researcher/config/config.py`
   - Controls LLM models, token limits, etc.

2. **Environment Variables**:
   - `.env.example` shows required API keys
   - `DOC_PATH` determines document storage location

## Implementation Examples

For understanding full implementations of different workflows:

1. **LinkedIn Post Generator**:
   - `/linkedin_generator.py` shows direct usage of GPTResearcher
   - Examples of prompt customization for social media

2. **CLI Example**:
   - `/cli.py` for command-line workflow

3. **Test Examples**:
   - `/tests/` directory for usage patterns
   - `/docs/docs/examples/` for documented examples

## Key Relationship Points

- **Prompts ↔ Actions**: Prompts define what to ask, actions determine when to ask
- **Agent ↔ Skills**: Agent coordinates skills for different capabilities
- **Report Types ↔ Workflows**: Report type selection drives the entire process flow
- **Research Sources ↔ Citations**: Source type affects how citations appear in reports

## Working with Multiple Prompt Files

GPT Researcher can use different prompt files for different use cases. When renaming or adding new prompt files, you'll need to update imports across the codebase.

### Key Import Locations

When adding a new prompts file or modifying an existing one, check these files for imports:

1. **Curator Implementation**:
   - `/gpt_researcher/skills/curator.py`
   - Imports: `from ..linkedin_prompts import curate_sources as rank_sources_prompt`

2. **Query Processing**:
   - `/gpt_researcher/actions/query_processing.py`
   - Imports: `from ..linkedin_prompts import generate_search_queries_prompt`

3. **Report Generation**:
   - `/gpt_researcher/actions/report_generation.py`
   - Imports: 
     ```python
     from ..linkedin_prompts import (
         generate_report_introduction,
         generate_draft_titles_prompt,
         generate_report_conclusion,
         get_prompt_by_report_type,
     )
     ```

4. **LLM Utilities**:
   - `/gpt_researcher/utils/llm.py`
   - Imports: `from ..linkedin_prompts import generate_subtopics_prompt`

5. **Agent Creator**:
   - `/gpt_researcher/actions/agent_creator.py`
   - Imports: `from ..linkedin_prompts import auto_agent_instructions`

### Adding a New Prompts File

When adding a new prompts file (e.g., `my_custom_prompts.py`):

1. **Create the file**: Add it to the base `/gpt_researcher/` directory
2. **Define functions**: Implement the same function signatures as in existing prompt files
3. **Update imports**: Update import statements in the above files to reference your new file

Example workflow:
```python
# 1. Create my_custom_prompts.py with necessary functions
# 2. Update imports in relevant files, e.g. in curator.py:
from ..my_custom_prompts import curate_sources as rank_sources_prompt
# 3. Or use conditional imports based on configuration
```

### Best Practices for Prompt File Management

1. **Maintain function signatures**: Keep the same function names and parameters across different prompt files
2. **Documentation**: Document which prompts file is used by which components
3. **Configuration-based selection**: Consider implementing a configuration parameter to select which prompts file to use
4. **Fallback mechanisms**: Implement fallbacks to default prompts when specialized ones aren't available

By properly managing imports, you can create specialized prompt files for different use cases while maintaining compatibility with the existing codebase architecture.

## Creating Custom Entry Points

Each specialized prompt file typically has a corresponding generator script that serves as an entry point. This pattern allows for customized applications while leveraging the core GPT Researcher infrastructure.

### Entry Point and Prompt File Relationship

The system follows this pattern:
- `linkedin_prompts.py` → `linkedin_generator.py`
- Future examples: `facebook_ads_prompts.py` → `facebook_ads_generator.py`

The prompt file contains templates, while the generator script:
1. Imports the GPTResearcher class
2. Configures it for the specific use case
3. Handles input/output for that specific application

### Steps to Create a New Application

To create a new application (e.g., Facebook Ads generator):

1. **Create a prompts file**:
   ```python
   # facebook_ads_prompts.py in /gpt_researcher/
   # Define specialized prompt functions for ad generation
   ```

2. **Create a generator script**:
   ```python
   # facebook_ads_generator.py in root directory
   import os
   from datetime import datetime
   from dotenv import load_dotenv
   from gpt_researcher.agent import GPTResearcher
   from gpt_researcher.config.config import RetrieverConfig
   from gpt_researcher.types import ReportType, ReportFormat
   
   def main():
       # Setup configs
       # Initialize GPTResearcher
       # Configure for ad generation
       # Execute research and generation
       # Save output to appropriate file
   
   if __name__ == "__main__":
       main()
   ```

3. **Update necessary imports** in core files as documented above

4. **Run your entry point**:
   ```bash
   python facebook_ads_generator.py
   ```

### Example: LinkedIn Generator Analysis

The `linkedin_generator.py` provides a template for creating new generators:

```python
# Key components:
# 1. Configuration setup
load_dotenv(override=True)

# 2. GPTResearcher initialization
researcher = GPTResearcher(
    query=query,
    report_type=ReportType.ResearchReport.value,
    report_format=ReportFormat.Default.value,
    report_source="web",
    retriever_config=retriever_config,
)

# 3. Research execution
researcher.conduct_research()  

# 4. Report generation with custom format
linkedin_posts = researcher.write_report()

# 5. Output handling
output_dir = os.path.join("outputs", "linkedin_posts")
...
```

### Entry Point Configuration Guide

When creating a new generator script:

1. **Import Requirements**:
   - Import the GPTResearcher class
   - Import necessary types and configurations
   - Import dotenv for environment handling

2. **Configuration Options**:
   - Set appropriate ReportType
   - Configure retriever settings
   - Define output paths

3. **Runtime Flow**:
   - Initialize researcher
   - Conduct research
   - Generate specialized content
   - Save to appropriate location

This pattern allows for creating multiple specialized applications while maintaining consistency in the codebase and leveraging the shared research infrastructure.

Follow this map to understand the system architecture and make targeted modifications to prompts, agent behaviors, and workflows.
