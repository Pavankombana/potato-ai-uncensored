"""
Potato AI Session & Chat Persistence Manager.
Saves conversation histories, prompts, and tool results across sessions.
"""

import os
import json
import time
from typing import List, Dict, Any, Optional

class SessionManager:
    def __init__(self, storage_dir: str):
        self.storage_dir = os.path.abspath(storage_dir)
        os.makedirs(self.storage_dir, exist_ok=True)
        self.file_path = os.path.join(self.storage_dir, "sessions.json")
        self.sessions: Dict[str, Dict[str, Any]] = self._load()

    def _load(self) -> Dict[str, Dict[str, Any]]:
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save(self):
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(self.sessions, f, indent=2)
        except Exception:
            pass

    def create_session(self, title: str = "New chat") -> str:
        session_id = f"sess_{int(time.time() * 1000)}"
        self.sessions[session_id] = {
            "id": session_id,
            "title": title,
            "created_at": time.time(),
            "messages": []
        }
        self._save()
        return session_id

    def list_sessions(self) -> List[Dict[str, Any]]:
        return sorted(self.sessions.values(), key=lambda s: s.get("created_at", 0), reverse=True)

    def get_messages(self, session_id: str) -> List[Dict[str, str]]:
        if session_id in self.sessions:
            return self.sessions[session_id].get("messages", [])
        return []

    def append_message(self, session_id: str, role: str, content: str):
        if session_id in self.sessions:
            self.sessions[session_id]["messages"].append({"role": role, "content": content})
            self._save()

    def update_title(self, session_id: str, title: str):
        if session_id in self.sessions:
            self.sessions[session_id]["title"] = title
            self._save()

    def delete_session(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]
            self._save()
