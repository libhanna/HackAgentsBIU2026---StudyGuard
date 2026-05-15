import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4


class MessagesDB:
    def __init__(self, file_path=None):
        if file_path is None:
            base_dir = Path(__file__).resolve().parent
            file_path = base_dir / "messages_db.json"

        self.file_path = str(file_path)
        self.data = self._load_db()

    def _load_db(self):
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)

                if "messages" not in content:
                    content["messages"] = []

                if "metadata" not in content:
                    content["metadata"] = {}

                return content

            except json.JSONDecodeError:
                pass

        return {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": None
            },
            "messages": []
        }

    def save(self):
        self.data["metadata"]["last_updated"] = datetime.now().isoformat()

        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=4)

    def add_message(
        self,
        text,
        title=None,
        level="info",
        sound=False,
        duration=5000,
        expects_reply=False,
        conversation_id=None,
        action_type="none",
        toast=None
    ):
        message = {
            "id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
            "title": title or "",
            "text": text,
            "level": level,
            "sound": sound,
            "duration": duration,
            "expects_reply": expects_reply,
            "conversation_id": conversation_id,
            "sent_to_user": False,
            "sent_to_user_at": None,
            "read_by_user": False,
            "read_by_user_at": None,
            "action": {
                "type": action_type
            },
            "toast": toast or self._default_toast(level)
        }

        self.data["messages"].append(message)
        self.save()

        return message

    def get_unsent_messages(self, mark_as_sent=True):
        messages = [
            msg for msg in self.data.get("messages", [])
            if not msg.get("sent_to_user", False)
        ]

        if mark_as_sent and messages:
            now = datetime.now().isoformat()

            for msg in messages:
                msg["sent_to_user"] = True
                msg["sent_to_user_at"] = now

            self.save()

        return messages

    def get_unread_messages(self):
        return [
            msg for msg in self.data.get("messages", [])
            if not msg.get("read_by_user", False)
        ]

    def mark_message_read(self, message_id):
        for msg in self.data.get("messages", []):
            if msg.get("id") == message_id:
                msg["read_by_user"] = True
                msg["read_by_user_at"] = datetime.now().isoformat()
                self.save()
                return msg

        return None

    def mark_all_sent_messages_read(self):
        now = datetime.now().isoformat()
        updated = []

        for msg in self.data.get("messages", []):
            if msg.get("sent_to_user", False) and not msg.get("read_by_user", False):
                msg["read_by_user"] = True
                msg["read_by_user_at"] = now
                updated.append(msg)

        if updated:
            self.save()

        return updated

    def get_all_messages(self):
        return self.data.get("messages", [])

    def clear_messages(self):
        self.data["messages"] = []
        self.save()

    def _default_toast(self, level):
        if level == "critical":
            return {
                "type": "error",
                "style": {
                    "background": "#7f1d1d",
                    "color": "#ffffff",
                    "border": "2px solid #dc2626",
                    "fontWeight": "900",
                    "fontSize": "18px",
                    "textTransform": "uppercase"
                }
            }

        if level == "danger":
            return {
                "type": "error",
                "style": {
                    "background": "#fee2e2",
                    "color": "#7f1d1d",
                    "border": "1px solid #ef4444",
                    "fontWeight": "800",
                    "fontSize": "17px"
                }
            }

        if level == "warning":
            return {
                "type": "warning",
                "style": {
                    "background": "#fef3c7",
                    "color": "#78350f",
                    "border": "1px solid #f59e0b",
                    "fontWeight": "700",
                    "fontSize": "16px"
                }
            }

        return {
            "type": "info",
            "style": {
                "background": "#eff6ff",
                "color": "#1e3a8a",
                "border": "1px solid #3b82f6",
                "fontWeight": "600",
                "fontSize": "16px"
            }
        }