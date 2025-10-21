
"""
tools.py - Tool implementations and registry for the Local AI Code Assistant

Intentions and Structure:
- Contains all tool functions (math and file operations) used by the agent.
- Math primitives (add, subtract, multiply, divide, sqrt, power) are provided for construction project calculations.
- File tools (read_file, list_files, edit_file) enable file management and editing.
- All tool functions are pure and stateless for easy testing and reuse.
- The tool_registry dictionary maps tool names to their function, input schema, and description.
- This registry is loaded by the agent for modularity and extensibility.
- All imports are placed at the top for clarity and review.
"""
import math
from typing import Dict, Any
import os

# Tool function implementations
def add(a: float, b: float) -> str:
    return f"Result: {a + b}"

def subtract(a: float, b: float) -> str:
    return f"Result: {a - b}"

def multiply(a: float, b: float) -> str:
    return f"Result: {a * b}"

def divide(a: float, b: float) -> str:
    if b == 0:
        return "Error: Division by zero"
    return f"Result: {a / b}"

def sqrt(x: float) -> str:
    if x < 0:
        return "Error: Cannot take square root of negative number"
    return f"Result: {math.sqrt(x)}"

def power(base: float, exponent: float) -> str:
    return f"Result: {math.pow(base, exponent)}"

# File tools (stubs, to be implemented or imported as needed)
def read_file(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        return f"File contents of {path}:\n{content}"
    except FileNotFoundError:
        return f"File not found: {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

def list_files(path: str) -> str:
    # ...existing code...
    try:
        if not os.path.exists(path):
            return f"Path not found: {path}"
        items = []
        for item in sorted(os.listdir(path)):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                items.append(f"[DIR]  {item}/")
            else:
                items.append(f"[FILE] {item}")
        if not items:
            return f"Empty directory: {path}"
        return f"Contents of {path}:\n" + "\n".join(items)
    except Exception as e:
        return f"Error listing files: {str(e)}"

def edit_file(path: str, old_text: str, new_text: str) -> str:
    # ...existing code...
    try:
        if os.path.exists(path) and old_text:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if old_text not in content:
                return f"Text not found in file: {old_text}"
            content = content.replace(old_text, new_text)
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully edited {path}"
        else:
            dir_name = os.path.dirname(path)
            if dir_name:
                os.makedirs(dir_name, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(new_text)
            return f"Successfully created {path}"
    except Exception as e:
        return f"Error editing file: {str(e)}"

# Tool registry: name -> (function, input_schema, description)
tool_registry: Dict[str, Dict[str, Any]] = {
    "add": {
        "function": add,
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
        },
        "description": "Add two numbers.",
    },
    "subtract": {
        "function": subtract,
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
        },
        "description": "Subtract second number from first number.",
    },
    "multiply": {
        "function": multiply,
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "First number"},
                "b": {"type": "number", "description": "Second number"},
            },
            "required": ["a", "b"],
        },
        "description": "Multiply two numbers.",
    },
    "divide": {
        "function": divide,
        "input_schema": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "Numerator"},
                "b": {"type": "number", "description": "Denominator"},
            },
            "required": ["a", "b"],
        },
        "description": "Divide first number by second number.",
    },
    "sqrt": {
        "function": sqrt,
        "input_schema": {
            "type": "object",
            "properties": {
                "x": {"type": "number", "description": "Number to take square root of"},
            },
            "required": ["x"],
        },
        "description": "Calculate the square root of a number.",
    },
    "power": {
        "function": power,
        "input_schema": {
            "type": "object",
            "properties": {
                "base": {"type": "number", "description": "Base number"},
                "exponent": {"type": "number", "description": "Exponent"},
            },
            "required": ["base", "exponent"],
        },
        "description": "Raise a number to a power.",
    },
    "read_file": {
        "function": read_file,
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to the file to read"},
            },
            "required": ["path"],
        },
        "description": "Read the contents of a file at the specified path",
    },
    "list_files": {
        "function": list_files,
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The directory path to list (defaults to current directory)"},
            },
            "required": [],
        },
        "description": "List all files and directories in the specified path",
    },
    "edit_file": {
        "function": edit_file,
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "The path to the file to edit"},
                "old_text": {"type": "string", "description": "The text to search for and replace (leave empty to create new file)"},
                "new_text": {"type": "string", "description": "The text to replace old_text with"},
            },
            "required": ["path", "new_text"],
        },
        "description": "Edit a file by replacing old_text with new_text. Creates the file if it doesn't exist.",
    },
}
