# Architecture Documentation
## Simple Agent Construction Project

**Version:** 1.0
**Last Updated:** 2025-10-31
**Status:** Active Development

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Architecture Design](#architecture-design)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [Technology Stack](#technology-stack)
7. [Database Schema](#database-schema)
8. [System Interactions](#system-interactions)
9. [Security & Privacy](#security--privacy)
10. [Extension Points](#extension-points)
11. [Deployment](#deployment)
12. [Future Considerations](#future-considerations)

---

## Executive Summary

The **Simple Agent Construction Project** is a modular, privacy-first AI coding assistant specifically designed for construction project management and general software engineering tasks. The system runs entirely locally, eliminating cloud API costs and privacy concerns while providing:

- **Conversational AI** for construction calculations and coding assistance
- **File management** capabilities through natural language
- **Mathematical tools** for construction engineering calculations
- **Multi-workspace support** with persistent chat history
- **Digital twin context memory** for long-term project understanding

### Key Characteristics

- **Privacy-First**: 100% local execution, no cloud dependencies
- **Construction-Focused**: Specialized tools for engineering calculations
- **Multi-Workspace**: Isolated project contexts with persistent memory
- **Dual Interface**: CLI and modern web UI (Streamlit)
- **Extensible**: Registry-based tool system for easy expansion

---

## System Overview

### Purpose

This system solves critical challenges faced by construction professionals and developers:

1. **Privacy Concerns**: Eliminates the need to share sensitive construction data with cloud AI services
2. **Cost Control**: No API fees or usage limits
3. **Domain-Specific Tools**: Built-in mathematical functions for structural calculations
4. **Project Context**: Maintains separate workspaces with long-term memory for different construction projects
5. **File Integration**: Direct manipulation of project files through conversational interface

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interfaces                         │
│  ┌─────────────────────┐      ┌────────────────────────┐   │
│  │   CLI Interface     │      │  Streamlit Web UI      │   │
│  │   (main.py)         │      │  (streamlit_app.py)    │   │
│  └──────────┬──────────┘      └──────────┬─────────────┘   │
└─────────────┼────────────────────────────┼─────────────────┘
              │                            │
              └────────────┬───────────────┘
                           │
              ┌────────────▼────────────────┐
              │      AIAgent Core           │
              │      (agent.py)             │
              │                             │
              │  • Chat orchestration       │
              │  • Tool execution          │
              │  • Context management      │
              │  • Streaming responses     │
              └─────┬──────────────┬────────┘
                    │              │
        ┌───────────▼─┐      ┌────▼─────────────┐
        │   Tools     │      │   Chat History   │
        │   Registry  │      │   Database       │
        │  (tools.py) │      │  (history.py)    │
        └─────┬───────┘      └────────┬─────────┘
              │                       │
    ┌─────────▼────────┐    ┌────────▼──────────┐
    │  Math Tools      │    │  SQLite Database  │
    │  File Tools      │    │  • Workspaces     │
    └──────────────────┘    │  • Messages       │
                            │  • Context        │
                            └───────────────────┘
              │
    ┌─────────▼──────────┐
    │   Ollama Server    │
    │   (localhost:11434)│
    │  • LLM Inference   │
    │  • Tool Calling    │
    └────────────────────┘
```

---

## Architecture Design

### Design Patterns

#### 1. Agent-Based Architecture

The system uses a central `AIAgent` class that acts as the orchestrator for all interactions:

- **Agent as Mediator**: All user requests flow through the agent
- **State Management**: Agent maintains conversation state and tool registry
- **Tool Execution**: Agent delegates to specialized tools based on LLM decisions
- **Context Injection**: Agent injects workspace context into every request

**Benefits**:
- Single point of control for all AI interactions
- Easy to extend with new capabilities
- Clear separation between UI and business logic

#### 2. Registry Pattern (Tools)

Tools are registered in an external dictionary (`tool_registry`) rather than hard-coded:

```python
tool_registry = {
    "tool_name": {
        "function": callable,
        "input_schema": {...},
        "description": "..."
    }
}
```

**Benefits**:
- Add new tools without modifying agent code
- Tools can be loaded dynamically
- Easy testing of individual tools
- Clear tool interface contract

#### 3. Repository Pattern (Database)

The `ChatHistoryDB` class abstracts all database operations:

- **Encapsulation**: SQL queries hidden from UI and agent
- **Single Responsibility**: Database class handles only persistence
- **Migration Support**: Schema changes managed in one place

**Benefits**:
- Easy to swap database implementations
- Simplified testing with mock repositories
- Clear data access layer

#### 4. Streaming Pattern

Async generators enable real-time response streaming:

```python
async for chunk in agent.chat(user_input):
    display(chunk)
```

**Benefits**:
- Immediate user feedback
- Reduced perceived latency
- Better UX for long responses

#### 5. Digital Twin Pattern

Each workspace maintains a context summary (digital twin):

- **Summarization**: Full history compressed into key points
- **Context Injection**: Summary injected into system prompt
- **Persistent Memory**: Summaries survive session restarts

**Benefits**:
- Long-term project understanding
- Reduced token usage
- Workspace isolation

### Architectural Principles

#### Modularity
- **Separation of Concerns**: UI, agent, tools, and database are independent modules
- **Loose Coupling**: Components interact through well-defined interfaces
- **High Cohesion**: Each module has a single, clear responsibility

#### Privacy-First
- **No Cloud Calls**: All processing happens locally
- **Data Ownership**: User controls all data
- **No Telemetry**: No usage tracking or analytics

#### Async-First
- **Non-Blocking I/O**: Async/await throughout the stack
- **Streaming**: Incremental responses for better UX
- **Event Loop Management**: Proper handling of nested loops (Streamlit)

#### Configuration-Driven
- **Environment Variables**: All settings in `.env` file
- **Runtime Overrides**: CLI arguments for ad-hoc changes
- **Sensible Defaults**: Works out of the box

---

## Core Components

### 1. AIAgent (agent.py)

**Location**: `/media/daniels/data/work/simple-agent-construction-project/agent.py`

**Responsibility**: Core conversational AI orchestrator

#### Class Structure

```python
class AIAgent:
    def __init__(self, model, server, system_prompt, context_summary=None)
    async def chat(self, user_input) -> AsyncGenerator[str, None]
    async def summarize_history(self, history) -> str
    def set_context(self, context_summary, history)
    def _setup_tools(self)
    def _execute_tool(self, tool_name, tool_input) -> str
```

#### Key Responsibilities

1. **Chat Orchestration**
   - Manages conversation flow with LLM
   - Handles streaming responses
   - Coordinates tool execution cycles

2. **Context Management**
   - Maintains conversation history
   - Injects digital twin context into prompts
   - Supports workspace switching via `set_context()`

3. **Tool Execution**
   - Validates tool calls from LLM
   - Executes tools from registry
   - Handles errors gracefully

4. **Summarization**
   - Compresses chat history into context summaries
   - Uses LLM for intelligent summarization

#### Important Methods

**`chat(user_input)`**
- Main entry point for user messages
- Returns async generator for streaming
- Handles tool calling loop until completion

```python
async for chunk in agent.chat("Calculate sqrt(144)"):
    print(chunk, end="")
# Output: "The square root of 144 is 12."
```

**`set_context(context_summary, history)`**
- Updates agent's workspace context
- Used during workspace switching
- Resets message history and injects new summary

```python
agent.set_context(
    context_summary="Project Alpha: Building stability analysis in progress",
    history=[("How tall?", "The building is 45 meters tall.")]
)
```

**`summarize_history(history)`**
- Generates context summary from message history
- Called before switching workspaces
- Returns concise summary for digital twin

---

### 2. ChatHistoryDB (history.py)

**Location**: `/media/daniels/data/work/simple-agent-construction-project/history.py`

**Responsibility**: Multi-workspace chat persistence layer

#### Database Schema

```sql
-- Workspaces (chats)
CREATE TABLE chats (
    chat_id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context_summary TEXT DEFAULT NULL,
    context_updated_at TIMESTAMP DEFAULT NULL
);

-- Message history
CREATE TABLE history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    user TEXT NOT NULL,
    assistant TEXT NOT NULL,
    FOREIGN KEY(chat_id) REFERENCES chats(chat_id) ON DELETE CASCADE
);
```

#### Key Methods

**Workspace Management**:
- `create_chat(chat_name)` → chat_id
- `list_chats()` → List of (chat_id, chat_name, created_at)
- `rename_chat(chat_id, new_name)`
- `delete_chat(chat_id)` (CASCADE deletes messages)

**Message Operations**:
- `load_history(chat_id)` → List of (user, assistant) tuples
- `add_to_history(chat_id, user, assistant)`
- `clear_history(chat_id)` (keeps workspace, deletes messages)

**Context Management**:
- `set_context_summary(chat_id, summary)` (updates timestamp)
- `get_context_summary(chat_id)` → summary string or None

#### Design Notes

- **Auto-commit**: Each operation commits immediately (no transactions)
- **CASCADE DELETE**: Deleting chat removes all messages
- **Ordered Results**: `list_chats()` returns most recent first
- **NULL Handling**: Context summary optional (new chats have no context)

---

### 3. Tool Registry (tools.py)

**Location**: `/media/daniels/data/work/simple-agent-construction-project/tools.py`

**Responsibility**: Tool definitions and implementations

#### Tool Categories

**Mathematical Tools** (Construction-focused):
- `add(a, b)` - Addition
- `subtract(a, b)` - Subtraction
- `multiply(a, b)` - Multiplication
- `divide(a, b)` - Division (zero-check)
- `sqrt(x)` - Square root (negative-check)
- `power(base, exponent)` - Exponentiation

**File Management Tools**:
- `read_file(path)` - Read file contents
- `list_files(path)` - List directory (handles both files and dirs)
- `edit_file(path, old_text, new_text)` - Replace text or create new file

#### Registry Structure

```python
tool_registry: Dict[str, Dict[str, Any]] = {
    "add": {
        "function": add,
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"}
            },
            "required": ["a", "b"]
        },
        "description": "Add two numbers together"
    },
    # ... more tools
}
```

#### Extension Pattern

To add a new tool:

1. **Define function**:
```python
def calculate_area(length: float, width: float) -> float:
    """Calculate area of rectangle"""
    return length * width
```

2. **Register in tool_registry**:
```python
tool_registry["calculate_area"] = {
    "function": calculate_area,
    "input_schema": {
        "type": "object",
        "properties": {
            "length": {"type": "number", "description": "Length in meters"},
            "width": {"type": "number", "description": "Width in meters"}
        },
        "required": ["length", "width"]
    },
    "description": "Calculate area of a rectangular surface"
}
```

3. **Agent automatically loads it** via `_setup_tools()`

---

### 4. User Interfaces

#### CLI Interface (main.py)

**Location**: `/media/daniels/data/work/simple-agent-construction-project/main.py`

**Features**:
- Async input loop with streaming responses
- Command-line argument overrides (`--model`, `--server`)
- Clean exit handling (Ctrl+C, "exit", "quit")
- Console and file logging

**Usage**:
```bash
python main.py                          # Use defaults from .env
python main.py --model qwen3:30b        # Override model
python main.py --server http://remote:11434  # Remote Ollama
```

**Architecture Notes**:
- Single `asyncio.run()` event loop
- Simple readline-based input (no fancy UI)
- Streaming output with `flush=True` for real-time display

---

#### Web Interface (streamlit_app.py)

**Location**: `/media/daniels/data/work/simple-agent-construction-project/streamlit_app.py`

**Features**:
- Modern chat bubble UI (gold for user, green for assistant)
- Sidebar workspace management
- Create, rename, delete workspaces
- Automatic context switching with summarization
- Sticky input bar at bottom
- Auto-rename first message as workspace name
- Query parameter navigation

**Architecture Highlights**:

1. **Nested Event Loop Handling**:
```python
import nest_asyncio
nest_asyncio.apply()

# Run async code in Streamlit's event loop
loop = asyncio.get_running_loop()
response = loop.run_until_complete(get_response())
```

2. **Session State Management**:
- `st.session_state["chat_id"]` - Current workspace
- `st.session_state["history"]` - Message history
- `st.session_state["chats"]` - All workspaces
- `st.session_state["user_input_modern"]` - Input value
- `st.session_state["pending_chat_rename"]` - First message flag

3. **Workspace Switching Flow**:
```python
# Before switch: summarize current workspace
summary = agent.summarize_history(current_history)
history_db.set_context_summary(current_chat_id, summary)

# Switch workspace
st.session_state["chat_id"] = new_chat_id
new_history = history_db.load_history(new_chat_id)

# After switch: load new context
new_context = history_db.get_context_summary(new_chat_id)
agent.set_context(new_context, new_history)
```

4. **Custom Styling**:
- Markdown with HTML/CSS for chat bubbles
- Fixed input bar via `st.container()`
- Scrollable chat area with `st.container(height=500)`

---

## Data Flow

### User Message Flow (Complete Cycle)

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User enters message in UI                                │
│    (CLI input() or Streamlit text_input)                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. UI calls: agent.chat(user_input)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. AIAgent prepares messages list:                          │
│    • System prompt with context: "[Context Summary]: ..."   │
│    • Previous messages from history                         │
│    • New user message                                       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Send to Ollama AsyncClient with tool schemas             │
│    client.chat(model, messages, tools, stream=True)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Stream response chunks from LLM                          │
│    async for chunk in response:                             │
│        yield chunk['message']['content']                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Check for tool_calls in response                         │
│    if 'tool_calls' in chunk['message']:                     │
└────────────┬───────────────┬────────────────────────────────┘
             │               │
             │ NO            │ YES
             │               ▼
             │    ┌──────────────────────────────────┐
             │    │ 7. Execute each tool:            │
             │    │    result = agent._execute_tool( │
             │    │        name, args                │
             │    │    )                             │
             │    └──────────┬───────────────────────┘
             │               │
             │               ▼
             │    ┌──────────────────────────────────┐
             │    │ 8. Append tool results to msgs  │
             │    │    messages.append({             │
             │    │      "role": "tool",             │
             │    │      "content": result           │
             │    │    })                            │
             │    └──────────┬───────────────────────┘
             │               │
             │               ▼
             │    ┌──────────────────────────────────┐
             │    │ 9. Loop back to step 4 with      │
             │    │    updated messages (includes    │
             │    │    tool results)                 │
             │    └──────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. Final response complete (no more tool calls)            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 11. UI displays full response                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 12. Save to database:                                       │
│     history_db.add_to_history(chat_id, user, assistant)    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 13. (Optional) If first message, rename chat:               │
│     history_db.rename_chat(chat_id, user_input[:64])       │
└─────────────────────────────────────────────────────────────┘
```

---

### Workspace Switching Flow (Digital Twin)

```
┌─────────────────────────────────────────────────────────────┐
│ User clicks workspace button in sidebar                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ BEFORE SWITCHING - Summarize Current Workspace             │
│                                                              │
│ 1. Load current history from session state                  │
│ 2. Call: summary = agent.summarize_history(history)         │
│    • Agent sends history to LLM with summarization prompt   │
│    • LLM returns concise summary of conversation            │
│ 3. Save summary: history_db.set_context_summary(            │
│       current_chat_id, summary                              │
│    )                                                         │
│ 4. Database updates context_summary and context_updated_at  │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ SWITCH WORKSPACE                                            │
│                                                              │
│ 1. Update session state:                                    │
│    st.session_state["chat_id"] = new_chat_id                │
│                                                              │
│ 2. Load new workspace history:                              │
│    new_history = history_db.load_history(new_chat_id)       │
│    st.session_state["history"] = new_history                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ AFTER SWITCHING - Load New Context                         │
│                                                              │
│ 1. Retrieve context summary from database:                  │
│    new_context = history_db.get_context_summary(            │
│        new_chat_id                                           │
│    )                                                         │
│                                                              │
│ 2. Create fresh agent with new context:                     │
│    agent = AIAgent(                                          │
│        model=MODEL,                                          │
│        server=SERVER,                                        │
│        system_prompt=SYSTEM_PROMPT,                          │
│        context_summary=new_context                           │
│    )                                                         │
│    OR                                                        │
│    agent.set_context(new_context, new_history)              │
│                                                              │
│ 3. Clear input and rerun UI                                 │
└─────────────────────────────────────────────────────────────┘
```

**Digital Twin Benefit**: When you switch back to "Project Alpha" weeks later, the agent remembers it was working on stability analysis for a 45-meter building, without loading the entire conversation history.

---

### Tool Execution Flow (Function Calling)

```
┌─────────────────────────────────────────────────────────────┐
│ LLM returns message with tool_calls array                   │
│ {                                                            │
│   "message": {                                               │
│     "tool_calls": [                                          │
│       {                                                      │
│         "function": {                                        │
│           "name": "sqrt",                                    │
│           "arguments": {"x": 144}                            │
│         }                                                    │
│       }                                                      │
│     ]                                                        │
│   }                                                          │
│ }                                                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ For each tool_call in tool_calls:                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. Extract tool name and arguments                          │
│    tool_name = "sqrt"                                        │
│    tool_args = {"x": 144}                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Call: agent._execute_tool(tool_name, tool_args)         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Lookup in tool_registry                                  │
│    tool_info = tool_registry.get("sqrt")                    │
│    if not found → return error message                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Validate arguments using inspect.signature()             │
│    func_params = inspect.signature(sqrt).parameters         │
│    if "x" not in func_params → return error                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Execute tool function                                    │
│    try:                                                      │
│        result = sqrt(x=144)  # Returns 12.0                 │
│        return str(result)    # "12.0"                       │
│    except Exception as e:                                    │
│        return f"Error: {str(e)}"                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Append tool result to messages                           │
│    messages.append({                                         │
│        "role": "tool",                                       │
│        "content": "12.0"                                     │
│    })                                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Send updated messages back to LLM                        │
│    (LLM now knows sqrt(144) = 12.0)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. LLM generates natural language response                  │
│    "The square root of 144 is 12."                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.12+ | Primary programming language |
| **LLM Framework** | Ollama | Latest | Local LLM inference server |
| **LLM Client** | ollama-python | Latest | Async Python client for Ollama |
| **Validation** | Pydantic | Latest | Data validation for Tool schemas |
| **Database** | SQLite 3 | Built-in | Chat history persistence |
| **Web UI** | Streamlit | Latest | Modern web interface |
| **Async** | asyncio | Built-in | Native async/await support |
| **Async (Nested)** | nest_asyncio | Latest | Nested event loop for Streamlit |
| **Config** | python-dotenv | Latest | Environment variable management |
| **Testing** | pytest | Latest | Unit testing framework |
| **Testing (Async)** | pytest-asyncio | Latest | Async test support |

### External Dependencies

#### Ollama Server
- **Purpose**: Local LLM inference engine
- **Default Endpoint**: `http://localhost:11434`
- **Installation**: See [ollama.com](https://ollama.com)
- **Supported Models**: qwen3:4b, qwen3:30b, llama3, mistral, etc.
- **Storage**: ~3GB per model

#### Recommended Models

| Model | Size | Speed | Accuracy | Use Case |
|-------|------|-------|----------|----------|
| qwen3:4b | ~3GB | Fast | Good | Development, quick responses |
| qwen3:30b | ~18GB | Slow | Excellent | Production, complex reasoning |
| llama3:8b | ~5GB | Medium | Very Good | Balanced performance |

---

### System Requirements

**Minimum**:
- CPU: 4 cores
- RAM: 8GB
- Disk: 10GB free
- OS: Linux, macOS, Windows

**Recommended**:
- CPU: 8+ cores
- RAM: 16GB+
- Disk: 50GB SSD
- GPU: NVIDIA GPU with 8GB+ VRAM (for faster inference)

---

## Database Schema

### Entity-Relationship Diagram

```
┌─────────────────────────────────────┐
│            chats                    │
├─────────────────────────────────────┤
│ PK  chat_id         INTEGER         │
│     chat_name       TEXT            │
│     created_at      TIMESTAMP       │
│     context_summary TEXT (nullable) │
│     context_updated_at TIMESTAMP    │
└──────────────┬──────────────────────┘
               │
               │ 1:N
               │
               │
┌──────────────▼──────────────────────┐
│           history                   │
├─────────────────────────────────────┤
│ PK  id              INTEGER         │
│ FK  chat_id         INTEGER         │
│     user            TEXT            │
│     assistant       TEXT            │
└─────────────────────────────────────┘
```

### Table Specifications

#### `chats` Table

Represents individual workspaces (project contexts).

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| chat_id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique workspace identifier |
| chat_name | TEXT | NOT NULL | Display name for workspace |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Workspace creation time |
| context_summary | TEXT | DEFAULT NULL | Digital twin summary |
| context_updated_at | TIMESTAMP | DEFAULT NULL | Last summary update time |

**Indexes**: Primary key on `chat_id`

**Example Row**:
```json
{
  "chat_id": 1,
  "chat_name": "Building Stability Analysis - Tower A",
  "created_at": "2025-10-15 14:30:22",
  "context_summary": "Analyzing 45-meter residential tower. Completed load calculations. Currently reviewing seismic requirements.",
  "context_updated_at": "2025-10-15 16:45:10"
}
```

---

#### `history` Table

Stores message pairs (user → assistant) for each workspace.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique message pair ID |
| chat_id | INTEGER | FOREIGN KEY → chats(chat_id) ON DELETE CASCADE | Workspace reference |
| user | TEXT | NOT NULL | User's message |
| assistant | TEXT | NOT NULL | Agent's response |

**Indexes**: Primary key on `id`, foreign key on `chat_id`

**CASCADE Behavior**: Deleting a chat deletes all associated messages.

**Example Rows**:
```json
[
  {
    "id": 1,
    "chat_id": 1,
    "user": "Calculate sqrt(2025)",
    "assistant": "The square root of 2025 is 45.0."
  },
  {
    "id": 2,
    "chat_id": 1,
    "user": "What's the load capacity for a 45m building?",
    "assistant": "I need more specifics about the building structure. Can you provide the cross-sectional area and material properties?"
  }
]
```

---

### Database Operations

#### Common Queries

**Create Workspace**:
```sql
INSERT INTO chats (chat_name) VALUES (?)
RETURNING chat_id;
```

**Load History**:
```sql
SELECT user, assistant
FROM history
WHERE chat_id = ?
ORDER BY id ASC;
```

**Update Context**:
```sql
UPDATE chats
SET context_summary = ?,
    context_updated_at = CURRENT_TIMESTAMP
WHERE chat_id = ?;
```

**Delete Workspace** (cascades to history):
```sql
DELETE FROM chats WHERE chat_id = ?;
```

---

## System Interactions

### Component Communication Matrix

| From → To | Protocol | Data Format | Async? |
|-----------|----------|-------------|--------|
| UI → Agent | Direct method call | Python strings | Yes |
| Agent → Ollama | HTTP/REST | JSON messages | Yes (streaming) |
| Agent → Tools | Direct function call | Python primitives | No (sync) |
| UI → Database | Direct method call | Python objects | No (sync) |
| Agent → Database | Via UI layer | N/A | N/A |

---

### Sequence Diagrams

#### User Question with Tool Call

```
User     UI          Agent        Ollama       Tool        Database
 │       │            │             │           │            │
 │──1────▶ "sqrt(16)" │             │           │            │
 │       │            │             │           │            │
 │       │──2─────────▶ chat()      │           │            │
 │       │            │             │           │            │
 │       │            │──3──────────▶ stream    │            │
 │       │            │             │           │            │
 │       │            │◀─4─ tool_call("sqrt",16)│            │
 │       │            │             │           │            │
 │       │            │──5──────────────────────▶ sqrt(16)   │
 │       │            │             │           │            │
 │       │            │◀─6──────────────────────│ "4.0"      │
 │       │            │             │           │            │
 │       │            │──7──────────▶ [tool result]          │
 │       │            │             │           │            │
 │       │            │◀─8─ "The sqrt of 16 is 4"            │
 │       │            │             │           │            │
 │       │◀─9─ yield──│             │           │            │
 │       │   chunks   │             │           │            │
 │◀─10───│ display    │             │           │            │
 │       │            │             │           │            │
 │       │──11────────────────────────────────────────────────▶
 │       │  add_to_history("sqrt(16)", "The sqrt of 16 is 4")│
 │       │◀─12────────────────────────────────────────────────│
```

---

#### Workspace Switching with Summarization

```
User     UI          Agent        Database      Ollama
 │       │            │             │            │
 │──1────▶ Switch to  │             │            │
 │       │ "Project B"│             │            │
 │       │            │             │            │
 │       │──2─────────▶ summarize   │            │
 │       │            │  (history)  │            │
 │       │            │             │            │
 │       │            │──3──────────────────────▶│
 │       │            │  "Summarize: [history]"  │
 │       │            │             │            │
 │       │            │◀─4──────────────────────│
 │       │            │  "Summary: Building calc"│
 │       │            │             │            │
 │       │──5─────────────────────▶ set_context │
 │       │  (chat_id, summary)     │  _summary  │
 │       │            │             │            │
 │       │──6─────────────────────▶ load_history│
 │       │            │             │            │
 │       │◀─7─────────────────────│ [(u,a)...]  │
 │       │            │             │            │
 │       │──8─────────▶ set_context│            │
 │       │            │ (summary,  │            │
 │       │            │  history)  │            │
 │       │            │             │            │
 │◀─10───│ Render new workspace    │            │
 │       │            │             │            │
```

---

### Event Loop Architecture

#### CLI Event Loop (Simple)

```python
# main.py
async def main():
    agent = AIAgent(...)

    while True:
        user_input = input("You: ")

        if user_input in ["exit", "quit"]:
            break

        print("Agent: ", end="", flush=True)

        async for chunk in agent.chat(user_input):
            print(chunk, end="", flush=True)

        print()  # Newline

if __name__ == "__main__":
    asyncio.run(main())
```

**Characteristics**:
- Single event loop created by `asyncio.run()`
- Blocking input via `input()` (acceptable for CLI)
- Streaming output via async generator

---

#### Streamlit Event Loop (Nested)

```python
# streamlit_app.py
import nest_asyncio
nest_asyncio.apply()  # Allow nested event loops

def get_response(agent, user_input):
    """Run async code in Streamlit's event loop"""
    loop = asyncio.get_running_loop()

    # Streamlit already has an event loop running
    # nest_asyncio allows us to create a nested one
    return loop.run_until_complete(
        stream_response(agent, user_input)
    )

async def stream_response(agent, user_input):
    chunks = []
    async for chunk in agent.chat(user_input):
        chunks.append(chunk)
    return "".join(chunks)
```

**Challenge**: Streamlit runs its own event loop, but we need to call async `agent.chat()`.

**Solution**: `nest_asyncio.apply()` patches asyncio to allow nested `run_until_complete()`.

---

## Security & Privacy

### Privacy Model

#### No Cloud Dependencies
- **Zero API Calls**: All LLM inference happens locally via Ollama
- **Data Ownership**: All data stored in local SQLite database
- **No Telemetry**: No usage tracking, analytics, or error reporting to external services

#### Benefits
- **Confidential Projects**: Safe for construction projects with NDA requirements
- **Regulatory Compliance**: Meets GDPR, HIPAA data locality requirements
- **Cost Control**: No API usage fees or rate limits

---

### Security Considerations

#### File Access Controls
- **Tool-Mediated Access**: File operations only via `read_file`, `edit_file`, `list_files` tools
- **No Arbitrary Execution**: Agent cannot execute shell commands
- **User-Controlled**: Tools activated only when LLM calls them based on user request

**Potential Risk**: User could ask agent to read sensitive files (e.g., "/etc/passwd")

**Mitigation Recommendation** (not implemented):
```python
ALLOWED_PATHS = ["/home/user/projects/"]

def read_file(path: str):
    if not any(path.startswith(allowed) for allowed in ALLOWED_PATHS):
        return "Error: Access denied to this path"
    # ... rest of implementation
```

---

#### SQL Injection Prevention
- **Parameterized Queries**: All database operations use `?` placeholders
- **Example**:
```python
# SAFE (parameterized)
cursor.execute("SELECT * FROM chats WHERE chat_id = ?", (chat_id,))

# UNSAFE (vulnerable to injection) - NOT USED
cursor.execute(f"SELECT * FROM chats WHERE chat_id = {chat_id}")
```

---

#### Input Validation
- **Tool Argument Validation**: `inspect.signature()` checks function parameters
- **Type Checking**: Pydantic validates tool schemas
- **Error Handling**: Try-catch blocks prevent crashes from malformed inputs

**Example**: Dividing by zero
```python
def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

# Agent gracefully returns error to user
```

---

#### Authentication & Authorization
- **None**: This is a single-user, local application
- **Assumption**: User has physical access to machine
- **Not Suitable For**: Multi-tenant deployments without modification

**Multi-User Extension** (future consideration):
- Add `user_id` column to `chats` table
- Implement login system
- Filter queries by `user_id`

---

## Extension Points

### 1. Adding New Tools

**Location**: `tools.py`

**Steps**:

1. **Define function**:
```python
def check_structural_integrity(
    material: str,
    load_kg: float,
    area_m2: float
) -> str:
    """Calculate if structure can handle load"""
    # Material stress limits (simplified)
    stress_limits = {
        "concrete": 25,  # MPa
        "steel": 250,
        "wood": 10
    }

    if material not in stress_limits:
        return f"Unknown material: {material}"

    stress = (load_kg * 9.81) / (area_m2 * 1_000_000)  # Convert to MPa
    limit = stress_limits[material]

    if stress > limit:
        return f"UNSAFE: {stress:.2f} MPa exceeds {limit} MPa limit"
    else:
        safety_factor = limit / stress
        return f"SAFE: {stress:.2f} MPa, safety factor: {safety_factor:.2f}"
```

2. **Register in tool_registry**:
```python
tool_registry["check_structural_integrity"] = {
    "function": check_structural_integrity,
    "input_schema": {
        "type": "object",
        "properties": {
            "material": {
                "type": "string",
                "description": "Material type (concrete, steel, wood)",
                "enum": ["concrete", "steel", "wood"]
            },
            "load_kg": {
                "type": "number",
                "description": "Total load in kilograms"
            },
            "area_m2": {
                "type": "number",
                "description": "Cross-sectional area in square meters"
            }
        },
        "required": ["material", "load_kg", "area_m2"]
    },
    "description": "Check if a structure can safely handle a given load"
}
```

3. **Restart application** - Agent auto-loads new tool via `_setup_tools()`

4. **Test**:
```
User: Can a concrete column with 0.5 m² area handle 50,000 kg?
Agent: [calls check_structural_integrity("concrete", 50000, 0.5)]
Agent: SAFE: 0.98 MPa, safety factor: 25.51
```

---

### 2. Changing LLM Model

**Method 1: Environment Variable**

Edit `.env`:
```bash
MODEL=llama3:8b
```

**Method 2: CLI Argument**
```bash
python main.py --model mistral:7b
```

**Method 3: Streamlit** (requires code change)

Edit `streamlit_app.py`:
```python
MODEL = os.getenv("MODEL", "qwen3:30b")  # Change default
```

**Model Selection Criteria**:
- **Speed**: Smaller models (4B-8B parameters) respond faster
- **Accuracy**: Larger models (30B+ parameters) reason better
- **Tool Calling**: Test compatibility (some models struggle with function calling)

---

### 3. Custom System Prompt

Edit `.env`:
```bash
SYSTEM_PROMPT="You are a construction engineering AI assistant specializing in Canadian building codes. Always reference NBC 2020 standards in your responses."
```

**Context Injection**: The prompt is automatically augmented with:
```
{SYSTEM_PROMPT}

[Context Summary]: {workspace_context_summary}
```

---

### 4. New UI Frontend

The core agent is UI-agnostic. Create new frontends by:

**Example: Discord Bot**

```python
# discord_bot.py
import discord
from agent import AIAgent
from history import ChatHistoryDB

client = discord.Client()
agent = AIAgent(model="qwen3:4b", server="http://localhost:11434")
db = ChatHistoryDB("discord_history.db")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Map Discord channel to workspace
    chat_id = db.get_or_create_chat(f"discord_{message.channel.id}")

    # Get response
    response_chunks = []
    async for chunk in agent.chat(message.content):
        response_chunks.append(chunk)

    response = "".join(response_chunks)

    # Save and send
    db.add_to_history(chat_id, message.content, response)
    await message.channel.send(response)
```

---

### 5. Database Backend Swap

**Interface**: `ChatHistoryDB` class in `history.py`

**Example: PostgreSQL Backend**

```python
# history_postgres.py
import psycopg2

class ChatHistoryPostgres:
    """PostgreSQL implementation of ChatHistoryDB interface"""

    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
        self._init_db()

    def create_chat(self, chat_name):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO chats (chat_name) VALUES (%s) RETURNING chat_id",
            (chat_name,)
        )
        chat_id = cursor.fetchone()[0]
        self.conn.commit()
        return chat_id

    # ... implement other methods matching ChatHistoryDB interface
```

**Usage**:
```python
# Replace in main.py or streamlit_app.py
from history_postgres import ChatHistoryPostgres
history_db = ChatHistoryPostgres("postgresql://user:pass@localhost/chatdb")
```

---

## Deployment

### Local Development Setup

**Prerequisites**:
1. Python 3.12+
2. Ollama installed and running

**Steps**:

```bash
# 1. Clone repository
cd /path/to/project

# 2. Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install and start Ollama
# Download from https://ollama.com
ollama serve  # Start server

# 5. Pull LLM model
ollama pull qwen3:4b

# 6. Configure environment
cp .env.example .env  # If exists, or create new
# Edit .env with your settings

# 7. Run application
python main.py  # CLI
# or
streamlit run streamlit_app.py  # Web UI
```

---

### Production Deployment (Local Server)

**Scenario**: Deploy on office server for team access

**Architecture**:
```
┌─────────────────┐
│  Team Member 1  │──┐
└─────────────────┘  │
                     │    ┌──────────────────────┐
┌─────────────────┐  │    │  Office Server       │
│  Team Member 2  │──┼───▶│  • Streamlit on :8501│
└─────────────────┘  │    │  • Ollama on :11434  │
                     │    │  • SQLite DB         │
┌─────────────────┐  │    └──────────────────────┘
│  Team Member 3  │──┘
└─────────────────┘
```

**Setup**:

1. **Install on server**:
```bash
ssh user@server
cd /opt/construction-agent
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Configure Streamlit for network access**:

Create `.streamlit/config.toml`:
```toml
[server]
port = 8501
address = "0.0.0.0"  # Listen on all interfaces
headless = true
enableCORS = false

[browser]
gatherUsageStats = false
```

3. **Run as systemd service**:

Create `/etc/systemd/system/construction-agent.service`:
```ini
[Unit]
Description=Construction AI Agent
After=network.target

[Service]
Type=simple
User=construction-agent
WorkingDirectory=/opt/construction-agent
Environment="PATH=/opt/construction-agent/.venv/bin"
ExecStart=/opt/construction-agent/.venv/bin/streamlit run streamlit_app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable construction-agent
sudo systemctl start construction-agent
```

4. **Setup reverse proxy (optional)**:

Nginx configuration:
```nginx
server {
    listen 80;
    server_name construction-agent.local;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

---

### Docker Deployment

**Dockerfile**:
```dockerfile
FROM python:3.12-slim

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pull model during build (optional, can be done at runtime)
RUN ollama serve & sleep 5 && ollama pull qwen3:4b

EXPOSE 8501 11434

# Start both Ollama and Streamlit
CMD ["sh", "-c", "ollama serve & streamlit run streamlit_app.py"]
```

**Docker Compose** (recommended):
```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama

  agent:
    build: .
    ports:
      - "8501:8501"
    environment:
      - ENDPOINT=http://ollama:11434
      - MODEL=qwen3:4b
      - CHAT_HISTORY_DB_PATH=/data/chat_history.sqlite
    volumes:
      - agent_data:/data
    depends_on:
      - ollama

volumes:
  ollama_models:
  agent_data:
```

**Usage**:
```bash
docker-compose up -d
# Access at http://localhost:8501
```

---

### Environment Configuration

**`.env` File Reference**:

```bash
# Ollama Configuration
ENDPOINT=http://localhost:11434
MODEL=qwen3:4b

# System Behavior
SYSTEM_PROMPT=You are an AI assistant for construction engineering. You help with calculations, file management, and project planning.

# Database
CHAT_HISTORY_DB_PATH=chat_history.sqlite

# Logging (optional)
LOG_LEVEL=INFO
LOG_FILE=agent.log
```

**Production Recommendations**:
- Use absolute paths for `CHAT_HISTORY_DB_PATH` and `LOG_FILE`
- Set `MODEL` to larger model for better accuracy (qwen3:30b)
- Customize `SYSTEM_PROMPT` for your specific domain
- Consider separate `.env` files for dev/prod

---

## Future Considerations

### Planned Enhancements

#### 1. Advanced Tools
- **CAD Integration**: Read/write AutoCAD DXF files
- **BIM Support**: Parse IFC (Industry Foundation Classes) files
- **Code Checking**: Automated building code compliance (NBC, IBC)
- **Cost Estimation**: Material quantity takeoffs and pricing

#### 2. Multi-User Support
- User authentication (OAuth, LDAP)
- Role-based access control (engineer, architect, PM)
- Shared workspaces with permissions
- Audit logs for compliance

#### 3. Document Processing
- **PDF Parsing**: Extract data from construction drawings
- **Image Analysis**: Analyze site photos for defects
- **OCR**: Digitize handwritten field notes

#### 4. Real-Time Collaboration
- **WebSocket Support**: Live multi-user chat
- **Concurrent Editing**: Shared context editing
- **Notifications**: Workspace updates via push

#### 5. Advanced Context Management
- **Vector Database**: Semantic search across all workspaces
- **RAG (Retrieval-Augmented Generation)**: Pull relevant past conversations
- **Auto-Summarization**: Periodic context updates, not just on switch

#### 6. Integration APIs
- **REST API**: Programmatic access for third-party tools
- **Webhooks**: Trigger external actions (e.g., create Jira ticket)
- **Zapier/Make Integration**: No-code automation

#### 7. Performance Optimizations
- **Caching**: Cache frequent calculations
- **Model Quantization**: Smaller model files with minimal accuracy loss
- **GPU Acceleration**: CUDA support for faster inference

---

### Architectural Evolution

#### Current Architecture (v1.0)
```
CLI/Streamlit → Agent → Ollama
                  ↓
              Tools + SQLite
```

**Characteristics**:
- Monolithic agent
- Synchronous tools
- Single database
- No caching

---

#### Proposed Architecture (v2.0)
```
                 ┌──────────────┐
                 │   Load       │
                 │  Balancer    │
                 └───────┬──────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
    │ Agent 1 │    │ Agent 2 │    │ Agent N │
    └────┬────┘    └────┬────┘    └────┬────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌────▼────┐    ┌────▼─────┐
    │  Ollama │    │  Tools  │    │ Postgres │
    │ Cluster │    │  API    │    │  + Redis │
    └─────────┘    └─────────┘    └──────────┘
```

**Characteristics**:
- Horizontal scaling (multiple agent instances)
- Centralized database (PostgreSQL)
- Caching layer (Redis)
- Microservices for tools
- Message queue for async tasks

---

### Migration Path

#### Phase 1: Optimization (v1.1)
- Add Redis caching for context summaries
- Implement connection pooling for database
- Optimize SQLite queries with indexes

#### Phase 2: Modularization (v1.5)
- Extract tools into separate service
- Add REST API wrapper around agent
- Implement authentication layer

#### Phase 3: Scaling (v2.0)
- Migrate to PostgreSQL
- Add load balancer
- Deploy agent pool
- Implement distributed caching

---

## Conclusion

The **Simple Agent Construction Project** demonstrates a well-architected, privacy-first AI system tailored for construction engineering. Its modular design, clear separation of concerns, and extensible architecture make it suitable for both individual use and team deployments.

### Key Strengths

1. **Privacy**: 100% local execution
2. **Modularity**: Easy to extend and maintain
3. **Persistence**: Multi-workspace support with long-term memory
4. **Usability**: Dual interfaces (CLI and modern web UI)
5. **Domain Focus**: Construction-specific tools

### Recommended Next Steps

1. **Production Hardening**: Add file access controls, authentication
2. **Tool Expansion**: Implement construction-specific tools (CAD, BIM, code checking)
3. **Testing**: Expand test coverage beyond current unit tests
4. **Documentation**: Create user guide and API reference
5. **Performance**: Benchmark and optimize database queries

---

**Document Version**: 1.0
**Last Updated**: 2025-10-31
**Maintained By**: Architecture Team
**Contact**: See README.md for support channels
