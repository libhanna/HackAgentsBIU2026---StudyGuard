"""MCP server with one example tool."""

from mcp.server.fastmcp import FastMCP
from agent_skeleton.tools.browser.start_managed_browser import start_managed_browser
from agent_skeleton.tools.browser.close_tab import close_browser_tab_by_url
from agent_skeleton.tools.get_biu_assignment_tasks import get_biu_assignment_tasks
from agent_skeleton.tools.browser.filter import apply_visual_effect_to_current_tab

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

@mcp.tool()
def apply_filter(effect: str, debug_port: int = 9222) -> str:
    """MCP tool that applies a visual filter to the current browser tab."""
    return apply_visual_effect_to_current_tab(effect, debug_port)

@mcp.tool()
def close_tab(url_contains: str, debug_port: int = 9222) -> str:
    """MCP tool that closes a browser tab whose URL contains the given text."""
    return close_browser_tab_by_url(url_contains, debug_port)

def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()