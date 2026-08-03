"""
Grading Engine Service
=======================
Core business logic for computing fabric quality grades.

Grading Rules (to be tuned with domain experts):
  Grade A: defect_density < 0.5 per m²  AND no critical defects
  Grade B: defect_density < 1.5 per m²  AND no critical defects
  Grade C: defect_density < 3.0 per m²  OR 1 critical defect
  Grade D: defect_density >= 3.0 per m² OR multiple critical defects

TODO:
  - Accept a list of DefectRecord objects and a fabric length in meters
  - Return a GradeRecord with computed grade, defect_density, yield_loss_pct
  - Expose as both a callable service and a FastAPI dependency
"""


class GradingEngine:
    """Placeholder — full implementation in Phase 3."""

    GRADE_THRESHOLDS = {
        'A': {'max_density': 0.5, 'allow_critical': False},
        'B': {'max_density': 1.5, 'allow_critical': False},
        'C': {'max_density': 3.0, 'allow_critical': True},
    }

    def compute_grade(self, defects: list, fabric_area_m2: float) -> dict:
        """Compute quality grade from a list of defect records."""
        raise NotImplementedError

    def compute_yield_loss(self, grade: str) -> float:
        """Estimate yield loss percentage based on grade."""
        raise NotImplementedError
