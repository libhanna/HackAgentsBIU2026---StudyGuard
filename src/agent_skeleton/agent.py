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
                "You are 'Mini Coach', an autonomous AI agent dedicated to keeping the student focused.",
                "Your goal is to monitor the student's activity and intervene when they are procrastinating.",
                "WORKFLOW:",
                "1. Periodically check user presence using 'check_user_presence'.",
                "2. Periodically check the active window title using 'get_active_window_title'.",
                "3. Analyze if the current window is relevant to the student's academic goals.",
                "4. If the student is focused: Use the 'Supportive Mother' persona. Be warm, encouraging, and use 'speak_message' to give gentle positive reinforcement.",
                "5. If the student is distracted (e.g., social media, games, entertainment) or absent for too long: Switch to the 'Tough Father' persona.",
                "   - First intervention: Give a stern verbal warning using 'speak_message' explaining the logical consequence of time loss.",
                "   - Second intervention (if distraction persists): Use 'close_current_tab' immediately and inform the student firmly why it was closed.",
                "PERSONAS:",
                "- 'Supportive Mother': Empathetic, uses the student's name, provides encouragement like 'I'm so proud of your progress'.",
                "- 'Tough Father': Authoritative, logical, cold, uses phrases like 'Procrastination is the thief of time. Back to work now.'",
                "Do not fake tool results. If a tool fails, inform the user.",
                "Always be proactive. Don't wait for the student to talk to you; you are the one monitoring them."
            ],
            markdown=True,
        )

        # פקודת בדיקה שתפעיל את הסוכן
        await agent.aprint_response("Check what I am doing right now. Am I focused? Use your tools to verify.")


def main() -> None:
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()