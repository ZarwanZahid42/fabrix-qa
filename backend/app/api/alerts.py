"""
Alerts Router
==============
Endpoints:
  GET  /alerts/          — List recent alerts (filterable by severity, line, date)
  POST /alerts/{id}/ack  — Acknowledge an alert
  POST /alerts/test      — Trigger a test alert (admin only)

TODO: Implement endpoints, integrate Twilio + email services
"""

from fastapi import APIRouter

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/")
async def list_alerts():
    """TODO: Return alert log."""
    raise NotImplementedError


@router.post("/{alert_id}/ack")
async def acknowledge_alert(alert_id: int):
    """TODO: Mark alert as acknowledged."""
    raise NotImplementedError
