"""Study Guard agent.

Runs three flows:
1. One-time initialization: starts managed browser and opens the UI.
2. Conversation loop: every 2 seconds checks if the user sent a message.
3. Monitoring loop: every 2 minutes checks calendar + browser tab relevance.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

try:
    from agent_skeleton.messages_db import MessagesDB
except ModuleNotFoundError:
    from messages_db import MessagesDB


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

USER_MESSAGE_POLL_SECONDS = 2
MONITORING_POLL_SECONDS = 120

messages_db = MessagesDB()


STUDY_GUARD_INSTRUCTIONS = [
    """
You are Study Guard Agent.
Your job is to help the student follow their own study schedule.

Hard rules:
1. The UI is http://localhost:5173.
2. The UI tab is always allowed.
3. Never close, blur, grayscale, punish, or classify http://localhost:5173 as distracting.
4. Never open, fetch, inspect, or use /newMessage. It is UI-only.
5. Send messages to the user only with save_message_to_user.
6. Before any browser monitoring action, always call get_current_calendar_event.
7. If the current calendar event is Free, empty, no active event, break, or הפסקה, do not inspect tabs and do not punish.
8. Only during an active study/work event may you inspect the active browser tab.
9. Do not call apply_filter unless there is an active study/work event and the active tab is confirmed distracting.
10. Do not call close_tab unless there is an active study/work event, the tab is not localhost:5173, and the tab is clearly distracting with confidence >= 0.9.
11. Do not call start_browser repeatedly.
12. Do not send the same warning repeatedly.

Startup:
1. Call start_browser.
2. Call initialize_study_guard_ui(debug_port=9222).
3. After the UI opens, call get_current_calendar_event.
4. Do not call apply_filter during startup.
5. Do not call close_tab during startup.

Empty calendar:
If today's/current calendar is empty, send one friendly message:
title="לו״ז ריק"
text="שמתי לב שהלו״ז שלך להיום ריק. רוצה שנבנה אותו יחד?"
level="info"
sound=false
expects_reply=true
conversation_id="schedule-setup"

Monitoring:
Every monitoring cycle:
1. Call get_current_calendar_event.
2. If there is no active study/work event, stop the cycle.
3. If the event is Free/break/empty, stop the cycle.
4. Only if there is an active study/work event, call get_current_tab_metadata.
5. If the active tab is localhost:5173, do nothing.
6. Decide whether the active tab is related to the current event.
7. If relevant, do nothing.
8. If unrelated, escalate gradually.
9. Level 1: save_message_to_user only.
10. Level 2: save_message_to_user with sound=true.
11. Level 3: save_message_to_user with sound=true, then apply_filter.
12. Level 4: save_message_to_user with sound=true, then close_tab.
13. Do not close a tab because of mouse inactivity alone.

Conversation:
When the user replies, handle the reply according to conversation_id.
For conversation_id="schedule-setup":
- If the user agrees, ask them to write today's schedule with hours.
- If the user refuses, say you will wait for schedule updates.
For conversation_id="schedule-details":
- Parse the user's schedule.
- If calendar/add_event tools are available, add the events.
- Confirm to the user.

Tone:
Start friendly.
Become firmer only after repeated clear violations.
Never insult the user.
"""
]


def create_server_params() -> StdioServerParameters:
    return StdioServerParameters(
        command=sys.executable,
        args=[str(BASE_DIR / "server.py")],
    )


def create_agent(mcp_tools: MCPTools) -> Agent:
    model_id = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise RuntimeError("Missing OPENROUTER_API_KEY in .env")

    return Agent(
        name="Study Guard Agent",
        model=OpenAIChat(
            id=model_id,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        ),
        tools=[mcp_tools],
        instructions=STUDY_GUARD_INSTRUCTIONS,
        markdown=True,
    )


async def run_agent_prompt(agent: Agent, prompt: str) -> None:
    await agent.aprint_response(prompt)


async def initialize_study_guard(agent: Agent) -> None:
    prompt = """
Run startup initialization exactly once.

Required order:
1. Call start_browser.
2. Call initialize_study_guard_ui(debug_port=9222).
3. Call get_current_calendar_event.

Important:
- Do not call apply_filter.
- Do not call close_tab.
- Do not inspect tabs during initialization.
- Do not open /newMessage.
- Do not send a warning during initialization.

