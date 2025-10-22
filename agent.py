import logging
from typing import List, Dict, Any
from ollama import AsyncClient  # type: ignore
from pydantic import BaseModel  # type: ignore
from tools import tool_registry
import inspect


"""
AIAgent implementation for a local AI code assistant.

Intentions and Design:
- The agent is designed to operate as a conversational coding assistant, with file and math tool capabilities for construction project management.
- Tools are externalized in a registry (see tools.py) for modularity, extensibility, and easier review/testing.
- The agent loads its available tools from the registry and can execute them based on user or model requests.
- The system prompt is configurable via .env for flexible assistant behavior.
- All imports are placed at the top for clarity and dependency review.
"""

class Tool(BaseModel):
    """
    Represents a callable tool for the agent, including its name, description, and input schema.
    """
    name: str
    description: str
    input_schema: Dict[str, Any]


class AIAgent:
    """
    Local AI code assistant agent.
- The agent is designed to operate as a conversational coding assistant, with file and math tool capabilities for construction project management.
- Tools are externalized in a registry (see tools.py) for modularity, extensibility, and easier review/testing.
- The agent loads its available tools from the registry and can execute them based on user or model requests.
- The system prompt is configurable via .env for flexible assistant behavior.
- All imports are placed at the top for clarity and dependency review.
    """
    def __init__(self, model: str = "qwen3:4b", server: str = None, system_prompt: str = None):
        """
        Initialize the agent.
        Args:
            model (str): The Ollama model to use.
            server (str): The Ollama server endpoint.
            system_prompt (str): The system prompt for the assistant (configurable via .env).
        """
        self.model = model
        self.server = server
        self.system_prompt = system_prompt or (
            "You are a helpful coding assistant operating in a terminal environment. Output only plain text without markdown formatting, as your responses appear directly in the terminal. Be concise but thorough, providing clear and practical advice with a friendly tone. Don't use any asterisk characters in your responses."
        )
        if server:
            self.client = AsyncClient(host=server)
        else:
            self.client = AsyncClient()
        self.messages: List[Dict[str, Any]] = []
        self.tools: List[Tool] = []
        self._setup_tools()

    def _setup_tools(self):
        self.tools = [
            Tool(
                name=name,
                description=tool_info["description"],
                input_schema=tool_info["input_schema"],
            )
            for name, tool_info in tool_registry.items()
        ]
        print(self.tools)

    def _execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> str:
        """
        Execute a tool by name using the provided input.
            - Load tool definitions from the external registry (tools.py).
            - This enables modularity and makes it easy to add, remove, or update tools.
        Args:
            tool_name (str): The name of the tool to execute.
            tool_input (Dict[str, Any]): The input arguments for the tool.
        Returns:
            str: The result of the tool execution or an error message.
        """
        logging.info(f"Executing tool: {tool_name} with input: {tool_input}")
        try:
            tool_info = tool_registry.get(tool_name)
            if not tool_info:
                return f"Unknown tool: {tool_name}"
            func = tool_info["function"]
            sig = inspect.signature(func)
            args = [tool_input[param] for param in sig.parameters]
            #if inspect.iscoroutinefunction(func):
            #    return await func(*args)
            return func(*args)
        except Exception as e:
            logging.error(f"Error executing {tool_name}: {str(e)}")
            return f"Error executing {tool_name}: {str(e)}"


    async def chat(self, user_input: str):
        """
        Handle a user message, interact with the Ollama model, and execute any requested tools.
        Args:
            user_input (str): The user's message.
        Yields:
            str: Chunks of the assistant's response.
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
                messages_with_system = [
                    {
                        "role": "system",
                        "content": self.system_prompt
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
                            logging.info(f"Tool result: {result[:500]}...")
                            tool_results.append({
                                "role": "tool",
                                "content": result,
                                "tool_call_id": tool_call.get("id", "")
                            })
                        self.messages.extend(tool_results)
                        tool_call_handled = True
                if not tool_call_handled:
                    break  # Exit loop if no tool call was handled
            except Exception as e:
                yield f"Error: {str(e)}"
                break
