"""
Grade Record Model (PostgreSQL)
================================
Stores the computed quality grade for each fabric roll / inspection batch.

Fields:
  id, timestamp, production_line_id, roll_id, grade (A/B/C/D),
  total_defects, defect_density, yield_loss_pct, graded_by_ai,
  override_by_user_id, notes

TODO: Add index on (production_line_id, timestamp)
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func

from app.core.database import Base


class GradeRecord(Base):
    __tablename__ = "grade_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    production_line_id = Column(Integer, nullable=False)
    roll_id = Column(String(50), nullable=True)
    grade = Column(String(1), nullable=False)            # 'A', 'B', 'C', 'D'
    total_defects = Column(Integer, default=0)
    defect_density = Column(Float, default=0.0)          # defects per square meter
    yield_loss_pct = Column(Float, default=0.0)          # percentage yield lost
    graded_by_ai = Column(Boolean, default=True)
    override_by_user_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
