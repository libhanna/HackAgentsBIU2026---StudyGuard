import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4


class MessagesDB:
    """
    Tiny JSON-backed message store shared between the Flask app and the MCP agent.

    IMPORTANT: This class is used from MORE THAN ONE PROCESS at the same time
    (Flask `app.py` AND the MCP `server.py`). If each process keeps its own
    in-memory copy of `self.data` and just overwrites the file on `save()`,
    one process will silently wipe the other process's writes.

    To avoid that, every mutating operation:
      1. Re-reads the file from disk to get the latest state.
      2. Mutates that fresh state.
      3. Writes it back to disk.
    """

    def __init__(self, file_path=None):
        if file_path is None:
            base_dir = Path(__file__).resolve().parent
            file_path = base_dir / "messages_db.json"

        self.file_path = str(file_path)
        # Make sure the file exists on disk with a valid skeleton, so reads
        # from other processes always succeed.
        self.data = self._load_db()
        self._write_data(self.data)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _empty_db(self):
        return {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": None,
            },
            "messages": [],
            "user_messages": [],
        }

    def _load_db(self):
        """Read the JSON file from disk and return a normalized dict."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    content = json.load(f)

                if not isinstance(content, dict):
                    content = self._empty_db()

                if "messages" not in content or not isinstance(content["messages"], list):
                    content["messages"] = []

                if "user_messages" not in content or not isinstance(content["user_messages"], list):
                    content["user_messages"] = []

                if "metadata" not in content or not isinstance(content["metadata"], dict):
                    content["metadata"] = {
                        "created_at": datetime.now().isoformat(),
                        "last_updated": None,
                    }

                return content

            except (json.JSONDecodeError, OSError):
                pass

        return self._empty_db()

    def _write_data(self, data):
        """Write the given dict to disk and update the in-memory cache."""
        data["metadata"]["last_updated"] = datetime.now().isoformat()

        tmp_path = self.file_path + ".tmp"

        # Write to a temp file first, then replace, so a crash mid-write
        # doesn't corrupt the database.
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        os.replace(tmp_path, self.file_path)
        self.data = data

    def save(self):
        """Persist the current in-memory state. Prefer `_write_data` after a reload."""
        self._write_data(self.data)

    # ------------------------------------------------------------------
    # Agent-to-user messages
    # ------------------------------------------------------------------

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
        toast=None,
    ):
        # Reload first, so we don't overwrite messages written by another process.
        data = self._load_db()

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
                "type": action_type,
            },
            "toast": toast or self._default_toast(level),
        }

        data["messages"].append(message)
        self._write_data(data)

        return message

    def get_unsent_messages(self, mark_as_sent=True):
        data = self._load_db()

        messages = [
            msg for msg in data.get("messages", [])
            if not msg.get("sent_to_user", False)
        ]

        if mark_as_sent and messages:
            now = datetime.now().isoformat()

            for msg in messages:
                msg["sent_to_user"] = True
                msg["sent_to_user_at"] = now

            self._write_data(data)
        else:
            # Keep in-memory cache fresh even if we didn't write.
            self.data = data

        return messages

    def get_unread_messages(self):
        data = self._load_db()
        self.data = data

        return [
            msg for msg in data.get("messages", [])
            if not msg.get("read_by_user", False)
        ]

    def mark_message_read(self, message_id):
        data = self._load_db()

        for msg in data.get("messages", []):
            if msg.get("id") == message_id:
                msg["read_by_user"] = True
                msg["read_by_user_at"] = datetime.now().isoformat()
                self._write_data(data)
                return msg

        self.data = data
        return None

    def mark_all_sent_messages_read(self):
        data = self._load_db()
        now = datetime.now().isoformat()
        updated = []

        for msg in data.get("messages", []):
            if msg.get("sent_to_user", False) and not msg.get("read_by_user", False):
                msg["read_by_user"] = True
                msg["read_by_user_at"] = now
                updated.append(msg)

        if updated:
            self._write_data(data)
        else:
            self.data = data

        return updated

    def get_all_messages(self):
        data = self._load_db()
        self.data = data
        return data.get("messages", [])

    def clear_messages(self):
        data = self._load_db()
        data["messages"] = []
        self._write_data(data)

    # ------------------------------------------------------------------
    # User-to-agent messages
    # ------------------------------------------------------------------

    def add_user_message(self, text, conversation_id=None, metadata=None):
        data = self._load_db()

        message = {
            "id": str(uuid4()),
            "created_at": datetime.now().isoformat(),
            "sender": "user",
            "text": text,
            "conversation_id": conversation_id,
            "processed_by_agent": False,
            "processed_by_agent_at": None,
            "metadata": metadata or {},
        }

        if "user_messages" not in data or not isinstance(data["user_messages"], list):
            data["user_messages"] = []

        data["user_messages"].append(message)
        self._write_data(data)

        return message

    def get_unprocessed_user_messages(self, mark_as_processed=True):
        data = self._load_db()

        if "user_messages" not in data or not isinstance(data["user_messages"], list):
            data["user_messages"] = []

        messages = [
            msg for msg in data["user_messages"]
            if not msg.get("processed_by_agent", False)
        ]

        if mark_as_processed and messages:
            now = datetime.now().isoformat()

            for msg in messages:
                msg["processed_by_agent"] = True
                msg["processed_by_agent_at"] = now

            self._write_data(data)
        else:
            self.data = data

        return messages

    def mark_user_message_processed(self, message_id):
        """Mark a single user message as processed by the agent."""
        data = self._load_db()

        for msg in data.get("user_messages", []):
            if msg.get("id") == message_id:
                msg["processed_by_agent"] = True
                msg["processed_by_agent_at"] = datetime.now().isoformat()
                self._write_data(data)
                return msg

        self.data = data
        return None

    def get_all_user_messages(self):
        data = self._load_db()
        self.data = data
        return data.get("user_messages", [])

    # ------------------------------------------------------------------
    # Toast styling
    # ------------------------------------------------------------------

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
                    "textTransform": "uppercase",
                },
            }

        if level == "danger":
            return {
                "type": "error",
                "style": {
                    "background": "#fee2e2",
                    "color": "#7f1d1d",
                    "border": "1px solid #ef4444",
                    "fontWeight": "800",
                    "fontSize": "17px",
                },
            }

        if level == "warning":
            return {
                "type": "warning",
                "style": {
                    "background": "#fef3c7",
                    "color": "#78350f",
                    "border": "1px solid #f59e0b",
                    "fontWeight": "700",
                    "fontSize": "16px",
                },
            }

        return {
            "type": "info",
            "style": {
                "background": "#eff6ff",
                "color": "#1e3a8a",
                "border": "1px solid #3b82f6",
                "fontWeight": "600",
                "fontSize": "16px",
            },
        }
