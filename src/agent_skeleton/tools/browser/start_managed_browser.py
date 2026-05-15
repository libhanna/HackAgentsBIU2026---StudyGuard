import os
import subprocess
import time
import urllib.request
from pathlib import Path


def is_managed_browser_running(debug_port: int = 9222) -> bool:
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{debug_port}/json/version",
            timeout=1
        ) as response:
            return response.status == 200
    except Exception:
        return False


def start_managed_browser(debug_port: int = 9222) -> str:
    """Start a managed browser instance with remote debugging enabled.

    This function is idempotent:
    if the managed browser is already running, it will not open another window.
    """

    if is_managed_browser_running(debug_port):
        return f"Managed browser is already running on debug port {debug_port}."

    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
    ]

    browser_path = None

    for path in chrome_paths:
        if Path(path).exists():
            browser_path = path
            break

    if not browser_path:
        edge_paths = [
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        ]

        for path in edge_paths:
            if Path(path).exists():
                browser_path = path
                break

        if not browser_path:
            return "Could not find Chrome or Edge executable."

    base_dir = Path(__file__).resolve().parent
    profile_dir = base_dir / ".managed-browser-profile"
    profile_dir.mkdir(exist_ok=True)

    args = [
        browser_path,
        f"--remote-debugging-port={debug_port}",
        f"--user-data-dir={profile_dir}",
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

    for _ in range(20):
        if is_managed_browser_running(debug_port):
            return (
                f"Managed browser started on debug port {debug_port}. "
                f"Profile directory: {profile_dir}"
            )
        time.sleep(0.25)

    return (
        f"Browser process was started, but DevTools did not respond on port {debug_port}. "
        f"Profile directory: {profile_dir}"
    )