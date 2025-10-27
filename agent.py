
"""
agent.py
--------
Async AI agent implementation for the Local AI Code Assistant.

Intentions and Design:
- The agent is a modular, privacy-first conversational coding assistant for construction project management and general coding tasks.
- Supports file and math tools via an external registry (see tools.py) for extensibility and easy review.
- Loads configuration (model, endpoint, system prompt) from .env or via arguments.
- Fully async, using Ollama AsyncClient for streaming LLM responses.
- Supports digital twin/context summary injection for each workspace/chat, enabling persistent memory and context switching.
- Designed for use in both CLI (main.py) and Streamlit UI (streamlit_app.py).

Key Classes:
- Tool: Pydantic model representing a callable tool (name, description, input schema).
- AIAgent: The main agent class, supporting chat, tool execution, and context summarization.

Usage:
    agent = AIAgent(model, endpoint, system_prompt, context_summary)
    async for chunk in agent.chat(user_input):
        ...
    summary = await agent.summarize_history(history)
"""

import logging
from typing import List, Dict, Any
from ollama import AsyncClient  # type: ignore
from pydantic import BaseModel  # type: ignore
from tools import tool_registry
import inspect
import time




class Tool(BaseModel):
    """
    Represents a callable tool for the agent, including its name, description, and input schema.
    Used for dynamic tool loading and function calling via the LLM.
    """
    name: str
    description: str
    input_schema: Dict[str, Any]



class AIAgent:
    """
    Local AI code assistant agent (async, modular, streaming).

    - Supports conversational coding and construction project management.
    - Loads tools from an external registry for extensibility.
    - Accepts a context summary (digital twin) for persistent memory per workspace.
    - Async, streaming responses via Ollama AsyncClient.
    - Used in both CLI and Streamlit UI.
    """

    def __init__(self, model: str = "qwen3:4b", server: str = None, system_prompt: str = None, context_summary: str = None):
        """
        Initialize the agent.
        Args:
            model (str): The Ollama model to use.
            server (str): The Ollama server endpoint.
            system_prompt (str): The system prompt for the assistant (configurable via .env).
            context_summary (str, optional): Digital twin/context summary to inject as persistent memory.
        """
        self.model = model
        self.server = server
        self.system_prompt = system_prompt or (
            "You are a helpful coding assistant operating in a terminal environment. Output only plain text without markdown formatting, as your responses appear directly in the terminal. Be concise but thorough, providing clear and practical advice with a friendly tone. Don't use any asterisk characters in your responses."
        )
        self.context_summary = context_summary
        if server:
            self.client = AsyncClient(host=server)
        else:
            self.client = AsyncClient()
        self.messages: List[Dict[str, Any]] = []
        self.tools: List[Tool] = []
        self._setup_tools()

    def _setup_tools(self):
        """
        Load all available tools from the external registry (tools.py).
        Populates self.tools with Tool objects for function calling.
        """
        self.tools = [
            Tool(
                name=name,
                description=tool_info["description"],
                input_schema=tool_info["input_schema"],
            )
            for name, tool_info in tool_registry.items()
        ]

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a tool by name using the provided input.
        Loads tool definitions from the external registry (tools.py).
        Args:
            tool_name (str): The name of the tool to execute.
            tool_input (Dict[str, Any]): The input arguments for the tool.
        Returns:
            str: The result of the tool execution or an error message (if required arguments are missing).
        """
        logging.info(f"Executing tool: {tool_name} with input: {tool_input}")
        try:
            tool_info = tool_registry.get(tool_name)
            if not tool_info:
                return f"Unknown tool: {tool_name}"
            func = tool_info["function"]
            sig = inspect.signature(func)
            args = []
            for param in sig.parameters:
                if param not in tool_input:
                    return f"Missing required argument '{param}' for tool '{tool_name}'."
                args.append(tool_input[param])
            return func(*args)
        except Exception as e:
            logging.error(f"Error executing {tool_name}: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"

    async def chat(self, user_input: str):
        """
        Handle a user message, interact with the Ollama model, and execute any requested tools.
        Injects the context summary (if provided) as part of the system prompt for persistent memory.
        Args:
            user_input (str): The user's message.
        Yields:
            str: Chunks of the assistant's response and surfaces tool errors to the user.
        """
        logging.info(f"User input: {user_input}")
        self.messages.append({"role": "user", "content": user_input})
        ollama_tools = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            }
            for tool in self.tools
        ]
        while True:
            try:
                # Inject context summary if available
                system_content = self.system_prompt
                if self.context_summary:
                    system_content += f"\n\n[Context Summary]: {self.context_summary}"
                messages_with_system = [
                    {
                        "role": "system",
                        "content": system_content
                    }
                ] + self.messages
                stream = await self.client.chat(
                    model=self.model,
                    messages=messages_with_system,
                    tools=ollama_tools,
                    stream=True
                )
                tool_call_handled = False
                async for part in stream:
                    message = part.get("message", {})
                    yield message.get("content", "")
                    tool_calls = message.get("tool_calls", [])
                    if tool_calls:
                        tool_results = []
                        for tool_call in tool_calls:
                            function = tool_call.get("function", {})
                            tool_name = function.get("name")
                            tool_args = function.get("arguments", {})
                            result = self._execute_tool(tool_name, tool_args)
                            logging.info(f"Tool {tool_name} result: {result[:500]}...")
                            tool_results.append({
                                "role": "tool",
                                "content": result,
                                "tool_call_id": tool_call.get("id", "")
                            })
                            # If result is an error, also append a user-facing message
                            if result.startswith("Missing required argument") or result.startswith("Error executing"):
                                self.messages.append({
                                    "role": "assistant",
                                    "content": result
                                })
                        self.messages.extend(tool_results)
                        tool_call_handled = True
                if not tool_call_handled:
                    break  # Exit loop if no tool call was handled
            except Exception as e:
                yield f"Error: {str(e)}"
                break

    async def summarize_history(self, history: list) -> str:
        """
        Summarize a chat history using the LLM.
        Used for digital twin/context memory updates.
        Args:
            history (List[Tuple[str, str]]): List of (user, assistant) message pairs.
        Returns:
            str: A summary of the conversation.
        """
        # Format the history as a string for the LLM
        history_text = "\n".join([
            f"User: {user}\nAssistant: {assistant}" for user, assistant in history
        ])
        prompt = (
            "Summarize the following conversation between a user and an assistant. "
            "Focus on the main topics, decisions, and any important context. "
            "Be concise and clear.\n\n" + history_text
        )
        messages = [
            {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
            {"role": "user", "content": prompt}
        ]
        logging.info(f"[summarize_history] Called with {len(history)} message pairs.")
        logging.debug(f"[summarize_history] Prompt sent to LLM:\n{prompt}")
        start_time = time.time()
        try:
            response = ""
            stream = await self.client.chat(
                model=self.model,
                messages=messages,
                stream=True
            )
            async for part in stream:
                message = part.get("message", {})
                response += message.get("content", "")
            elapsed = time.time() - start_time
            logging.info(f"[summarize_history] LLM summary completed in {elapsed:.2f}s. Length: {len(response)} chars.")
            logging.debug(f"[summarize_history] LLM summary output:\n{response.strip()}")
            return response.strip()
        except Exception as e:
            logging.error(f"[summarize_history] Error during summarization: {str(e)}")
            return f"[Error summarizing history: {str(e)}]"
