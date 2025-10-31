
# Local AI Code Assistant for Construction Project Management

## Project Purpose
This project is a modular, privacy-first AI coding assistant designed for construction project management and general coding tasks. It builds on the local-first AI philosophy, running entirely on your machine with no cloud APIs or external dependencies. The agent can read, list, and edit files, and perform essential math operations for sizing and calculations in construction workflows.

## What Makes This Special

- **Privacy-First Architecture**: 100% local execution with no cloud dependencies - your construction data never leaves your machine
- **Digital Twin Memory**: Each workspace maintains an intelligent context summary, giving the AI long-term understanding of your projects without loading full conversation history
- **Construction-Focused**: Built-in mathematical tools specifically designed for engineering calculations (stability analysis, material sizing, etc.)
- **True Multi-Workspace**: Isolated project contexts with independent memory - switch between different construction projects seamlessly
- **Extensible by Design**: Registry-based tool system lets you add domain-specific tools without modifying core agent code
- **Dual Interface**: Choose between lightweight CLI or modern web UI depending on your workflow

## Prerequisites
- **Ollama**: Download from [ollama.com](https://ollama.com) to run local LLMs (e.g., qwen3:4b)
- **qwen3:4b model**: Efficient 4B parameter model (auto-downloaded by Ollama)
- **uv package manager**: For Python dependency management ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
- **Python 3.12+**: Managed automatically by uv
- **RAM**: 4GB+ recommended
- **Storage**: ~3GB for model files
- **OS**: Linux, macOS, or Windows
- **Internet**: Only needed for initial setup/model download

## Important Technical Choices
- **Local-First AI**: No data leaves your machine; complete privacy and zero API costs
- **Modular Design**: Tools are externalized in `tools.py` and loaded via a registry for easy extension and review
- **Async Handling**: The agent and main loop are fully async, supporting streaming responses for fast, responsive interaction.
- **Streamlit UI**: Modern chat interface with sticky input, chat bubbles, sidebar controls, and history management.
- **Long-Term History**: All chat history is stored in a local SQLite database (`chat_history.sqlite`) for persistence across sessions, managed via `history.py`.
- **Configurable System Prompt**: Easily change the assistant's behavior via the `.env` file
- **Logging**: All interactions are logged for traceability and debugging
- **No Manual Dependency Installation**: Uses uv's inline dependencies in script headers

## Environment Variables (.env)

Create a `.env` file in the project root to configure the assistant. The following variables are supported:

- `ENDPOINT`: The URL of your local or remote Ollama server (e.g., `http://localhost:11434`).
- `MODEL`: The default model to use (e.g., `qwen3:4b`, `qwen3:30b`).
- `SYSTEM_PROMPT`: The system prompt that controls the assistant's behavior and tone.

Example `.env`:
```
ENDPOINT=http://localhost:11434
MODEL=qwen3:30b
SYSTEM_PROMPT=You are a helpful coding assistant operating in a terminal environment. Output only plain text without markdown formatting, as your responses appear directly in the terminal. Be concise but thorough, providing clear and practical advice with a friendly tone. Don't use any asterisk characters in your responses.
```

## Getting Started

### 1. Set Up a Python Virtual Environment

You can use either [uv](https://docs.astral.sh/uv/) (recommended for speed and reproducibility) or standard Python venv with requirements.txt.

#### Using uv (recommended)
```bash
uv venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

#### Using Python venv
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

> **Note:** Always activate your virtual environment before running Streamlit or the agent.
1. **Install uv**
   - Linux/macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. **Install Ollama**
   - Linux/macOS: `curl -fsSL https://ollama.com/install.sh | sh`
   - Windows: Download from [ollama.com](https://ollama.com/download)
3. **Ensure Ollama server is running and pull the model**
    - Make sure the Ollama server is running on the port specified in your `.env` file (default: `http://localhost:11434`).
    - You can check if Ollama is running with:
       ```bash
       curl http://localhost:11434/api/tags
       ```
    - If not running, start it with:
       ```bash
       ollama serve
       ```
    - Then check if the model you want to use (e.g., `qwen3:4b` or `qwen3:30b`) is already available:
       ```bash
       ollama list | grep qwen3:4b
       ollama list | grep qwen3:8b
       ollama list | grep qwen3:30b
       ollama list | grep gpt-oss:20b
       ```
      If the model is not listed, pull it with:
       ```bash
       ollama pull qwen3:4b
       # or
       ollama pull qwen3:8b
       # or
       ollama pull qwen3:30b
       # or
       ollama pull gpt-oss:20b      
       ```
4. **Run the agent in CLI**
   ```bash
   uv run main.py
   ```

5. **Or you can run the modern chat interface with:**
```bash
uv run streamlit_app.py
```


## References & Origins
This project is based on and inspired by:
- [single-file-ai-agent-tutorial](https://github.com/dstroe2000/single-file-ai-agent-tutorial) (starting point for this codebase)
- [Dave Ebbelaar's implementation](https://github.com/daveebbelaar/single-file-ai-agent-tutorial)
- [Francis Beeson's implementation](https://github.com/leobeeson/single-file-ai-agent-tutorial)
- [Thorsten Ball's tutorial](https://ampcode.com/how-to-build-an-agent)


## Key Features

### Core Capabilities
- **File Operations**: Read, list, and edit files directly from the chat interface
- **Math Tools**: Add, subtract, multiply, divide, sqrt, power for construction calculations
- **Persistent History**: SQLite database stores all conversations for long-term retention across sessions
- **Context Summaries**: Automatic workspace summarization for efficient memory management

### Technical Highlights
- **Async Architecture**: Fully async agent and streaming responses for real-time interaction
- **Modern Streamlit UI**: Chat bubbles, sticky input bar, sidebar navigation, and workspace management
- **Workspace Operations**: Create, switch, rename, and delete workspaces with independent contexts
- **Configurable Behavior**: Customize system prompt, model, and endpoint via `.env` file
- **Comprehensive Logging**: All interactions logged for traceability and debugging
- **Zero Setup Friction**: Uses uv for dependency management with inline script headers



## License
Apache License 2.0. See [LICENSE](LICENSE) for details.
