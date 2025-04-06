# Multi-Agents System Code Trace Guide

## Table of Contents
1. [System Architecture Overview](#system-architecture-overview)
2. [Agent Interaction Workflow](#agent-interaction-workflow)
3. [Core Agent Explorer Paths](#core-agent-explorer-paths)
4. [Prompt Modification Touchpoints](#prompt-modification-touchpoints)
5. [Creating New Agent Behaviors](#creating-new-agent-behaviors)
6. [Real-World Modification Examples](#real-world-modification-examples)
7. [Output Format Customization](#output-format-customization)
8. [Integration with GPTResearcher](#integration-with-gptresearcher)
9. [Creating Custom Generator Files](#creating-custom-generator-files)

This document serves as a navigational map to help you understand and modify the Multi-Agents system structure, allowing you to create new agent behaviors by modifying prompts and agent interactions.

## System Architecture Overview

The Multi-Agents system uses a team of specialized agents working together in a coordinated workflow:

1. **Core Components Location**:
   - `/multi_agents/` - Root directory for the multi-agent system
   - `/multi_agents/agents/` - Individual agent implementations
   - `/multi_agents/graphs/` - LangGraph workflow definitions
   - `/multi_agents/tasks/` - Task configuration and data structures

2. **Agent Hierarchy**:
   - **EditorAgent**: Plans research structure and coordinates overall direction
   - **ResearchAgent**: Gathers information using the core GPTResearcher
   - **WriterAgent**: Creates content based on research and plan
   - **ReviewerAgent**: Evaluates content quality and suggests improvements
   - **ReviserAgent**: Implements improvements based on reviewer feedback
   - **HumanAgent**: Facilitates human feedback integration
   - **PublisherAgent**: Formats and exports final research products

3. **Key Entry Points**:
   - `/multi_agents/main.py` - Primary entry point and task execution
   - `/multi_agents/graphs/research_graph.py` - Agent workflow definition
   - `/multi_agents/tasks/base.py` - Task configuration

## Agent Interaction Workflow

The agents interact in a sequential workflow with feedback loops:

1. **Initial Flow**:
   ```
   Task Configuration → EditorAgent → ResearchAgent → WriterAgent
   ```

2. **Review Cycle**:
   ```
   WriterAgent → ReviewerAgent → [if feedback] → ReviserAgent → ReviewerAgent
   ```

3. **Finalization**:
   ```
   ReviewerAgent [approved] → PublisherAgent → Final Output
   ```

4. **Human-in-the-Loop Integration**:
   ```
   Any Agent → HumanAgent → Return to Workflow
   ```

## Core Agent Explorer Paths

To understand how to modify each agent, explore these key files:

### EditorAgent
- **Primary Location**: `/multi_agents/agents/editor.py`
- **Key Methods**:
  - `_create_planning_prompt()`: Defines how the agent plans research
  - `_format_planning_instructions()`: Structures planning instructions
  - `plan()`: Main entry point for planning logic

### ReviewerAgent
- **Primary Location**: `/multi_agents/agents/reviewer.py`
- **Key Components**:
  - `TEMPLATE`: System message defining reviewer role
  - `review_draft()`: Core review functionality
  - Feedback formatting logic

### ReviserAgent
- **Primary Location**: `/multi_agents/agents/reviser.py`
- **Key Methods**:
  - `revise_draft()`: Core revision functionality
  - Revision response handling

### WriterAgent
- **Primary Location**: `/multi_agents/agents/writer.py`
- **Key Methods**:
  - `write_sections()`: Creates content sections
  - `revise_headers()`: Standardizes headers
  - Content formatting logic

### HumanAgent
- **Primary Location**: `/multi_agents/agents/human.py`
- **Key Methods**:
  - `get_feedback()`: Human interaction handling
  - Feedback integration

### ResearchAgent
- **Primary Location**: `/multi_agents/agents/researcher.py`
- **Key Integration Point**:
  - `research()`: Uses GPTResearcher for information gathering

### PublisherAgent
- **Primary Location**: `/multi_agents/agents/publisher.py`
- **Key Methods**:
  - `publish()`: Output formatting and export

### Workflow Coordination
- **Primary Location**: `/multi_agents/graphs/research_graph.py`
- **Key Components**:
  - Graph definition
  - Agent connection points
  - Conditional branching logic

## Prompt Modification Touchpoints

To modify agent behavior, focus on these key touchpoints:

### EditorAgent Prompts
- **Planning System Message**: Controls how the editor approaches planning
  ```python
  # In _create_planning_prompt()
  system_message = SystemMessage(
      content="You are a research editor responsible for planning the structure..."
  )
  ```
- **Planning Instructions**: Controls what the editor considers in planning
  ```python
  # In _format_planning_instructions()
  instructions = f"""
  Today is {date_str}.
  {summary_prompt}
  ...
  """
  ```

### ReviewerAgent Prompts
- **Reviewer Identity**: Controls reviewer expertise and focus
  ```python
  # TEMPLATE constant
  TEMPLATE = """You are an expert research article reviewer..."""
  ```
- **Review Instructions**: Controls what the reviewer evaluates
  ```python
  # In review_draft()
  review_prompt = f"""
  Please review the following research article draft...
  ...
  """
  ```

### ReviserAgent Prompts
- **Revision Instructions**: Controls how revisions are performed
  ```python
  # In revise_draft()
  system = "You are an expert writer..."
  user_message = f"""
  Please revise the following draft based on reviewer feedback...
  ...
  """
  ```

### WriterAgent Prompts
- **Writer Instructions**: Controls content creation approach
  ```python
  # In write_sections()
  system = "You are a research writer..."
  user_message = f"""
  Write the following sections...
  ...
  """
  ```
- **Header Revision Instructions**: Controls header standardization
  ```python
  # In revise_headers()
  system = "You are a research writer focusing on headers..."
  ```

## Creating New Agent Behaviors

To create new agent behaviors, follow these steps:

### 1. Identify Target Behavior
Determine which aspect of the research process you want to modify:
- Research focus and organization (EditorAgent)
- Content quality standards (ReviewerAgent)
- Writing style and formatting (WriterAgent)
- Revision approach (ReviserAgent)

### 2. Locate Relevant Prompt
Find the prompt that controls the target behavior using the touchpoints above.

### 3. Modify the Prompt
Adjust the prompt to guide the agent toward your desired behavior:
- Change the agent's role definition
- Add specific instructions for the desired output
- Modify evaluation criteria
- Adjust output format requirements

### 4. Test and Iterate
Run the system to verify behavior changes and refine as needed.

## Real-World Modification Examples

### Example 1: Creating a Social Media Focused Research Team

To adapt the multi-agent system for social media content creation:

1. **Modify EditorAgent Planning Prompt**:
   ```python
   # In _create_planning_prompt()
   system_message = SystemMessage(
       content="You are a social media content strategist planning viral content..."
   )
   
   # In _format_planning_instructions()
   instructions = f"""
   Today is {date_str}.
   Plan 5-7 social media content pieces about: {task.query}
   Each section should be a different platform focus (Twitter, LinkedIn, Instagram, etc.)
   ...
   """
   ```

2. **Adjust WriterAgent Instructions**:
   ```python
   # In write_sections()
   user_message = f"""
   Create social media posts for each platform based on the research...
   For Twitter/X: 280 character limit, include hashtags
   For LinkedIn: Professional tone, 1300 character limit
   ...
   """
   ```

3. **Modify ReviewerAgent Criteria**:
   ```python
   # In review_draft()
   review_prompt = f"""
   Evaluate these social media posts for:
   - Virality potential
   - Platform appropriateness
   - Call-to-action effectiveness
   - Hashtag relevance
   ...
   """
   ```

### Example 2: Creating an Academic Research Team

To adapt the system for academic paper production:

1. **Modify EditorAgent Planning Prompt**:
   ```python
   # In _create_planning_prompt()
   system_message = SystemMessage(
       content="You are an academic journal editor planning a scholarly paper..."
   )
   
   # In _format_planning_instructions()
   instructions = f"""
   Create an academic paper outline following {task.guidelines} format.
   Include sections for: Abstract, Introduction, Literature Review, Methodology,
   Results, Discussion, Conclusion, References.
   ...
   """
   ```

2. **Adjust WriterAgent Instructions**:
   ```python
   # In write_sections()
   user_message = f"""
   Write scholarly content for each section using academic language.
   Include proper citations in {task.guidelines} format.
   Maintain third-person objective voice throughout.
   ...
   """
   ```

3. **Modify ReviewerAgent Criteria**:
   ```python
   # In review_draft()
   review_prompt = f"""
   Evaluate this academic paper for:
   - Methodological rigor
   - Citation completeness
   - Argument coherence
   - Adherence to {task.guidelines} format
   ...
   """
   ```

## Output Format Customization

To customize output formats:

1. **Modify PublisherAgent**:
   ```python
   # In publisher.py
   def publish(self, content, format="custom"):
       if format == "custom":
           # Implement custom formatting
           # ...
   ```

2. **Add Format-Specific Instructions to WriterAgent**:
   ```python
   # In write_sections()
   if task.output_format == "custom":
       format_instructions = """
       Format your output as...
       """
   ```

3. **Update Task Configuration**:
   ```python
   # When creating the task
   task = ResearchTask(
       query="Your research question",
       output_format="custom"
   )
   ```

## Integration with GPTResearcher

The multi-agent system integrates with the core GPTResearcher through the ResearchAgent:

1. **ResearchAgent as Bridge**:
   ```python
   # In researcher.py
   from gpt_researcher.agent import GPTResearcher
   
   def research(self, query, ...):
       researcher = GPTResearcher(...)
       results = researcher.conduct_research()
       return results
   ```

2. **Customizing the Research Parameters**:
   ```python
   # Modify research behavior
   researcher = GPTResearcher(
       query=query,
       report_type=report_type,  # Change this
       report_format=report_format,  # Change this
       # ...
   )
   ```

3. **Integrating Custom Prompt Files**:
   If you've created custom prompts (e.g., `facebook_ads_prompts.py`), you can use them:
   ```python
   # In researcher.py
   # Configure GPTResearcher to use your custom prompts
   # This might require modifying GPTResearcher initialization 
   # or creating a specialized version
   ```

By following this map, you can navigate the multi-agents system and create custom behaviors for specific use cases, just as we modified the GPTResearcher to create LinkedIn posts. 

## Creating Custom Generator Files

To create a dedicated entry point file for your custom multi-agent application (e.g., `facebook_ads_generator.py`), follow these steps:

### 1. Basic Structure for Custom Generator

Here's a template for creating a custom generator file that runs the multi-agent system with your specialized behavior:

```python
# facebook_ads_generator.py
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Add the project root to the path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import multi-agent components
from multi_agents.tasks.base import ResearchTask
from multi_agents.main import run_research_task
from multi_agents.output_formats import OutputFormat

def main():
    """
    Run a specialized Facebook Ads research and generation task using the multi-agents system.
    """
    # Configure the specialized task
    task = ResearchTask(
        query="Facebook advertising best practices for [target audience]",
        guidelines="Generate Facebook ad copy optimized for conversion",
        output_format=OutputFormat.MARKDOWN,
        enable_human_feedback=False,  # Set to True for human-in-the-loop
        max_iterations=2,  # Number of review cycles
        # Add any custom parameters your task might need
        custom_parameters={
            "ad_formats": ["image", "carousel", "video"],
            "audience_demographics": "18-35, tech-savvy professionals",
            "platform_focus": "Facebook and Instagram"
        }
    )
    
    # Execute the multi-agent workflow
    result = run_research_task(task)
    
    # Save the output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("outputs", "facebook_ads")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"facebook_ads_{timestamp}.md")
    with open(output_path, "w") as f:
        f.write(result.content)
    
    print(f"Facebook ads generated successfully and saved to {output_path}")
    return output_path

if __name__ == "__main__":
    main()
```

### 2. Customizing the Multi-Agent Workflow

Before running your custom generator, you'll need to modify the agent prompts as detailed in the previous sections. However, to make your modifications apply only to your specific generator without affecting the core system, you can:

1. **Create a specialized task class** that extends the base `ResearchTask`:

```python
# In a new file like multi_agents/tasks/facebook_ads_task.py
from multi_agents.tasks.base import ResearchTask

class FacebookAdsTask(ResearchTask):
    """Task specifically for generating Facebook ads."""
    
    def __init__(self, query, audience_demographics, ad_formats, **kwargs):
        super().__init__(query, **kwargs)
        self.audience_demographics = audience_demographics
        self.ad_formats = ad_formats
        self.task_type = "facebook_ads"  # This can be used for conditional prompt selection
```

2. **Create custom prompt handlers** for your specific task type:

```python
# This could be in the agent files or in a utility module

def get_editor_prompt(task):
    """Select the appropriate editor prompt based on task type."""
    if getattr(task, 'task_type', None) == "facebook_ads":
        return """You are a Facebook advertising strategist planning 
                ad content for maximum engagement and conversion..."""
    # Default prompt for other tasks
    return """You are a research editor responsible for planning..."""
```

3. **Update your generator file** to use these specialized components:

```python
# In facebook_ads_generator.py
from multi_agents.tasks.facebook_ads_task import FacebookAdsTask

def main():
    task = FacebookAdsTask(
        query="Facebook advertising best practices for SaaS products",
        audience_demographics="Business professionals, 25-54",
        ad_formats=["image", "carousel"],
        guidelines="Generate Facebook ad copy optimized for conversion",
        # Other parameters
    )
    # Rest of the code
```

### 3. Running and Logging

To execute your specialized generator with proper logging:

```python
# Add to facebook_ads_generator.py
import logging

def setup_logging():
    """Configure logging for the Facebook ads generator."""
    log_dir = os.path.join("logs", "facebook_ads_logs")
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"facebook_ads_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"Logging to {log_file}")
    return log_file

def main():
    log_file = setup_logging()
    logging.info("Starting Facebook ads generation")
    
    # Task configuration and execution
    # ...
    
    logging.info(f"Facebook ads generated and saved to {output_path}")
```

### 4. Complete Example

A complete `facebook_ads_generator.py` file would combine all these components:

```python
#!/usr/bin/env python3
"""
Facebook Ads Generator

This script uses the multi-agents system to research and generate 
Facebook ad content optimized for specific audiences and objectives.
"""
import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

# Add the project root to the path if needed
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import multi-agent components
from multi_agents.tasks.facebook_ads_task import FacebookAdsTask
from multi_agents.main import run_research_task
from multi_agents.output_formats import OutputFormat

def setup_logging():
    """Configure logging for the Facebook ads generator."""
    log_dir = os.path.join("logs", "facebook_ads_logs")
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"facebook_ads_{timestamp}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"Logging to {log_file}")
    return log_file

def main():
    """Main execution function for Facebook ads generation."""
    log_file = setup_logging()
    logging.info("Starting Facebook ads generation")
    
    # Parse command line arguments if needed
    # import argparse
    # parser = argparse.ArgumentParser()
    # parser.add_argument("--query", type=str, help="Research query for ad content")
    # args = parser.parse_args()
    
    # Set default query or use command line argument
    query = "Effective Facebook advertising strategies for SaaS products"
    
    # Configure the specialized Facebook ads task
    task = FacebookAdsTask(
        query=query,
        audience_demographics="Business professionals, 25-54",
        ad_formats=["image", "carousel", "video"],
        guidelines="Generate Facebook ad copy optimized for conversion",
        output_format=OutputFormat.MARKDOWN,
        enable_human_feedback=False,
        max_iterations=2,
        custom_parameters={
            "campaign_objective": "lead_generation",
            "key_value_propositions": ["time-saving", "cost-effective", "easy integration"],
            "tone": "professional but approachable"
        }
    )
    
    # Execute the multi-agent workflow
    logging.info(f"Running research task for query: {query}")
    result = run_research_task(task)
    
    # Save the output
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join("outputs", "facebook_ads")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"facebook_ads_{timestamp}.md")
    with open(output_path, "w") as f:
        f.write(result.content)
    
    logging.info(f"Facebook ads generated successfully and saved to {output_path}")
    print(f"\nFacebook ads saved to: {output_path}")
    print(f"Log file: {log_file}")
    
    return output_path

if __name__ == "__main__":
    main()
```

### 5. Integration with Modified Agent Prompts

To fully implement your custom generator, make sure it works with your modified agent prompts. The key connection points are:

1. **Task Type Awareness**: Your custom task class should have a unique `task_type` attribute
2. **Conditional Prompt Selection**: Agent files should check the task type and use appropriate prompts
3. **Parameter Passing**: Ensure your custom parameters are available to the prompt functions

By following these steps, you can create specialized generator files that utilize the multi-agents system with customized behaviors for specific applications like Facebook ad generation, just as `linkedin_generator.py` uses the core GPTResearcher system.