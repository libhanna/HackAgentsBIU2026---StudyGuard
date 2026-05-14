import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import CalendarDB
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})
db = CalendarDB()

# הגדרת הלקוח של OpenRouter (השתמש במפתח שלך מה-.env)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200

# 2. /calendar - מחזיר רק את רשימת ה-events כפי שביקשת
@app.route('/calendar', methods=['GET'])
def get_calendar():
    db.sync_with_google()
    
    # שליפת כל האירועים מכל התאריכים ואיחודם לרשימה אחת שטוחה
    all_events = []
    events_by_date = db.data.get("events", {})
    
    for date in events_by_date:
        all_events.extend(events_by_date[date])
    
    return jsonify({"events": all_events}), 200

# 3. /tasks - רשימת משימות
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(db.data.get("tasks", [])), 200

# 4. /newMessage - מחזיר את הודעת ה-AI האחרונה
@app.route('/newMessage', methods=['GET'])
def get_new_message():
    msg = db.get_latest_message()
    if msg:
        return jsonify({"has_new": True, "message": msg}), 200
    return jsonify({"has_new": False, "message": None}), 200

# 5. /sendMessage - מעבד את ההודעה ומחזיר רק את שמות האירועים מופרדים בפסיק
@app.route('/sendMessage', methods=['POST'])
def send_message():
    data = request.json
    user_msg = data.get("message", "")
    
    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    try:
        # שליפת הלו"ז העדכני
        calendar_data = db.data.get("events", {})
        
        # פנייה ל-AI כדי שינתח את הבקשה
        response = client.chat.completions.create(
             model="openai/gpt-4o-mini",
             messages=[
                 {
                      "role": "system", 
                      "content": (
                         f"You are StudyGuard, a professional AI assistant. Use this calendar data: {calendar_data}. "
                         "STRICT RULES: "
                         "1. Always respond in ENGLISH only. "
                         "2. If the user asks about their schedule, provide the event topics separated by commas. "
                         "3. Keep your responses concise and professional."
            )
        },
        {"role": "user", "content": user_msg}
    ]
)

        ai_text = response.choices[0].message.content
        
        # שמירת התשובה ב-DB
        db.add_message(ai_text)
        
        # החזרת התשובה בפורמט שביקשת (למשל: "pizza party, learning for cs course")
        return ai_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)