@mcp.tool()
def speak_message(text: str) -> str:
    """Plays a voice message through the computer speakers."""
    try:
        engine = pyttsx3.init()
        # ניתן להגדיר פה מהירות וטון אם רוצים להבדיל בין 'אמא' ל'אבא'
        engine.say(text)
        engine.runAndWait()
        return f"Voice message played: {text}"
    except Exception as e:
        return f"Error speaking: {str(e)}