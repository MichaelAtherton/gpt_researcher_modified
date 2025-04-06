# Multi-Agent System Prompt Engineering Guide

## Table of Contents
- [Multi-Agent System Prompt Engineering Guide](#multi-agent-system-prompt-engineering-guide)
  - [Table of Contents](#table-of-contents)
  - [1. EditorAgent Prompts](#1-editoragent-prompts)
    - [1.1 Planning Prompt](#11-planning-prompt)
    - [1.2 Planning Instructions Format](#12-planning-instructions-format)
  - [2. ReviewerAgent Prompts](#2-revieweragent-prompts)
    - [2.1 Review Template](#21-review-template)
    - [2.2 Review Draft Prompt](#22-review-draft-prompt)
  - [3. ReviserAgent Prompts](#3-reviseragent-prompts)
    - [3.1 Revision Prompt](#31-revision-prompt)
  - [4. WriterAgent Prompts](#4-writeragent-prompts)
    - [4.1 Write Sections Prompt](#41-write-sections-prompt)
    - [4.2 Revise Headers Prompt](#42-revise-headers-prompt)
  - [5. HumanAgent](#5-humanagent)
  - [6. PublisherAgent](#6-publisheragent)
  - [7. ResearchAgent](#7-researchagent)
  - [Key Findings](#key-findings)
  - [Modification Strategy](#modification-strategy)
  - [Comparison: Multi-Agents System vs. Core GPTResearcher](#comparison-multi-agents-system-vs-core-gptresearcher)
    - [Architectural Differences](#architectural-differences)
    - [Advantages of the Multi-Agents System](#advantages-of-the-multi-agents-system)
    - [When to Use Multi-Agents vs. Core GPTResearcher](#when-to-use-multi-agents-vs-core-gptresearcher)

This document provides a comprehensive breakdown of all prompts used in the GPT-Researcher's multi-agent system, their locations, functions, and how modifications would affect behavior.

## 1. EditorAgent Prompts

### 1.1 Planning Prompt
- **Location**: `multi_agents/agents/editor.py:_create_planning_prompt()`
- **Description**: Defines the Editor's role and generates an outline of sections for research based on initial research.
- **Components**: 
  - System message sets the agent as a "research editor" who oversees research and plans article structure
  - User message contains research summary and formatting instructions for the outline
- **How Modification Affects Behavior**: 
  - Changing the system message affects how the agent views its responsibilities and authority
  - Modifying max_sections parameter changes research breadth
  - Adjusting the output format instructions affects how section plans are structured

### 1.2 Planning Instructions Format
- **Location**: `multi_agents/agents/editor.py:_format_planning_instructions()`
- **Description**: Formats the detailed instructions for research planning, including today's date, research summary, feedback, and section specifications.
- **How Modification Affects Behavior**:
  - Adjusting the section generation requirements affects report structure and depth
  - Changing JSON output format requirements affects downstream processing
  - Modifying instructions about introduction/conclusion exclusion changes outline scope

## 2. ReviewerAgent Prompts

### 2.1 Review Template
- **Location**: `multi_agents/agents/reviewer.py:TEMPLATE` (constant)
- **Description**: Defines the reviewer's core identity as an expert research article reviewer
- **How Modification Affects Behavior**: 
  - Setting different reviewer expertise/domain focus will change review priorities
  - Adding specific quality criteria will influence feedback style

### 2.2 Review Draft Prompt
- **Location**: `multi_agents/agents/reviewer.py:review_draft()` 
- **Description**: Dynamically constructed prompt that includes the system template, review instructions, and optional revision history
- **Components**:
  - Main review prompt for first-time reviews
  - Specialized revise_prompt for already-revised content
  - Guideline information from task
- **How Modification Affects Behavior**:
  - Changing feedback threshold (what warrants "None" vs. revision requests) affects review cycle length
  - Modifying guideline evaluation criteria changes what the reviewer focuses on
  - Changing the revision feedback style affects how iterative the review process becomes

## 3. ReviserAgent Prompts

### 3.1 Revision Prompt
- **Location**: `multi_agents/agents/reviser.py:revise_draft()`
- **Description**: Instructs an expert writer to revise drafts based on reviewer feedback
- **Components**:
  - System message defining agent role as expert writer
  - User message with draft content, reviewer notes, and JSON output format
  - Sample JSON structure (sample_revision_notes)
- **How Modification Affects Behavior**:
  - Changing expertise level affects how aggressively revisions are made
  - Modifying instructions about balancing reviewer feedback vs. original content changes revision approach
  - Adjusting output format affects how revision notes are structured

## 4. WriterAgent Prompts

### 4.1 Write Sections Prompt
- **Location**: `multi_agents/agents/writer.py:write_sections()`
- **Description**: Instructs the agent to create introduction, conclusion, table of contents, and reference sections
- **Components**:
  - System message defining research writer role
  - Detailed instructions for creating report components
  - Format guidelines for markdown and citations
  - JSON output format specifications using sample_json
- **How Modification Affects Behavior**:
  - Changing writing style instructions affects tone/formality
  - Modifying formatting guidelines changes output structure
  - Adjusting source citation requirements affects reference handling

### 4.2 Revise Headers Prompt
- **Location**: `multi_agents/agents/writer.py:revise_headers()`
- **Description**: Used to standardize and refine report headers based on guidelines
- **Components**:
  - System message defining role as headers-focused writer
  - Instructions for revising headers based on guidelines
  - Input headers data and output format requirements
- **How Modification Affects Behavior**:
  - Changing header standardization rules affects report structure
  - Modifying how guidelines are applied to headers changes overall report organization

## 5. HumanAgent

The HumanAgent doesn't use LLM prompts; instead it handles human-in-the-loop interactions, collecting feedback that might influence other agents.

## 6. PublisherAgent

The PublisherAgent doesn't use prompts - it's focused on formatting and exporting research reports to different file formats.

## 7. ResearchAgent

ResearchAgent doesn't contain direct prompts in its code; instead, it uses the GPTResearcher class from the main project, which likely has its own prompt engineering. The actual research prompts are encapsulated in that external class.

## Key Findings

1. **Central Prompt Design Pattern**: All agents follow a consistent pattern with system messages defining roles and user messages providing specific instructions.

2. **JSON Output Control**: Most prompts enforce specific JSON output formats to ensure correct data structure for the next agent in the workflow.

3. **Hierarchical Relationships**: Prompts establish clear agent relationships (Editor oversees, Researcher collects, Reviewer evaluates, Reviser improves, Writer compiles).

4. **High Modification Impact Areas**:
   - Editor's planning prompt (affects entire research structure)
   - Reviewer's feedback criteria (affects revision cycles)
   - Writer's section generation (affects final output quality)

5. **Low Code-to-Prompt Ratio**: The system uses relatively few but very targeted prompts. Each prompt serves a specific function in the research workflow.

## Modification Strategy

To modify agent behavior in this system:

1. **Role Definition**: Change system messages to adjust agent personality and approach
2. **Task Instructions**: Modify user message content to change specific task parameters
3. **Output Format**: Adjust JSON formatting requirements to change data structure 
4. **Evaluation Criteria**: Change the guidelines or review thresholds to affect quality standards
5. **Workflow Control**: Adjust when "None" is returned to control flow between agents

The modular nature of the system allows for targeted changes that can significantly alter research outcomes while maintaining the overall workflow structure.

## Comparison: Multi-Agents System vs. Core GPTResearcher

This section compares the multi-agents system with the core GPTResearcher class to highlight key differences and advantages.

### Architectural Differences

| Feature | Multi-Agents System | Core GPTResearcher |
|---------|---------------------|-------------------|
| Agent Structure | Multiple specialized agents with defined roles | Single agent with different skills and report types |
| Workflow | Sequential process with feedback loops | Linear process from research to report generation |
| Planning | Explicit planning phase with EditorAgent | Implicit planning through search queries |
| Quality Control | Dedicated ReviewerAgent and ReviserAgent | Self-review within same agent |
| Human Interaction | Explicit HumanAgent for feedback integration | Limited or no human-in-the-loop functionality |

### Advantages of the Multi-Agents System

1. **Specialized Expertise**: Each agent focuses on a specific aspect of the research process, leading to higher quality in each area.

2. **Iterative Improvement**: The review-revise cycle allows for multiple passes of quality improvement before finalization.

3. **Human Collaboration**: Structured integration of human feedback through the HumanAgent provides greater control over the research direction.

4. **Enhanced Structure**: The EditorAgent creates a comprehensive plan upfront, ensuring more coherent organization of complex topics.

5. **Quality Assurance**: Separation of content creation from review leads to more objective quality assessment.

6. **Workflow Flexibility**: The modular agent structure allows for easy addition, removal, or modification of steps in the research process.

7. **Realistic Team Simulation**: The multi-agent approach mimics how human research teams function, with specialized roles collaborating on a common goal.

### When to Use Multi-Agents vs. Core GPTResearcher

**Choose Multi-Agents for**:
- Complex, comprehensive research projects requiring high quality
- Projects benefiting from human guidance during the process
- Research requiring careful structure and organization
- Situations where iterative improvement is valuable

**Choose Core GPTResearcher for**:
- Quicker, more straightforward research tasks
- Specialized output formats (LinkedIn posts, resource lists)
- Research with less complex organizational needs
- Situations where computational efficiency is prioritized

The multi-agents system represents an evolution of the research capabilities in GPTResearcher, providing a more collaborative, iterative approach that enhances quality through specialization and feedback.
