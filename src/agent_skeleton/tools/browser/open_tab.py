from mcp.server.fastmcp import FastMCP
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


async def open_tab(url: str) -> dict:
    """
    Opens a new browser tab with the given URL.
    If a tab with the same URL already exists, it focuses that tab instead.
    Does not open a new browser window if a browser already exists.
    """

    context = await get_browser_context()

    for page in context.pages:
        if page.url.rstrip("/") == url.rstrip("/"):
            await page.bring_to_front()
            return {
                "success": True,
                "status": "existing_tab_focused",
                "url": page.url
            }

    page: Page = await context.new_page()
    await page.goto(url)
    await page.bring_to_front()

    return {
        "success": True,
        "status": "new_tab_opened",
        "url": page.url
    }



async def open_ui_tab() -> dict:
    """
    Opens or focuses the study guard UI tab.
    """

    return await open_tab("http://localhost:5173")
