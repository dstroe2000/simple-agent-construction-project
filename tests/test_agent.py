
import sys
import os
import asyncio
import logging
import pytest

# Ensure the project root is in sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent import AIAgent

@pytest.mark.asyncio
async def test_summarize_history_basic():
    agent = AIAgent()
    # Provide a simple chat history
    history = [
        ("How do I pour concrete for a foundation?", "You should prepare the site, build forms, and pour concrete evenly."),
        ("What about curing?", "Keep the concrete moist for at least 7 days to ensure proper curing.")
    ]
    summary = await agent.summarize_history(history)
    assert isinstance(summary, str)
    assert "concrete" in summary.lower()
    assert "foundation" in summary.lower() or "curing" in summary.lower()
    print("Summary:", summary)
