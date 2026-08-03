"""
Notification Service
=====================
Handles sending SMS alerts via Twilio and email alerts via FastAPI-Mail.

TODO:
  - Implement send_sms(to: str, message: str) using Twilio REST client
  - Implement send_email(to: str, subject: str, body: str) using FastAPI-Mail
  - Add alert_on_grade(grade: str, line_id: int) trigger logic
  - Respect per-user notification preferences stored in DB
"""


class NotificationService:
    """Placeholder — full implementation in Phase 4."""

    async def send_sms(self, to: str, message: str) -> bool:
        raise NotImplementedError

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        raise NotImplementedError
