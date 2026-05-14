"""MCP server with example tool."""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agent-skeleton")


@mcp.tool()
def ping(message: str = "hello") -> str:
    """Return a message to verify tool wiring."""
    return f"pong: {message}"


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
