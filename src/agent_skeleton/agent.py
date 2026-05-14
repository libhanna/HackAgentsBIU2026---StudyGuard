"""Example agent client that calls the MCP tool."""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run() -> None:
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["-m", "agent_skeleton.server"],
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool("ping", {"message": "hi"})
            print(result)


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
