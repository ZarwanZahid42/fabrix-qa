"""
Alert Pydantic Schemas
=======================
TODO: Add AlertCreate, AlertFilter schemas
"""

from pydantic import BaseModel
from datetime import datetime


class AlertRead(BaseModel):
    id: int
    timestamp: datetime
    severity: str
    message: str
    acknowledged: bool

    model_config = {"from_attributes": True}
