"""
Reports API - Module 4
Endpoints for generating reports
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.report_service import ReportService
from app.models.run import Run
from app.models.issue import Issue
from app.models.connector import Connector
from pydantic import BaseModel
from datetime import datetime
import os


router = APIRouter(prefix="/reports", tags=["reports"])


class ReportGenerateRequest(BaseModel):
    run_id: int
    report_type: str = "executive_summary"
    format: str = "pdf"


@router.post("/generate")
def generate_report(
    request: ReportGenerateRequest, db: Session = Depends(get_db)
):
    """
    Generate executive PDF report for a run

    This is part of the fourth screen - "Executive PDF report"
    """
    # Get run data
    run = db.query(Run).filter(Run.id == request.run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    # Get connector name
    connector = db.query(Connector).filter(Connector.id == run.connector_id).first()
    connector_name = connector.name if connector else "Unknown"

    # Get issues
    issues = db.query(Issue).filter(Issue.run_id == request.run_id).all()

    # Prepare run data
    run_data = {
        "total_records": run.total_records,
        "total_issues": run.total_issues,
        "rules_executed": run.rules_passed + run.rules_failed,
        "rules_passed": run.rules_passed,
        "rules_failed": run.rules_failed,
    }

    # Convert issues to dict
    issues_data = [
        {
            "title": issue.title,
            "description": issue.description,
            "severity": issue.severity.value,
            "rule_name": issue.rule_name,
        }
        for issue in issues
    ]

    # Generate report
    report_service = ReportService()

    if request.format == "pdf":
        filepath = report_service.generate_executive_summary_pdf(
            run_data, issues_data, connector_name
        )

        if not os.path.exists(filepath):
            raise HTTPException(status_code=500, detail="Failed to generate report")

        return {
            "success": True,
            "file_path": filepath,
            "filename": os.path.basename(filepath),
            "download_url": f"/api/v1/reports/download/{os.path.basename(filepath)}",
        }
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


@router.get("/download/{filename}")
def download_report(filename: str):
    """Download a generated report"""
    report_service = ReportService()
    filepath = os.path.join(report_service.output_dir, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(
        path=filepath,
        media_type="application/pdf",
        filename=filename,
    )


@router.get("/trends")
def get_trends(tenant_id: int = 1, days: int = 30, db: Session = Depends(get_db)):
    """Get trend analysis for the past N days"""
    runs = (
        db.query(Run)
        .filter(Run.tenant_id == tenant_id)
        .order_by(Run.created_at.desc())
        .all()
    )

    # Convert to list of dicts
    historical_runs = [
        {
            "created_at": run.created_at.isoformat(),
            "total_issues": run.total_issues,
            "total_records": run.total_records,
        }
        for run in runs
    ]

    report_service = ReportService()
    trends = report_service.generate_trend_analysis(historical_runs, days)

    return trends
