from __future__ import annotations

from typing import Optional

from twilio.rest import Client as TwilioClient

from app.config import Settings, get_settings


class Notifier:
    def __init__(self, settings: Optional[Settings] = None) -> None:
        self.settings = settings or get_settings()
        self.client = TwilioClient(self.settings.twilio_account_sid, self.settings.twilio_auth_token)

    def send_whatsapp(self, to_phone: str, message: str) -> str:
        from_phone = self.settings.twilio_whatsapp_from
        resp = self.client.messages.create(from_=from_phone, to=to_phone, body=message)
        return resp.sid


