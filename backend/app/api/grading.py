"""
Grading Router
===============
Endpoints:
  GET  /grading/latest      — Latest quality grade for each active line
  GET  /grading/history     — Paginated grade history with filters
  POST /grading/manual      — Manually submit a grade override (Manager role)

TODO: Implement endpoints, wire to GradingService
"""

from fastapi import APIRouter

router = APIRouter(prefix="/grading", tags=["Grading"])


@router.get("/latest")
async def get_latest_grade():
    """TODO: Return latest grade per production line."""
    raise NotImplementedError


@router.get("/history")
async def get_grade_history():
    """TODO: Paginated grade history."""
    raise NotImplementedError
