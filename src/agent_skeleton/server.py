"""MCP server with one example tool."""

from mcp.server.fastmcp import FastMCP
from agent_skeleton.tools.browser.start_managed_browser import start_managed_browser
from agent_skeleton.tools.browser.close_tab import close_browser_tab_by_url
from agent_skeleton.tools.get_biu_assignment_tasks import get_biu_assignment_tasks

mcp = FastMCP("agent-skeleton")


@mcp.tool()
def ping(message: str = "hello") -> str:
    """Simple MCP tool used to verify that the agent can call tools."""
    return f"pong: {message}"

@mcp.tool()
def start_browser(debug_port: int = 9222) -> str:
    """MCP tool that starts a managed browser instance."""
    return start_managed_browser(debug_port)

@mcp.tool()
def get_assignment_tasks() -> list:
    """MCP tool that retrieves BIU assignment tasks."""
    return get_biu_assignment_tasks()

def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()