"""MCP server with one example tool."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agent-skeleton")


@mcp.tool()
def ping(message: str = "hello") -> str:
    """Simple MCP tool used to verify that the agent can call tools."""
    return f"pong: {message}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()