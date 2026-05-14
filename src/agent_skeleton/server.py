"""MCP server with one example tool."""

import cv2
import pyautogui
import pyttsx3
import pygetwindow as gw
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("agent-skeleton")

@mcp.tool()
def ping(message: str = "hello") -> str:
    """Simple MCP tool used to verify that the agent can call tools."""
    return f"pong: {message}"

# --- כלי 1: זיהוי החלון הפעיל ---
@mcp.tool()
def get_active_window_title() -> str:
    """Returns the title of the window currently in focus."""
    try:
        window = gw.getActiveWindow()
        return window.title if window else "No active window found"
    except Exception as e:
        return f"Error detecting window: {str(e)}"

# --- כלי 2: זיהוי נוכחות פנים ---
@mcp.tool()
def check_user_presence() -> str:
    """Uses the webcam to check if a face is present in front of the computer."""
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            return "Error: Could not access camera."
        
        # צילום מספר פריימים כדי לאפשר למצלמה להסתגל לאור
        for _ in range(5):
            ret, frame = cap.read()
            
        cap.release()
        
        if not ret:
            return "Error: Could not read frame from camera."
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        return "User Present" if len(faces) > 0 else "User Absent"
    except Exception as e:
        return f"Error in face detection: {str(e)}"

# --- כלי 3: סגירת הטאב הנוכחי ---
@mcp.tool()
def close_current_tab() -> str:
    """Closes the current browser tab using a keyboard shortcut."""
    try:
        # בדיקה בסיסית לסוג מערכת ההפעלה יכולה לעזור כאן
        pyautogui.hotkey('ctrl', 'w') 
        return "Action performed: Tab closed."
    except Exception as e:
        return f"Error closing tab: {str(e)}"

# --- כלי 4: דיבור קולי ---
@mcp.tool()
def speak_message(text: str) -> str:
    """Plays a voice message through the computer speakers."""
    try:
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()
        # חשוב לעצור את ה-engine בסיום
        engine.stop()
        return f"Voice message played: {text}"
    except Exception as e:
        return f"Error speaking: {str(e)}"

def main() -> None:
    mcp.run()

if __name__ == "__main__":
    main()