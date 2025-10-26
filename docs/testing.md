### Viewing Print Output During Tests

By default, pytest captures all print output and only shows it if a test fails. To see print statements (such as `print("Summary:", summary)`) even when tests pass, use the `-s` option:

```bash
pytest -s tests/test_agent.py
```

This will display all print output in your terminal during the test run.
# Testing the AIAgent

This document describes the test suite for the `simple-agent-construction-project` and provides instructions for running the tests, understanding their purpose, and interpreting the results.

## Test Suite Structure

- All tests are located in the `tests/` directory at the root of the repository.
- Tests are written using `pytest` and `pytest-asyncio` for async support.
- Each test file targets a specific module or feature of the agent.

## Current Tests

### `tests/test_agent.py`

- **Purpose:**
  - Tests the `summarize_history` async method of the `AIAgent` class.
- **Test(s):**
  - `test_summarize_history_basic`: Verifies that the agent can summarize a simple chat history and that the summary contains relevant keywords (e.g., "concrete", "foundation", or "curing").
- **Expected Outcome:**
  - The test should pass if the summary is a string and contains expected keywords from the input history.
  - The summary is printed for manual inspection.

## How to Run the Tests

1. **Install dependencies:**
   Ensure you have `pytest` and `pytest-asyncio` installed. You can install them with:
   ```bash
   pip install pytest pytest-asyncio
   ```

2. **Run the tests:**
  From the project root, you can run all tests with:
  ```bash
  pytest
  ```
  To run a specific test file:
  ```bash
  pytest tests/test_agent.py
  ```

  To run a specific test function directly from the command line, use:
  ```bash
  pytest tests/test_agent.py::test_summarize_history_basic
  ```

  Or, you can run the test code interactively in Python:
  ```python
  import asyncio
  from tests.test_agent import test_summarize_history_basic

  asyncio.run(test_summarize_history_basic())
  ```

3. **Interpreting Results:**
   - A passing test will show `PASSED` in the output.
   - If a test fails, review the error message and the printed summary for debugging.

## Adding More Tests

- Add new test files to the `tests/` directory.
- Use `pytest.mark.asyncio` for async test functions.
- Follow the pattern in `test_agent.py` for consistency.

## Notes

- The summarization test requires the Ollama server and model to be available and accessible.
- If the LLM is not running or misconfigured, tests may fail or hang.
- Summaries may vary slightly depending on the model version and prompt.

---

For questions or issues, please consult the project README or open an issue.
