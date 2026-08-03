"""
Reports Router
===============
Endpoints:
  GET  /reports/daily     — Aggregate daily defect + grade summary
  GET  /reports/export    — Export report as PDF or CSV
  GET  /reports/yield     — Yield loss calculation over date range

TODO: Implement endpoints, wire to ReportService + yield calculator
"""

from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/daily")
async def daily_report():
    """TODO: Daily aggregated report."""
    raise NotImplementedError


@router.get("/export")
async def export_report():
    """TODO: Export to PDF/CSV."""
    raise NotImplementedError
