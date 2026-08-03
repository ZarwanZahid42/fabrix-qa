"""
Grading Pydantic Schemas
=========================
TODO: Add GradeFilter, GradeHistoryResponse schemas
"""

from pydantic import BaseModel
from datetime import datetime


class GradeRecordRead(BaseModel):
    id: int
    timestamp: datetime
    production_line_id: int
    roll_id: str | None
    grade: str
    total_defects: int
    defect_density: float
    yield_loss_pct: float
    graded_by_ai: bool

    model_config = {"from_attributes": True}
