# Code Execution Path: Next.js Frontend Request for Multi-Agent Report

## 1. Introduction

This document provides a detailed, step-by-step trace of the code execution flow when a user requests a "Multi Agents Report" through the Next.js frontend interface. The goal is to understand how the frontend request triggers the backend processing, invokes the specialized multi-agent research logic, streams results back, and completes the task, without needing to refer back to the original source code files.

The system uses a WebSocket connection for real-time communication and task execution management.

## 2. High-Level Flow Overview

1.  **Frontend**: User selects "Multi Agents Report", enters query, clicks "Generate".
2.  **Frontend → Backend**: WebSocket connection established; `start` command sent with task details (query, `report_type="multi_agents"`).
3.  **Backend (WebSocket Listener)**: Receives `start` command.
4.  **Backend (Command Handler)**: Parses command, prepares parameters.
5.  **Backend (Dispatcher)**: Identifies `report_type` as "multi_agents".
6.  **Backend (Multi-Agent Invocation)**: Calls the primary function (`run_research_task`) within the `multi_agents` codebase.
7.  **Backend (Multi-Agent Execution)**: The multi-agent system (ChiefEditor, Editor, Researcher, etc.) runs, using a provided streaming function to send logs/updates back via WebSocket.
8.  **Backend → Frontend**: Real-time logs and status updates are streamed back.
9.  **Backend (Completion)**: Multi-agent task finishes; final report content potentially returned.
10. **Backend (File Generation)**: Output files (.md, .pdf, .docx) created from the final report.
11. **Backend → Frontend**: Final message sent via WebSocket with paths to the generated files.

## 3. Detailed Step-by-Step Execution Trace

**Step 1: Frontend - User Action & WebSocket Initiation**

*   The user interacts with the Next.js UI, selects "Multi Agents Report" as the report type, enters their research query (e.g., "Is AI in a hype cycle?"), and initiates the report generation.
*   Frontend JavaScript code establishes a WebSocket connection to the backend server's `/ws` endpoint.
*   Upon successful connection, the frontend sends a message over the WebSocket. The message starts with the command `start` followed by a JSON string containing the task details.
    *   *Message Format Example:* `start {"task": "Is AI in a hype cycle?", "report_type": "multi_agents", "report_source": "web", "tone": "Objective", ...}`

**Step 2: Backend - WebSocket Connection Handling (`server.py`)**

*   The FastAPI application receives the WebSocket connection request at the `/ws` route.
*   The `websocket_endpoint` asynchronous function handles this route.
*   An instance of the `WebSocketManager` class (from `backend/server/websocket_manager.py`, likely named `manager`) is used.
*   `await manager.connect(websocket)` is called. This method within `WebSocketManager`:\n    *   Accepts the WebSocket connection.\n    *   Adds the `websocket` object to its list of `active_connections`.\n    *   Creates an `asyncio.Queue` for outgoing messages specific to this connection.\n    *   Starts an asynchronous `start_sender` task dedicated to sending messages from the queue over this specific `websocket`.\n*   Control is then passed to `await handle_websocket_communication(websocket, manager)` (from `backend/server/server_utils.py`).

**Step 3: Backend - WebSocket Message Listener (`server_utils.py`)**

*   The `handle_websocket_communication` function enters a continuous loop (`while True`).
*   Inside the loop, `data = await websocket.receive_text()` waits for and receives the message sent by the frontend.
*   The code checks the received `data`. The condition `elif data.startswith("start"):` matches the incoming message.
*   To handle the potentially long-running research task without blocking the listener, it wraps the command handler in a background task: `running_task = run_long_running_task(handle_start_command(websocket, data, manager))`.\n    *   `run_long_running_task` is a helper function that creates an `asyncio.Task` to run the provided awaitable (`handle_start_command(...)`) and includes basic error handling and logging.

**Step 4: Backend - Handling the 'start' Command (`server_utils.py`)**

