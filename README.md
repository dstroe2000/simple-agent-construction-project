
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
4. **Run the agent**
   ```bash
   uv run main.py
   ```

## References & Origins
This project is based on and inspired by:
- [single-file-ai-agent-tutorial](https://github.com/dstroe2000/single-file-ai-agent-tutorial) (starting point for this codebase)
- [Dave Ebbelaar's implementation](https://github.com/daveebbelaar/single-file-ai-agent-tutorial)
- [Francis Beeson's implementation](https://github.com/leobeeson/single-file-ai-agent-tutorial)
- [Thorsten Ball's tutorial](https://ampcode.com/how-to-build-an-agent)

## Features
- Conversational AI agent for coding and construction project management
- File tools: read, list, and edit files
- Math primitives: add, subtract, multiply, divide, sqrt, power
- Configurable system prompt via `.env`
- Modular tool registry for easy extension
- Logging to `agent.log`
- No API costs, offline capable, and fast

## License
MIT License. See [LICENSE](LICENSE) for details.
