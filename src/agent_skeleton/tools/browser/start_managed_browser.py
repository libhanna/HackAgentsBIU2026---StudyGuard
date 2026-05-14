import os
import subprocess
from pathlib import Path

def start_managed_browser(debug_port: int = 9222) -> str:
    """Start a managed browser instance with remote debugging enabled.

    Use this tool before listing or closing browser tabs.
    This opens a separate browser profile controlled by the study agent.
    """

    browser_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

    if not Path(browser_path).exists():
        browser_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

    if not Path(browser_path).exists():
        return "Could not find Chrome or Edge executable."

    base_dir = Path(__file__).resolve().parent
    profile_dir = base_dir / ".managed-browser-profile"
    profile_dir.mkdir(exist_ok=True)

    args = [
        browser_path,
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={profile_dir}",
        "--new-window",
        "about:blank",
    ]

    try:
        subprocess.Popen(
            args,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
        )
    except Exception as e:
        return f"Failed to start managed browser: {e}"

    return (
        f"Managed browser started on debug port {debug_port}. "
        f"Profile directory: {profile_dir}"
    )