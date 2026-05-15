from mcp.server.fastmcp import FastMCP
from playwright.async_api import async_playwright
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

mcp = FastMCP("browser-tools")

_playwright = None
_browser: Browser | None = None
_context: BrowserContext | None = None


async def get_browser_context() -> BrowserContext:
    global _playwright, _browser, _context

    if _context is not None:
        return _context

    _playwright = await async_playwright().start()

    _browser = await _playwright.chromium.launch(
        headless=False
    )

    _context = await _browser.new_context()

    return _context

_playwright = None
_browser = None


async def get_managed_browser(debug_port: int = 9222):
    global _playwright, _browser

    if _browser is not None and _browser.is_connected():
        return _browser

    _playwright = await async_playwright().start()

    _browser = await _playwright.chromium.connect_over_cdp(
        f"http://127.0.0.1:{debug_port}"
    )

    return _browser


async def open_tab(url: str, debug_port: int = 9222) -> dict:
    """
    Opens or focuses a tab in the existing managed browser.
    Connects to the browser through the remote debugging port.
    Does not launch a new browser window.
    """

    browser = await get_managed_browser(debug_port)

    if not browser.contexts:
        return {
            "success": False,
            "error": "No browser context found. Make sure start_browser was called first."
        }

    context = browser.contexts[0]

    normalized_url = url.rstrip("/")

    for page in context.pages:
        if page.url.rstrip("/") == normalized_url:
            await page.bring_to_front()
            return {
                "success": True,
                "status": "existing_tab_focused",
                "url": page.url
            }

    page = await context.new_page()
    await page.goto(url)
    await page.bring_to_front()

    return {
        "success": True,
        "status": "new_tab_opened",
        "url": page.url
    }


async def open_ui_tab(debug_port: int = 9222) -> dict:
    """
    Opens or focuses the study guard UI tab.
    """

    return await open_tab("http://localhost:5173", debug_port=debug_port)