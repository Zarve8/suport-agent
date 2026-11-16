# Support-Ticket Co-pilot

A LangChain/LangGraph support assistant for a retail forex/CFD broker. It classifies tickets, retrieves approved policy content with BM25, drafts cited responses, and escalates sensitive or unsupported requests to human support.

## Project structure

```text
app/
├── main.py              # Console entrypoint
├── agent.py             # Agent initialization and callable interface
├── graph.py             # LangGraph workflow
├── context.py           # Graph state
├── message.py           # Message and output models
├── nodes/               # Individual graph nodes
├── mcp/                 # Knowledge-base and escalation stubs
├── policies.py          # BM25 policy loading and chunking
└── logging_config.py    # Colored logging setup
policies/md/             # Markdown knowledge-base files
tests/                   # Real-model tests with an LLM judge
BUSINESS_CASE.md         # Quantitative business case
```

## Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini
APP_ENV=development
LOG_LEVEL=INFO
LOG_COLOR=true
RECENT_HISTORY_LIMIT=5
```

`OPENAI_API_KEY` is required for model-backed responses and LLM tests. The policy corpus is loaded from `policies/md/` when the agent starts.

## Installation

Using uv:

```bash
uv sync --dev
```

Or use the existing virtual environment:

```bash
.venv/bin/python -m pip install -e .
```

## Run the console agent

```bash
uv run python app/main.py
```

Type a customer question. Enter `exit` or `quit` to stop.

## Run tests

Run all tests:

```bash
uv run pytest -q
```

Run only real-model evaluation tests:

```bash
uv run pytest -q -m llm -n auto -s
```

Run one case:

```bash
uv run pytest -q -m llm -k crypto_deposit -s
```

The LLM tests use the configured OpenAI model both for the co-pilot and for the structured evaluation judge, so they consume API credits and require network access.
