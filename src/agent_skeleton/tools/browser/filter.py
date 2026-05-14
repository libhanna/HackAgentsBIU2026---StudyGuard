import json
import requests
import websocket

def apply_visual_effect_to_current_tab(effect: str, debug_port: int = 9222) -> str:
    """
    Apply a visual effect to the currently available tab in the managed browser.

    effect can be:
    - "grayscale" to make the page black and white
    - "blur" to blur the page
    - "clear" to remove the effect

    Use this tool when the agent decides that a page should be visually blocked
    instead of closing the tab.
    The managed browser must be running with remote debugging enabled.
    """

    effect = effect.strip().lower()

    filters = {
        "grayscale": "grayscale(1)",
        "blur": "blur(6px)",
        "clear": "",
    }

    if effect not in filters:
        return "Invalid effect. Use one of: grayscale, blur, clear."

    base_url = f"http://127.0.0.1:{debug_port}"

    try:
        response = requests.get(f"{base_url}/json", timeout=5)
        response.raise_for_status()
        tabs = response.json()
    except requests.RequestException as e:
        return f"Failed to connect to managed browser on port {debug_port}: {e}"

    page_tabs = [
        tab for tab in tabs
        if tab.get("type") == "page" and tab.get("webSocketDebuggerUrl")
    ]

    if not page_tabs:
        return "No open page tabs found in the managed browser."

    tab = page_tabs[0]
    websocket_url = tab["webSocketDebuggerUrl"]

    filter_value = filters[effect]

    script = f"""
    (() => {{
        document.documentElement.style.filter = {json.dumps(filter_value)};
        document.documentElement.style.transition = "filter 0.2s ease";
        return {{
            effect: {json.dumps(effect)},
            filter: {json.dumps(filter_value)},
            title: document.title,
            url: location.href
        }};
    }})()
    """

    command = {
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": script,
            "returnByValue": True,
        },
    }

    try:
        ws = websocket.create_connection(websocket_url, timeout=5)
        ws.send(json.dumps(command))
        raw_result = ws.recv()
        ws.close()
    except Exception as e:
        return f"Failed to apply visual effect: {e}"

    try:
        result = json.loads(raw_result)
    except json.JSONDecodeError:
        return f"Effect was sent, but failed to parse browser response: {raw_result}"

    if "error" in result:
        return f"Browser returned an error: {result['error']}"

    value = (
        result
        .get("result", {})
        .get("result", {})
        .get("value", {})
    )

    title = value.get("title", tab.get("title", ""))
    url = value.get("url", tab.get("url", ""))

    if effect == "clear":
        return f"Removed visual effect from tab: {title} | {url}"

    return f"Applied {effect} effect to tab: {title} | {url}"