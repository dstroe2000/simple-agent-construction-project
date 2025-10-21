
"""
main.py - Entry point for the Local AI Code Assistant

Intentions and Structure:
- This script launches a conversational AI agent for coding and construction project management.
- Loads configuration (endpoint, model, system prompt) from a .env file for flexibility.
- Uses argparse for command-line overrides of model and endpoint.
- Handles user interaction loop, printing responses and managing session.
- All imports are placed at the top for clarity and review.
- Logging is set up for both file and console output, and verbose HTTP logs are suppressed.
- The agent logic is separated into agent.py for modularity.
"""
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "ollama",
#     "pydantic",
#     "python-dotenv",
# ]
# ///

import os
import sys
import argparse
import logging
from agent import AIAgent
from dotenv import load_dotenv


# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[logging.FileHandler("agent.log")]
)

# Suppress verbose HTTP logs
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)

def main():
    load_dotenv()
    endpoint = os.getenv("ENDPOINT")
    model = os.getenv("MODEL", "qwen3:4b")
    system_prompt = os.getenv("SYSTEM_PROMPT")

    parser = argparse.ArgumentParser(
        description="🏠 Local AI Code Assistant - Private, fast, and cost-free conversational AI agent with file editing capabilities"
    )
    parser.add_argument(
        "--model", 
        default=model,
        help="Ollama model to use - compact, efficient models for local execution (default: value from .env or qwen3:4b)"
    )
    parser.add_argument(
        "--server",
        default=endpoint,
        help="Ollama server address for remote execution (default: value from .env or localhost)"
    )
    args = parser.parse_args()

    agent = AIAgent(args.model, args.server, system_prompt)

    print("🏠 Local AI Code Assistant (Ollama)")
    print("=====================================")
    print(f"🤖 Running {args.model} locally - your data stays private!")
    print("📁 I can read, list, and edit files through natural conversation.")
    if args.server:
        print(f"🌐 Connected to Ollama server: {args.server}")
    else:
        print("💻 Using local Ollama server (completely private)")
    print("💡 Benefits: No API costs, offline capable, lightning fast!")
    print()
    print("Type 'exit' or 'quit' to end the conversation.")
    print()

    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ["exit", "quit"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            print("\nAssistant: ", end="", flush=True)
            response = agent.chat(user_input)
            print(response)
            print()

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")
            print()


if __name__ == "__main__":
    main()