*   The `handle_start_command(websocket, data, manager)` function executes as a background task.
*   It parses the JSON payload from the `data` string: `json_data = json.loads(data[6:])`.
*   It extracts the parameters using `extract_command_data(json_data)`, retrieving `task`, `report_type` (value is "multi_agents"), `tone`, etc.
*   It instantiates `CustomLogsHandler(websocket, task)`. This `logs_handler` object is crucial:\n    *   It stores the specific `websocket` connection instance.\n    *   It provides an `async send_json(data)` method which formats log/status messages and sends them over the stored `websocket`.\n    *   It also initializes and manages a persistent JSON log file in the `./outputs` directory for the specific task.
*   The core delegation step occurs: `report = await manager.start_streaming(...)` is called. This passes the task parameters (`task`, `report_type="multi_agents"`, `tone`, etc.) and the original `websocket` object to the `WebSocketManager` instance.

**Step 5: Backend - Delegating to the Agent Runner (`websocket_manager.py`)**

*   The `WebSocketManager.start_streaming(...)` method is invoked.
*   It primarily acts as an initial entry point, performing minimal processing (like converting the `tone` string to an Enum).
*   It immediately calls the main agent execution logic: `report = await run_agent(...)`, passing along all necessary parameters received from `handle_start_command`, including `task`, `report_type="multi_agents"`, and the `websocket` object.

**Step 6: Backend - Dispatching and Running the Agent (`websocket_manager.py`)**

*   The `run_agent(...)` asynchronous function (defined in `websocket_manager.py`) now takes control.
*   It creates *another* instance of `CustomLogsHandler(websocket, task)` (named `logs_handler`). This instance will be passed down to the research functions to handle streaming output.
*   **Dispatch Logic:** The code checks the value of `report_type`:\n    *   `if report_type == "multi_agents":` evaluates to TRUE.
*   **Multi-Agent Invocation:** The code inside this `if` block runs:\n    *   It calls the imported `run_research_task` function (from `multi_agents.main`).\n    *   Crucially, it passes specific arguments:\n        *   `query=task`: The user\'s research query.\n        *   `websocket=logs_handler`: The `CustomLogsHandler` instance is passed. Any code within `run_research_task` or its sub-agents that expects a \'websocket\' object with a `send_json` method will use this handler to stream data back.\n        *   `stream_output=stream_output`: A function (imported from `gpt_researcher.actions`) is passed. This function is likely designed to also use the `send_json` method of the object passed as the `websocket` argument (i.e., the `logs_handler`).\n        *   Other parameters like `tone` and `headers` are also passed through.

**Step 7: Backend - Multi-Agent Code Execution (`multi_agents/` directory)**

*   The `run_research_task` function in `multi_agents/main.py` starts execution.
*   It likely initializes the `ChiefEditorAgent` (from `multi_agents/agents/orchestrator.py`), passing the task details and potentially the `websocket` (the `logs_handler`) and `stream_output` function.
*   The `ChiefEditorAgent` orchestrates the multi-agent workflow using LangGraph:\n    *   Initial research (e.g., using `ResearchAgent` which internally uses `GPTResearcher`).\n    *   Planning (`EditorAgent`).\n    *   Parallel subtopic research (`ResearchAgent`, `ReviewerAgent`, `ReviserAgent` loop for each section).\n    *   Report writing (`WriterAgent`).\n    *   Publishing (`PublisherAgent`).
*   **Streaming:** Throughout this process, individual agents can use the `websocket` object (the `logs_handler`) or the `stream_output` function provided to them (via the orchestrator) to send status updates, logs, or partial results. These calls invoke `logs_handler.send_json(data)`, which sends formatted JSON messages back to the connected frontend via the original WebSocket.
*   `run_research_task` eventually completes and returns a result (e.g., a dictionary potentially containing the final report content under a key like "report").

**Step 8: Backend - Returning Results (`websocket_manager.py`)**

*   Control returns to the `run_agent` function.
*   It extracts the final report content from the dictionary returned by `run_research_task` (e.g., `report = report.get("report", "")`).
*   Since `report_type` is "multi_agents", the `return_researcher` logic is skipped.
*   `run_agent` returns the final report string.
*   Control returns to `WebSocketManager.start_streaming`.
*   `start_streaming` receives the final report string, potentially uses it to initialize a `ChatAgentWithMemory`, and returns the report string.

**Step 9: Backend - Finalizing and Sending File Paths (`server_utils.py`)**

