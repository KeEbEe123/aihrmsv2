from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Intent:
    type: str
    entity: Optional[str] = None


class SimpleAIAgent:
    """Lightweight intent detection placeholder.

    Replace with LangChain/OpenAI chain later.
    """

    LEAVE_PATTERNS = [
        re.compile(r"\b(leave|sick|vacation)\b", re.IGNORECASE),
    ]
    APPROVE_PATTERN = re.compile(r"^approve\s+(\d+)(?:\s+([\w,]+))?", re.IGNORECASE)
    REJECT_PATTERN = re.compile(r"^reject\s+(\d+)", re.IGNORECASE)
    CONFIRM_PATTERN = re.compile(r"^confirm\s+(\d+)", re.IGNORECASE)

    def detect_intent(self, text: str) -> Intent:
        text = text.strip()

        if m := self.APPROVE_PATTERN.search(text):
            return Intent(type="approve", entity=m.group(1) + (":" + (m.group(2) or "") if m.group(2) else ""))
        if m := self.REJECT_PATTERN.search(text):
            return Intent(type="reject", entity=m.group(1))
        if m := self.CONFIRM_PATTERN.search(text):
            return Intent(type="confirm", entity=m.group(1))
        if any(p.search(text) for p in self.LEAVE_PATTERNS):
            return Intent(type="leave")
        return Intent(type="unknown")


