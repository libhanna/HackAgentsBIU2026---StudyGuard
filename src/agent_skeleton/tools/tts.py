import asyncio
import edge_tts
import io
import pygame


def play_tough_voice_wrapper(text, toughness_level=1.0):
    asyncio.run(play_tough_voice(text, 2))

async def play_tough_voice(text, toughness_level=1.0):
    # הגדרות שפה וקול (כפי שעשינו קודם)
    voice = "he-IL-AvriNeural" if any('\u0590' <= c <= '\u05ff' for c in text) else "en-US-GuyNeural"

    pitch_str = f"{int(toughness_level * -20)}Hz"
    rate_str = f"{int(toughness_level * -12)}%"

    # 1. יצירת האודיו בתוך משתנה (בזיכרון RAM) במקום קובץ
    communicate = edge_tts.Communicate(text, voice, pitch=pitch_str, rate=rate_str)

    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]

    # 2. שימוש ב-Pygame כדי לנגן את הנתונים מהזיכרון
    pygame.mixer.init()

    # טעינת הנתונים כאילו היו קובץ
    audio_stream = io.BytesIO(audio_data)
    pygame.mixer.music.load(audio_stream)
    pygame.mixer.music.play()

    # המתנה עד שההשמעה תסתיים
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    pygame.mixer.quit()


# #  --- הרצה לדוגמה ---
if __name__ == "__main__":
    text_to_say_hebrew = "מערכת הנתונים עודכנה. אל תנסה לגשת שוב ללא הרשאה."
    text_to_say_english = "Don't do it"
    play_tough_voice_wrapper(text_to_say_hebrew, 2)