*   Control returns to `handle_start_command` where the `await manager.start_streaming(...)` call resolves, assigning the final report string to the `report` variable.
*   `report = str(report)` ensures it\'s a string.
*   `file_paths = await generate_report_files(report, sanitized_filename)` is called. This utility function takes the final markdown report string and generates the corresponding `.md`, `.pdf`, and `.docx` files in the `./outputs` directory, returning a dictionary of their relative paths.
*   The path to the persistent JSON log file is added to the `file_paths` dictionary.
*   `await send_file_paths(websocket, file_paths)` is called. This sends a final JSON message over the WebSocket to the frontend. This message contains the relative paths to all the generated output files.
    *   *Message Format Example:* `{"type": "path", "output": {"pdf": "outputs/task_1678886400_Is_AI_in_a_hype_cycle.pdf", "docx": "...", "md": "...", "json": "..."}}`
*   The background task executing `handle_start_command` finishes.

**Step 10: Frontend - Receiving Results**

*   The frontend WebSocket listener receives the streamed log/status messages throughout the process and updates the UI accordingly.
*   Finally, it receives the `{"type": "path", ...}` message containing the links to the downloadable report files.
*   The frontend updates the UI to show links to the generated reports.

## 4. Conclusion

This detailed trace shows that the multi-agent report generation is initiated via a WebSocket `start` command from the frontend. The backend uses a `WebSocketManager` and the `run_agent` function within it to dispatch the request based on the `report_type="multi_agents"` parameter. This dispatcher correctly invokes the `run_research_task` function from the `multi_agents` codebase, passing a specialized logging handler (`CustomLogsHandler`) that wraps the original WebSocket connection to enable real-time streaming of logs and status updates back to the user interface. The process concludes with the generation of report files and the transmission of their paths to the frontend.

## 5. Key Points for Modifying Multi-Agent Behavior

To change the behavior of the multi-agent system when run through the Next.js frontend, specific prompts at key points in the execution flow need to be modified. These prompts directly control how different agents perform their assigned tasks.

### Critical Prompt Locations

1.  **Research Planning Prompt:**
    *   **Location:** Used by the [`EditorAgent`](../multi_agents/agents/editor.py) during the planning phase in the [`_create_planning_prompt`](../multi_agents/agents/editor.py#L80) function.
    *   **Description:** Controls how the report outline and sections are structured based on initial research findings.
    *   **Impact:** Modifying this prompt changes the organization, section breakdown, and topical focus of the entire research report.

2.  **Subtopic Research & Drafting Prompts:**
    *   **Location:** Used by the [`ResearchAgent`](../multi_agents/agents/researcher.py) when performing in-depth investigation on individual section topics.
    *   **Description:** Guides the generation of search queries, information extraction, and section draft writing.
    *   **Impact:** Changes here affect research depth, source selection criteria, and the initial content quality for each section.

3.  **Draft Review Prompt:**
    *   **Location:** Used by the [`ReviewerAgent`](../multi_agents/agents/reviewer.py) in the review phase of each section via the [`review_draft`](../multi_agents/agents/reviewer.py#L15) function.
    *   **Description:** Defines the evaluation criteria for assessing each section draft.
    *   **Impact:** Editing this prompt alters quality standards, feedback specificity, and which aspects of the content receive scrutiny.

4.  **Draft Revision Prompt:**
    *   **Location:** Used by the [`ReviserAgent`](../multi_agents/agents/reviser.py) when improving sections based on reviewer feedback in the [`revise_draft`](../multi_agents/agents/reviser.py#L21) function.
    *   **Description:** Instructs how to interpret and implement reviewer feedback to improve section content.
    *   **Impact:** Changes here influence how thoroughly feedback is incorporated and the approach to content enhancement.

5.  **Final Report Compilation/Writing Prompt:**
    *   **Location:** Used by the [`WriterAgent`](../multi_agents/agents/writer.py) during the final compilation phase in the [`write_sections`](../multi_agents/agents/writer.py#L32) function.
    *   **Description:** Guides the integration of all revised sections into a cohesive final report with proper introduction and conclusion.
    *   **Impact:** Modifications affect overall report coherence, style consistency, introduction/conclusion quality, and citation formatting.

### Implementation Notes

These prompts are executed during the multi-agent workflow orchestrated by the [`ChiefEditorAgent`](../multi_agents/agents/orchestrator.py), which coordinates the entire process through a state graph. The actual prompt templates are defined in the respective agent implementation files. By identifying and modifying these specific prompts, you can significantly alter the behavior, quality, and characteristics of the multi-agent research output without changing the overall execution flow described in previous sections.
