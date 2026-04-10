# minimal-react-agent

A minimal Python ReAct agent demo with an OpenAI-compatible LLM backend and SerpApi-based web search.

> Status: PoC / Demo

## Missing Information (TODO)

The following items still need your confirmation before official release:

- Project formal name confirmation
- One-line introduction final wording
- Target user profile
- Runtime environment statement (OS and Python version baseline)
- Final development status wording
- License owner fields (`[year]`, `[fullname]` in `LICENSE`)
- Real sample output
- Final accepted known limitations
- Public roadmap

## Overview

This project demonstrates a minimal ReAct-style loop:

- OpenAI-compatible LLM client (`HelloAgentsLLM`)
- ReAct prompt builder (`build_react_messages`)
- Agent loop with `Thought` / `Action` parsing (`ReActAgent`)
- Simple tool registry and built-in SerpApi search tool (`ToolManager` + `Search`)

This is a small educational/experimental codebase, not a production framework.

## Features

- Configurable `model`, `base_url`, `api_key`, and `timeout` from environment variables
- Streaming LLM output handling
- ReAct format enforcement (`Thought` then `Action`)
- `Finish[...]` and `ToolName[...]` action parsing
- Repeated-action detection
- Observation truncation to reduce context pollution
- Pluggable tool registration via `ToolManager`
- Built-in `Search` tool backed by SerpApi

## Project Structure

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── requirements.txt
├── src/
│   └── minimal_react_agent/
│       ├── __init__.py
│       ├── llm.py
│       ├── agent.py
│       ├── prompt.py
│       └── tools.py
├── scripts/
│   ├── run_agent.py
│   ├── inspect_prompt.py
│   └── check_env.py
└── .github/
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md
    │   └── feature_request.md
    └── PULL_REQUEST_TEMPLATE.md
```

## Requirements

- Python 3.9+ (recommended)
- OpenAI-compatible API endpoint
- Valid LLM API key
- Valid SerpApi key

## Installation

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt
```

## Configuration

Create `.env` in project root:

```env
LLM_MODEL_ID=your_model_id
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=https://your-openai-compatible-endpoint/v1
LLM_TIMEOUT=60
SERPAPI_API_KEY=your_serpapi_key
```

You may also use `SERPAPI_KEY` instead of `SERPAPI_API_KEY`.

## Quick Start

Run end-to-end demo:

```bash
python scripts/run_agent.py
```

Inspect prompt + raw model output:

```bash
python scripts/inspect_prompt.py
```

Check env loading:

```bash
python scripts/check_env.py
```

## How It Works

1. `build_react_messages()` builds system/user prompts with tool descriptions and history.
2. `ReActAgent.run()` sends messages to LLM and receives streamed output.
3. Agent parses `Thought` and `Action`.
4. If `Action` is `Finish[...]`, the run ends and returns final answer.
5. Otherwise it executes the tool call, captures `Observation`, appends history, and continues.

## Current Limitations

- Only one concrete external tool (`Search`) is provided by default.
- Search currently relies on SerpApi legacy `GoogleSearch` workflow.
- No automated unit tests / CI pipeline yet.
- Packaging metadata (`pyproject.toml`) is not added yet.
- Error handling is basic and console-oriented.

## Security Notes

Do not commit:

- `.env`
- Real API keys or tokens
- Local virtual environments
- Local logs / temp outputs / personal data

## Next Steps

- [ ] Confirm release metadata in the TODO list above
- [ ] Replace LICENSE placeholders
- [ ] Add automated tests and CI
- [ ] Consider migrating SerpApi integration to the new package path
