# GPT Researcher Agent Workflows

This document outlines the various agent workflows in the GPT Researcher project, their functionalities, and how to invoke them.

## Overview

GPT Researcher implements multiple agent-based systems that work together to provide research capabilities. The project uses different architectural patterns for different tasks:

1. **Multi-Agent Research System** - A collaborative agent workflow for comprehensive research
2. **Core GPT Researcher System** - The foundational research system using a skills-based approach
3. **Chat Agent System** - A React-based agent for chat interactions with research results
4. **Deep Research System** - Specialized workflow for deeper, more complex research topics

## 1. Multi-Agent Research System

### Description
The Multi-Agent Research System is built using a team of specialized agents that collaborate to produce comprehensive research reports. Each agent has a specific role in the research pipeline.

### Key Components
- **ChiefEditorAgent** (`multi_agents/agents/orchestrator.py`) - Coordinates the entire research process
- **EditorAgent** (`multi_agents/agents/editor.py`) - Plans research and manages parallel research tasks
- **WriterAgent** (`multi_agents/agents/writer.py`) - Converts research data into coherent content
- **ResearchAgent** (`multi_agents/agents/researcher.py`) - Conducts the actual research
- **ReviewerAgent** (`multi_agents/agents/reviewer.py`) - Reviews content for quality
- **ReviserAgent** (`multi_agents/agents/reviser.py`) - Revises content based on reviewer feedback
- **PublisherAgent** (`multi_agents/agents/publisher.py`) - Prepares final output formats
- **HumanAgent** (`multi_agents/agents/human.py`) - Handles human-in-the-loop interactions

### State Management
- **ResearchState** (`multi_agents/memory/research.py`) - Manages overall research state
- **DraftState** (`multi_agents/memory/draft.py`) - Manages individual section drafting state

### How to Invoke
1. **Direct Command Line**:
   ```bash
   python multi_agents/main.py
   ```

2. **API Endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/multi_agents
   ```

3. **Web Interface**:
   Navigate to `http://localhost:8000/` and select the multi-agent option.

## 2. Core GPT Researcher System

### Description
The Core GPT Researcher System is the foundation of the project, implementing a skills-based approach rather than distinct agents. It handles the main research functionality through specialized skills.

### Key Components
- **GPTResearcher** (`gpt_researcher/agent.py`) - Main orchestrator
- **ResearchConductor** (`gpt_researcher/skills/researcher.py`) - Conducts research
- **ReportGenerator** (`gpt_researcher/skills/writer.py`) - Generates reports
- **ContextManager** (`gpt_researcher/skills/context_manager.py`) - Manages research context
- **BrowserManager** (`gpt_researcher/skills/browser.py`) - Handles web browsing
- **SourceCurator** (`gpt_researcher/skills/curator.py`) - Curates sources

### How to Invoke
1. **API Endpoint**:
   ```bash
   curl -X POST http://localhost:8000/report/ \
     -H "Content-Type: application/json" \
     -d '{
       "task": "research about climate change",
       "report_type": "research_report",
       "report_source": "web",
       "tone": "Objective",
       "headers": {},
       "repo_name": "my-research",
       "branch_name": "main",
       "generate_in_background": true
     }'
   ```

2. **Web Interface**:
   Navigate to `http://localhost:8000/` and use the research form.

3. **Programmatic Usage**:
   ```python
   from gpt_researcher.agent import GPTResearcher
   
   researcher = GPTResearcher(
       query="climate change impacts",
       report_type="research_report",
       report_source="web",
       tone="Objective"
   )
   context = await researcher.conduct_research()
   report = await researcher.write_report()
   ```

## 3. Chat Agent System

### Description
The Chat Agent System provides interactive chat capabilities with research results. It uses a React agent pattern and vector store for memory.

### Key Components
- **ChatAgentWithMemory** (`backend/chat/chat.py`) - Handles chat interactions
- Uses LangGraph's `create_react_agent` for reasoning
- Utilizes vector store for context retrieval

### How to Invoke
1. **WebSocket Connection**:
   ```javascript
   const socket = new WebSocket('ws://localhost:8000/ws');
   
   socket.onopen = () => {
     socket.send(JSON.stringify({
       type: 'chat',
       content: 'Tell me about the research on climate change',
       report: 'report_id_here'
     }));
   };
   
   socket.onmessage = (event) => {
     const response = JSON.parse(event.data);
     console.log(response.content);
   };
   ```

2. **Web Interface**:
   After generating a report, use the chat interface to interact with the research results.

## 4. Deep Research System

### Description
The Deep Research System extends the Core GPT Researcher to provide more in-depth analysis on complex topics. It supports multi-level exploration of topics with customizable breadth and depth.

### Key Components
- **DeepResearchSkill** (`gpt_researcher/skills/deep_research.py`) - Handles deep research
- Extension of the Core GPT Researcher

### How to Invoke
1. **API Endpoint**:
   ```bash
   curl -X POST http://localhost:8000/report/ \
     -H "Content-Type: application/json" \
     -d '{
       "task": "in-depth research on quantum computing",
       "report_type": "deep_research",
       "report_source": "web",
       "tone": "Objective",
       "headers": {},
       "repo_name": "my-research",
       "branch_name": "main",
       "generate_in_background": true
     }'
   ```

2. **Web Interface**:
   Navigate to `http://localhost:8000/` and select "Deep Research" as the report type.

3. **Programmatic Usage**:
   ```python
   from gpt_researcher.agent import GPTResearcher
   
   researcher = GPTResearcher(
       query="quantum computing applications",
       report_type="deep_research",
       report_source="web",
       tone="Objective"
   )
   context = await researcher.conduct_research()
   report = await researcher.write_report()
   ```

## Running the Server

To access all workflows, start the server:

```bash
python main.py
```

This will start the server on http://0.0.0.0:8000, making all endpoints accessible.

## Workflow Comparison

| Feature | Multi-Agent | Core GPT Researcher | Chat Agent | Deep Research |
|---------|------------|-------------------|-----------|---------------|
| Focus | Collaborative research | General research | Interactive Q&A | In-depth exploration |
| Architecture | Agent-based | Skills-based | React agent | Extended core system |
| Entry Point | `/api/multi_agents` | `/report/` | WebSocket `/ws` | `/report/` with type=deep_research |
| State Management | ResearchState & DraftState | Internal context | Vector store | Internal context |
| Human-in-loop | Yes | No | Yes (chat) | No |
| Output | Research report | Research report | Chat responses | Detailed research report |

## Conclusion

GPT Researcher provides multiple agent workflows optimized for different research needs. The system can be accessed through API endpoints, WebSocket connections, the web interface, or direct programmatic usage depending on the specific requirements.
