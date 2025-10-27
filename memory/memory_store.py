import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

from dateutil import tz


class ConversationMemory:
    def __init__(self, storage_path: str = "/workspace/data/memory.json", timezone: Optional[str] = None):
        self.storage_path = storage_path
        self.timezone = timezone or os.getenv("DEFAULT_TIMEZONE", "UTC")
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def _now_local(self) -> str:
        tzinfo = tz.gettz(self.timezone)
        return datetime.now(tzinfo).isoformat()

    def _load(self) -> Dict[str, Any]:
        with open(self.storage_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _save(self, data: Dict[str, Any]) -> None:
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add_message(self, customer_id: str, role: str, content: str) -> None:
        data = self._load()
        history: List[Dict[str, Any]] = data.get(customer_id, [])
        history.append({
            "timestamp": self._now_local(),
            "role": role,
            "content": content,
        })
        data[customer_id] = history[-200:]
        self._save(data)

    def get_history(self, customer_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        data = self._load()
        history: List[Dict[str, Any]] = data.get(customer_id, [])
        return history[-limit:]

    def summarize_history(self, customer_id: str) -> str:
        history = self.get_history(customer_id, limit=50)
        if not history:
            return "No prior conversation history."
        summary_lines = []
        for item in history:
            ts = item.get("timestamp", "")
            role = item.get("role", "user")
            content = item.get("content", "").strip()
            content_short = content if len(content) <= 240 else content[:240] + "…"
            summary_lines.append(f"[{ts}] {role}: {content_short}")
        return "\n".join(summary_lines)