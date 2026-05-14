from bs4 import BeautifulSoup
import pygetwindow as gw
from selenium import webdriver
import time

def is_chrome_in_front():
    #  מקבל את החלון הפעיל כרגע במערכת ההפעלה
    active_window = gw.getActiveWindow()
    if active_window is None:
        return False

    # בודק אם המילה "Google Chrome" מופיעה בכותרת החלון הפעיל
    return "Google Chrome" in active_window.title


def get_last_tab_metadata(driver):
    # שליפת המקור של הדף
    metadata = {}
    if is_chrome_in_front():
        driver.switch_to.window(driver.window_handles[-1])
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # חילוץ תגית התיאור (Description) מה-Meta
        meta_desc = soup.find("meta", attrs={"name": "description"})
        description = meta_desc["content"] if meta_desc else "No description available"

        # חילוץ הכותרת הראשית (H1) הראשונה בדף
        h1_tag = soup.find("h1")
        h1_text = h1_tag.get_text(strip=True) if h1_tag else "No H1 header found"

        # בניית המילון (Dictionary)
        metadata = {
            "title": driver.title,
            "url": driver.current_url,
            "h1": h1_text,
            "description": description,
            "tab_id": driver.current_window_handle
        }

    return metadata

# --- הרצה לדוגמה ---
driver = webdriver.Chrome()
driver.get("https://en.wikipedia.org/wiki/Artificial_intelligence")
time.sleep(20)
# קבלת המידע
print(get_last_tab_metadata(driver))
driver.quit()