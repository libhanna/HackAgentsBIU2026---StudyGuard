from flask import Flask, jsonify, request
from flask_cors import CORS
from database import CalendarDB
from datetime import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"]}})
db = CalendarDB()

# 1. /health - Returns server status
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }), 200

# 2. /calendar - Returns the synced calendar data
@app.route('/calendar', methods=['GET'])
def get_calendar():
    # Force a sync for testing purposes or live updates
    db.sync_with_google()
    return jsonify(db.data.get("events", {})), 200

# 3. /tasks - Returns the list of tasks
@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(db.data.get("tasks", [])), 200

# 4. /newMessage - Checks for new messages in the queue
@app.route('/newMessage', methods=['GET'])
def get_new_message():
    msg = db.get_latest_message()
    if msg:
        return jsonify({"has_new": True, "message": msg}), 200
    return jsonify({"has_new": False, "message": None}), 200

# 5. /sendMessage - User sends a message to the system
@app.route('/sendMessage', methods=['POST'])
def send_message():
    data = request.json
    user_msg = data.get("message", "")
    
    if not user_msg:
        return jsonify({"error": "No message provided"}), 400
    
    # Store the message in DB
    db.add_message(f"User: {user_msg}")
    
    # Future integration: Pass 'user_msg' to AI Agent here
    
    return jsonify({
        "status": "received",
        "response": f"Message '{user_msg}' saved to DB!"
    }), 200

if __name__ == '__main__':
    # Default Flask port is 5000
    app.run(debug=True)