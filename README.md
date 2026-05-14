# Agent Skeleton (MCP, Python)

Minimal skeleton for an MCP server + an example agent client.

## What is included
- MCP server with one example tool (`ping`)
- Example agent client that calls the tool
- Packaging via `pyproject.toml`

## Quick start
1) Create and activate a venv
2) Install:

```bash
pip install -e .
```

3) Run the server (stdio):

```bash
agent-server
```

4) In another terminal, run the example agent:

```bash
agent-client
```

## Where to extend
- Add or modify tools in `src/agent_skeleton/server.py`
- Expand agent logic in `src/agent_skeleton/agent.py`
