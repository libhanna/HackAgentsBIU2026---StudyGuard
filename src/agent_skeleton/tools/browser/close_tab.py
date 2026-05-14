import requests
def close_browser_tab_by_url(url_contains: str, debug_port: int = 9222) -> str:
    """
    Close an open browser tab whose URL contains the given text.

    Use this tool only after the agent has decided that a browser tab should be closed.
    The browser must be running with remote debugging enabled.
    Example:
    chrome.exe --remote-debugging-port=9222
    """

    if not url_contains or not url_contains.strip():
        return "Cannot close tab: url_contains is empty."

    base_url = f"http://127.0.0.1:{debug_port}"

    try:
        tabs_response = requests.get(f"{base_url}/json", timeout=5)
        tabs_response.raise_for_status()
        tabs = tabs_response.json()
    except requests.RequestException as e:
        return f"Failed to connect to browser debug port {debug_port}: {e}"

    matching_tabs = []

    for tab in tabs:
        tab_id = tab.get("id")
        tab_url = tab.get("url", "")
        tab_title = tab.get("title", "")

        if tab.get("type") == "page" and url_contains.lower() in tab_url.lower():
            matching_tabs.append({
                "id": tab_id,
                "url": tab_url,
                "title": tab_title,
            })

    if not matching_tabs:
        return f"No open browser tab found with URL containing: {url_contains}"

    if len(matching_tabs) > 1:
        matches_text = "\n".join(
            f"- {tab['title']} | {tab['url']}"
            for tab in matching_tabs
        )

        return (
            "More than one matching tab was found. "
            "Refine url_contains before closing a tab.\n"
            f"{matches_text}"
        )

    tab = matching_tabs[0]

    try:
        close_response = requests.get(f"{base_url}/json/close/{tab['id']}", timeout=5)
        close_response.raise_for_status()
    except requests.RequestException as e:
        return f"Failed to close tab: {e}"

    return f"Closed tab: {tab['title']} | {tab['url']}"