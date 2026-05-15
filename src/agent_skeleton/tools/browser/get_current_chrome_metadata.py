from bs4 import BeautifulSoup
import pygetwindow as gw
import time
from agent_skeleton.tools.browser.start_managed_browser import start_managed_browser
import requests

def get_active_tab_metadata(port=9222):
    metadata = {}
    if is_chrome_in_front():
        try:
            # 1. קבלת רשימת הכרטיסיות מהדפדפן
            response = requests.get(f"http://127.0.0.1:{port}/json")
            tabs = response.json()

            # בדרך כלל הכרטיסייה הראשונה ברשימה היא הפעילה ביותר (Last Focused)
            active_tab = None
            for tab in tabs:
                if tab.get('type') == 'page':
                    active_tab = tab
                    break

            if not active_tab:
                return "No active tab found."

            # 2. שימוש ב-URL של הכרטיסייה כדי למשוך את התוכן שלה
            # הערה: אנחנו פונים ל-URL ישירות עם requests
            target_url = active_tab.get('url')

            # נוסיף User-Agent כדי להיראות כמו דפדפן רגיל
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            }

            page_response = requests.get(target_url, headers=headers, timeout=5)
            soup = BeautifulSoup(page_response.text, 'html.parser')

            # 3. חילוץ הנתונים (בדיוק כמו בסלניום)
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc["content"] if meta_desc else "N/A"

            h1_tag = soup.find("h1")
            h1_text = h1_tag.get_text(strip=True) if h1_tag else "N/A"

            metadata =  {
                "tab_id": active_tab.get('id'),
                "title": active_tab.get('title'),
                "url": target_url,
                "h1": h1_text,
                "description": description
            }

        except Exception as e:
            metadata = {e}
    return metadata

def is_chrome_in_front():
    #  מקבל את החלון הפעיל כרגע במערכת ההפעלה
    active_window = gw.getActiveWindow()
    if active_window is None:
        return False

    # בודק אם המילה "Google Chrome" מופיעה בכותרת החלון הפעיל
    return "Google Chrome" in active_window.title

#  --- הרצה לדוגמה ---
# start_managed_browser()
# while (1):
#     time.sleep(10)
#     print(get_active_tab_metadata())