import os
import json
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import CalendarDB
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
from messages_db import MessagesDB

load_dotenv()

app = Flask(__name__)

CORS(
    app,
    origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    supports_credentials=True,
)
db = CalendarDB()
messages_db = MessagesDB()

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
    
    # שליפת כל האירועים רק של היום הנוכחי (לפי תאריך מקומי)
    today_str = datetime.now().strftime("%Y-%m-%d")
    all_events = db.data.get("events", {}).get(today_str, [])
    
    # מיון האירועים לפי שעת ההתחלה, מכיוון שאספנו ממספר יומנים שונים
    all_events = sorted(all_events, key=lambda x: x["start"])
    
    return jsonify({"events": all_events}), 200

# 3. /tasks - רשימת משימות
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(db.data.get("tasks", [])), 200

# 4. /newMessage - מחזיר את הודעת ה-AI האחרונה
@app.route('/newMessage', methods=['GET'])
def get_new_message():
    messages = messages_db.get_unsent_messages(mark_as_sent=True)

    if messages:
        return jsonify({
            "has_new": True,
            "messages": messages
        }), 200

    return jsonify({
        "has_new": False,
        "messages": []
    }), 200

@app.route('/sendMessage', methods=['POST', 'OPTIONS'])
def send_message():
    if request.method == "OPTIONS":
        return "", 204

    data = request.get_json() or {}
    user_msg = data.get("message", "").strip()
    conversation_id = data.get("conversation_id") or data.get("conversationId")

    if not user_msg:
        return jsonify({"error": "No message provided"}), 400

    try:
        saved_message = messages_db.add_user_message(
            text=user_msg,
            conversation_id=conversation_id,
            metadata={
                "source": "vue-ui"
            }
        )

        return jsonify({
            "success": True,
            "queued_for_agent": True,
            "message": saved_message
        }), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)