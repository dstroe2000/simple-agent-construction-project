
# Local AI Code Assistant for Construction Project Management

## Project Purpose
This project is a modular, privacy-first AI coding assistant designed for construction project management and general coding tasks. It builds on the local-first AI philosophy, running entirely on your machine with no cloud APIs or external dependencies. The agent can read, list, and edit files, and perform essential math operations for sizing and calculations in construction workflows.

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

## Getting Started
1. **Install uv**
   - Linux/macOS: `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Windows: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
2. **Install Ollama**
   - Linux/macOS: `curl -fsSL https://ollama.com/install.sh | sh`
   - Windows: Download from [ollama.com](https://ollama.com/download)
3. **Start Ollama and pull the model**
   ```bash
   ollama serve
   ollama pull qwen3:4b
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

- **Local-First AI**: All data stays on your machine for complete privacy and zero API costs.
- **Modular Design**: Easily extend and review tools via a registry in `tools.py`.
- **Async Agent & Streaming**: Fully async agent and main loop, supporting streaming responses for fast, responsive interaction.
- **Modern Streamlit UI**: Sticky input bar, chat bubbles, sidebar navigation, and Open WebUI-inspired look.
- **Persistent Chat History**: All chat history is stored in a local SQLite database for long-term retention across sessions.
- **Multi-Workspace & Multi-Chat Support**: Start new chats, switch, rename, and delete chats, with per-chat history.
- **Configurable System Prompt**: Easily change assistant behavior via the `.env` file.
- **Logging**: All interactions are logged for traceability and debugging.
- **No Manual Dependency Installation**: Uses uv's inline dependencies in script headers.
- **File Tools**: Read, list, and edit files directly from the chat interface.
- **Math Primitives**: Add, subtract, multiply, divide, sqrt, power for construction calculations.
- **Sidebar Controls**: App name, chat history management (reset, save, import), and navigation.
- **Offline Capable & Fast**: No cloud APIs required; works entirely locally.



## License
Apache License 2.0. See [LICENSE](LICENSE) for details.