After checking the calendar:
- If the calendar is empty today, send one setup message using save_message_to_user:
  title="לו״ז ריק"
  text="שמתי לב שהלו״ז שלך להיום ריק. רוצה שנבנה אותו יחד?"
  level="info"
  sound=false
  duration=5000
  expects_reply=true
  conversation_id="schedule-setup"
- If there is an active event, do not punish yet. Monitoring will handle it in the next cycle.
"""

    await run_agent_prompt(agent, prompt)


def get_message_text(message: dict[str, Any]) -> str:
    return str(message.get("text") or message.get("message") or "").strip()


def get_conversation_id(message: dict[str, Any]) -> str | None:
    return message.get("conversation_id") or message.get("conversationId")


async def handle_user_message(agent: Agent, message: dict[str, Any]) -> None:
    message_id = message.get("id")
    text = get_message_text(message)
    conversation_id = get_conversation_id(message)

    if not text:
        if message_id:
            messages_db.mark_user_message_processed(message_id)
        return

    prompt = f"""
The user sent a message to the agent.

conversation_id: {conversation_id}
user_message: {text}

Handle this user reply.

Rules:
1. Reply to the user only by calling save_message_to_user.
2. Do not call /newMessage.
3. Do not inspect browser tabs.
4. Do not call apply_filter.
5. Do not call close_tab.
6. Do not call start_browser.
7. Keep the reply short and useful.

Conversation handling:
If conversation_id is "schedule-setup":
- If the user agrees to build the schedule, ask them to write today's schedule with hours.
- Use conversation_id="schedule-details" in your next message.
- If the user refuses, say you will wait for schedule updates.
- If the answer is unclear, ask again politely.

If conversation_id is "schedule-details":
- Treat the message as the user's schedule for today.
- Extract events with start time, end time, and topic.
- If an add_event/calendar tool exists, add the events.
- Then confirm that the schedule was saved.
- If the schedule is unclear, ask for a clearer format.

If conversation_id is missing or unknown:
- Answer as Study Guard, but do not perform browser actions.
"""

    await run_agent_prompt(agent, prompt)

    if message_id:
        messages_db.mark_user_message_processed(message_id)


async def conversation_loop(agent: Agent) -> None:
    print("[Agent] Conversation loop started. Checking user messages every 2 seconds.", file=sys.stderr)

    while True:
        try:
            user_messages = messages_db.get_unprocessed_user_messages()

            for message in user_messages:
                await handle_user_message(agent, message)

        except Exception as e:
            print(f"[Agent] Conversation loop error: {e}", file=sys.stderr)

        await asyncio.sleep(USER_MESSAGE_POLL_SECONDS)


async def monitoring_cycle(agent: Agent) -> None:
    prompt = """
Run one monitoring cycle.

Required order:
1. Call get_current_calendar_event.
2. If the result is Free, empty, no active event, break, or הפסקה:
   stop immediately. Do not call get_current_tab_metadata.
3. Only if there is an active study/work event:
   call get_current_tab_metadata.
4. If the active tab URL starts with http://localhost:5173:
   do nothing.
5. Decide whether the active tab is relevant to the current calendar event.
6. If the tab is relevant:
   do nothing.
7. If the tab is unrelated:
   escalate gradually using save_message_to_user.
8. Use apply_filter only if escalation level is 3 or higher.
9. Use close_tab only if escalation level is 4, confidence >= 0.9, and the tab is clearly distracting.
10. Never close, blur, or punish localhost:5173.
11. Never open or inspect /newMessage.
"""

    await run_agent_prompt(agent, prompt)


async def monitoring_loop(agent: Agent) -> None:
    print("[Agent] Monitoring loop started. Checking schedule and browser every 2 minutes.", file=sys.stderr)

    while True:
        try:
            await monitoring_cycle(agent)

        except Exception as e:
            print(f"[Agent] Monitoring loop error: {e}", file=sys.stderr)

        await asyncio.sleep(MONITORING_POLL_SECONDS)


async def run_agent() -> None:
    server_params = create_server_params()

    async with MCPTools(server_params=server_params) as mcp_tools:
        agent = create_agent(mcp_tools)

        await initialize_study_guard(agent)

        print("[Agent] Agent is running. Press Ctrl+C to stop.", file=sys.stderr)

        await asyncio.gather(
            conversation_loop(agent),
            monitoring_loop(agent),
        )


def main() -> None:
    asyncio.run(run_agent())


if __name__ == "__main__":
    main()