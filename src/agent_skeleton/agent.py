"""Agno agent that connects to an MCP server and calls a model through OpenRouter."""

import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


async def run_agent() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(BASE_DIR / "server.py")],
    )

    model_id = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY in .env")

    async with MCPTools(server_params=server_params) as mcp_tools:
        agent = Agent(
            name="Basic MCP Agent",
            model=OpenAIChat(
                id=model_id,
                api_key=api_key,
                base_url="https://openrouter.ai/api/v1",
            ),
            tools=[mcp_tools],
            instructions=[
                "You are a basic agent.",
                "Use the available MCP tools when they are useful.",
                "Do not fake tool results.",
            ],
            markdown=True,
        )

        await agent.aprint_response(
            "use start_browser! after that permanently use the get_current_tab_metadata and use close_tab after 40 seconds if the current active tab metadata do not relate to sport or blank! do not wait to feedback from the user and do what you are requested before!"
        )

        print("Agent is running. Press Ctrl+C to stop.")

        while True:
            await asyncio.sleep(1)


def main() -> None:
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()