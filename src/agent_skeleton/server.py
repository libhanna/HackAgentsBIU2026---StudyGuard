"""MCP server with one example tool."""

# --- Path setup MUST come before any agent_skeleton / database imports ---
import sys
import os
from datetime import datetime


_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
_SRC_DIR = os.path.abspath(os.path.join(_CURRENT_DIR, ".."))           # .../src
_PROJECT_ROOT = os.path.abspath(os.path.join(_CURRENT_DIR, "..", "..")) # project root (for database.py)

for _p in (_SRC_DIR, _PROJECT_ROOT):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from mcp.server.fastmcp import FastMCP
from agent_skeleton.tools.browser.start_managed_browser import start_managed_browser
from agent_skeleton.tools.browser.close_tab import close_browser_tab_by_url
from agent_skeleton.tools.browser.get_current_chrome_metadata import get_active_tab_metadata
from agent_skeleton.tools.get_biu_assignment_tasks import get_biu_assignment_tasks
from agent_skeleton.tools.browser.filter import apply_visual_effect_to_current_tab
from agent_skeleton.tools.browser.start_managed_browser import start_managed_browser
from agent_skeleton.tools.browser.open_tab import open_tab as open_tab_impl

from database import CalendarDB
from messages_db import MessagesDB


mcp = FastMCP("agent-skeleton")
# אתחול ה-Database בתוך השרת
db = CalendarDB()
messages_db = MessagesDB()

@mcp.tool()
def get_current_calendar_event() -> str:
    """
    Checks the user's Google Calendar and returns the topic of the current event.
    Returns 'Free' if no event is scheduled.
    """
    now = datetime.now()
    return db.get_event_at(now)

@mcp.tool()
def ping(message: str = "hello") -> str:
    """Simple MCP tool used to verify that the agent can call tools."""
    return f"pong: {message}"

@mcp.tool()
def start_browser(debug_port: int = 9222) -> str:
    """MCP tool that starts a managed browser instance."""
    return start_managed_browser(debug_port)

@mcp.tool()
def get_assignment_tasks(calendar_url: str) -> str:
    """MCP tool that retrieves BIU assignment tasks from a BIU Moodle calendar export URL."""
    return get_biu_assignment_tasks(calendar_url)


@mcp.tool()
def apply_filter(effect: str, debug_port: int = 9222) -> str:
    """MCP tool that applies a visual filter to the current browser tab."""
    return apply_visual_effect_to_current_tab(effect, debug_port)

@mcp.tool()
def close_tab(url_contains: str, debug_port: int = 9222) -> str:
    """MCP tool that closes a browser tab whose URL contains the given text."""
    return close_browser_tab_by_url(url_contains, debug_port)


@mcp.tool()
async def initialize_study_guard_ui(debug_port: int = 9222) -> dict:
    start_result = start_managed_browser(debug_port=debug_port)
    tab_result = await open_tab_impl(
        url="http://localhost:5173",
        debug_port=debug_port
    )

    return {
        "success": True,
        "start_browser": start_result,
        "open_tab": tab_result
    }

@mcp.tool()
def get_current_tab_metadata(debug_port: int = 9222) -> dict:
    """MCP tool that get the active browser tab metadata."""
    return get_active_tab_metadata(debug_port)

@mcp.tool()
def save_message_to_user(
    text: str,
    title: str = "",
    level: str = "info",
    sound: bool = False,
    duration: int = 5000,
    expects_reply: bool = False,
    conversation_id: str | None = None,
    action_type: str = "none"
) -> dict:
    """
    Save a message from the agent to the user.

    This tool does not send the message directly to the UI.
    It writes the message into messages_db.json.
    The UI/API can later fetch unsent messages and mark them as sent_to_user.
    """

    if not text or not text.strip():
        return {
            "success": False,
            "error": "Message text is required."
        }

    allowed_levels = ["info", "warning", "danger", "critical"]

    if level not in allowed_levels:
        level = "info"

    message = messages_db.add_message(
        text=text.strip(),
        title=title.strip() if title else "",
        level=level,
        sound=sound,
        duration=duration,
        expects_reply=expects_reply,
        conversation_id=conversation_id,
        action_type=action_type
    )

    return {
        "success": True,
        "message": message
    }

def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()