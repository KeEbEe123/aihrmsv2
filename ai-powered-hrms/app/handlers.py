from __future__ import annotations

from datetime import date, datetime
from typing import Dict, List, Optional

from app.ai_agent import SimpleAIAgent
from app.config import Settings, get_settings
from app.database import SupabaseDatabase, get_db
from app.notifier import Notifier


class LeaveService:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        db: Optional[SupabaseDatabase] = None,
        notifier: Optional[Notifier] = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.db = db or get_db(self.settings)
        self.notifier = notifier or Notifier(self.settings)
        self.agent = SimpleAIAgent()

    async def process_incoming_message(self, from_number: str, message_body: str) -> Dict:
        intent = self.agent.detect_intent(message_body)
        match intent.type:
            case "leave":
                return await self._handle_leave_request(from_number, message_body)
            case "approve":
                return await self._handle_approve(from_number, intent.entity)
            case "reject":
                return await self._handle_reject(from_number, intent.entity)
            case "confirm":
                return await self._handle_confirm(from_number, intent.entity)
            case _:
                return {"message": "Unrecognized. Try: 'I need leave on Oct 15', 'approve 42', 'reject 42', 'confirm 42'"}

    async def _handle_leave_request(self, from_number: str, message_body: str) -> Dict:
        teacher = self._find_teacher_by_phone(from_number)
        if not teacher:
            return {"message": "Teacher not found. Contact admin."}

        # naive parse: look for a date like 'Oct 15' or ISO date
        start_date, end_date = self._parse_dates_from_message(message_body)
        reason = message_body

        leave = {
            "teacher_id": teacher["id"],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "reason": reason,
            "status": "pending",
        }
        resp = self.db.insert("leaves", leave)
        leave_id = resp.data[0]["id"] if resp and resp.data else None

        substitutes = self._suggest_substitutes(teacher_id=teacher["id"], start_date=start_date, end_date=end_date)

        hod = self._find_hod_for_teacher(teacher)
        if hod:
            sub_str = ", ".join([f"{s['name']}" for s in substitutes]) or "None"
            msg = (
                f"Leave Request #{leave_id}: {teacher['name']}, {start_date.isoformat()} to {end_date.isoformat()}\n"
                f"Suggested substitutes: {sub_str}.\n"
                f"Reply: approve {leave_id} name1,name2 or reject {leave_id}"
            )
            self._notify(hod["phone"], msg)

        return {"message": f"Leave submitted with id {leave_id}. Await HOD approval."}

    async def _handle_approve(self, from_number: str, entity: Optional[str]) -> Dict:
        if not entity:
            return {"message": "Usage: approve <leave_id> <comma-separated-substitute-names>"}
        parts = entity.split(":")
        leave_id = int(parts[0])
        chosen = parts[1] if len(parts) > 1 else ""
        chosen_names = [s.strip() for s in chosen.split(",") if s.strip()]

        leave = self.db.select_one("leaves", ("id", leave_id))
        if not leave:
            return {"message": "Leave not found"}

        self.db.update("leaves", {"status": "approved"}, ("id", leave_id))

        # create substitutions rows for chosen teachers
        for name in chosen_names:
            sub_teacher = self._find_teacher_by_name(name)
            if sub_teacher:
                self.db.insert(
                    "substitutions",
                    {"leave_id": leave_id, "substitute_teacher_id": sub_teacher["id"], "status": "pending"},
                )
                self._notify(
                    sub_teacher["phone"],
                    f"You’ve been assigned for leave #{leave_id}. Reply 'confirm {leave_id}' to accept.",
                )

        teacher = self.db.select_one("teachers", ("id", leave["teacher_id"]))
        if teacher:
            self._notify(teacher["phone"], f"Your leave #{leave_id} is approved.")

        return {"message": f"Leave {leave_id} approved."}

    async def _handle_reject(self, from_number: str, entity: Optional[str]) -> Dict:
        if not entity:
            return {"message": "Usage: reject <leave_id>"}
        leave_id = int(entity)
        leave = self.db.select_one("leaves", ("id", leave_id))
        if not leave:
            return {"message": "Leave not found"}
        self.db.update("leaves", {"status": "rejected"}, ("id", leave_id))
        teacher = self.db.select_one("teachers", ("id", leave["teacher_id"]))
        if teacher:
            self._notify(teacher["phone"], f"Your leave #{leave_id} is rejected.")
        return {"message": f"Leave {leave_id} rejected."}

    async def _handle_confirm(self, from_number: str, entity: Optional[str]) -> Dict:
        if not entity:
            return {"message": "Usage: confirm <leave_id>"}
        leave_id = int(entity)
        teacher = self._find_teacher_by_phone(from_number)
        if not teacher:
            return {"message": "Teacher not found"}
        # find substitution row for this teacher & leave
        subs = self.db.select("substitutions", {"leave_id": leave_id, "substitute_teacher_id": teacher["id"]})
        if not subs:
            return {"message": "No pending substitution found for you."}
        sub_id = subs[0]["id"]
        self.db.update("substitutions", {"status": "confirmed"}, ("id", sub_id))
        return {"message": f"Confirmed substitution for leave #{leave_id}."}

    # Helpers
    def _find_teacher_by_phone(self, phone: str):
        result = self.db.table("teachers").select("*").eq("phone", phone).limit(1).execute()
        return (result.data or [None])[0]

    def _find_teacher_by_name(self, name: str):
        result = self.db.table("teachers").select("*").ilike("name", name).limit(1).execute()
        return (result.data or [None])[0]

    def _find_hod_for_teacher(self, teacher: Dict):
        # simple: first admin for now; later map per department
        result = self.db.table("admins").select("*").limit(1).execute()
        return (result.data or [None])[0]

    def _suggest_substitutes(self, teacher_id: int, start_date: date, end_date: date) -> List[Dict]:
        # naive: any teacher not equal to teacher_id
        teachers = self.db.table("teachers").select("*").neq("id", teacher_id).limit(5).execute()
        return teachers.data or []

    def _parse_dates_from_message(self, message: str):
        # naive: today or single-day if named month present; improve later with LLM
        try:
            import dateparser  # optional if installed

            dt = dateparser.parse(message)
            if dt:
                d = dt.date()
                return d, d
        except Exception:
            pass
        today = datetime.utcnow().date()
        return today, today

    def _notify(self, to_phone: str, message: str) -> None:
        try:
            sid = self.notifier.send_whatsapp(to_phone=to_phone, message=message)
            self.db.insert("notifications", {"target_phone": to_phone, "message": message, "twilio_sid": sid, "status": "sent"})
        except Exception:
            self.db.insert("notifications", {"target_phone": to_phone, "message": message, "twilio_sid": None, "status": "failed"})


