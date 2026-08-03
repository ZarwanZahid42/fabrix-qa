"""
Defect Record Model (PostgreSQL)
=================================
Stores each detected defect event — links to MongoDB for image/heatmap metadata.

Fields:
  id, timestamp, production_line_id, defect_type, severity,
  grade_impact, mongo_ref_id, acknowledged_by, acknowledged_at

TODO: Add ForeignKey to ProductionLine model once created
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func

from app.core.database import Base


class DefectRecord(Base):
    __tablename__ = "defect_records"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    production_line_id = Column(Integer, nullable=False, index=True)
    defect_type = Column(String(100), nullable=False)  # e.g. "hole", "stain", "weave_error"
    severity = Column(String(20), nullable=False)       # "low", "medium", "high", "critical"
    grade_impact = Column(Float, default=0.0)           # penalty points applied to grade
    mongo_ref_id = Column(String(24), nullable=True)    # MongoDB ObjectId of image metadata
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(Integer, nullable=True)    # FK to User.id (resolved at query time)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
