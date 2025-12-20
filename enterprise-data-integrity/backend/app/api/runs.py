"""
Runs API - Module 2 & 3
Endpoints for executing data quality checks and viewing run history
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.connector_service import ConnectorService
from app.services.rules_engine import DataQualityEngine
from app.models.run import Run, RunStatus, RunType
from app.models.issue import Issue, IssueSeverity, IssueStatus
from app.models.connector import Connector
from pydantic import BaseModel
from datetime import datetime


router = APIRouter(prefix="/runs", tags=["runs"])


class RunCreate(BaseModel):
    connector_id: int
    file_path: str
    rule_ids: List[str] = None
    run_type: RunType = RunType.MANUAL


class RunResponse(BaseModel):
    id: int
    name: str = None
    run_type: RunType
    status: RunStatus
    connector_id: int
    started_at: datetime
    completed_at: datetime = None
    duration_seconds: int = None
    total_records: int
    total_issues: int
    rules_passed: int
    rules_failed: int

    class Config:
        from_attributes = True


class IssueResponse(BaseModel):
    id: int
    title: str
    description: str = None
    severity: IssueSeverity
    status: IssueStatus
    rule_name: str
    rule_category: str = None
    impact_description: str = None
    recommendation: str = None
    created_at: datetime

    class Config:
        from_attributes = True


def execute_data_quality_check(run_id: int, file_path: str, rule_ids: List[str], db: Session):
    """Background task to execute data quality checks"""
    try:
        # Load the run
        run = db.query(Run).filter(Run.id == run_id).first()
        if not run:
            return

        # Update status to running
        run.status = RunStatus.RUNNING
        db.commit()

        # Load data
        connector_service = ConnectorService()
        df = connector_service.load_csv(file_path)

        # Execute rules
        engine = DataQualityEngine()
        results = engine.execute_rules(df, rule_ids)

        # Update run with results
        run.status = RunStatus.COMPLETED
        run.completed_at = datetime.utcnow()
        run.duration_seconds = int(
            (run.completed_at - run.started_at).total_seconds()
        )
        run.total_records = results["total_records"]
        run.total_issues = results["total_issues"]
        run.rules_passed = results["rules_passed"]
        run.rules_failed = results["rules_failed"]

        # Create issue records for each failed rule
        for detail in results["execution_details"]:
            if not detail.get("passed", True) and detail.get("issues"):
                # Create issue for this rule failure
                severity_map = {
                    "critical": IssueSeverity.CRITICAL,
                    "high": IssueSeverity.HIGH,
                    "medium": IssueSeverity.MEDIUM,
                    "low": IssueSeverity.LOW,
                    "info": IssueSeverity.INFO,
                }

                issue = Issue(
                    title=f"{detail['rule_name']} - {detail['message']}",
                    description=detail.get("message", ""),
                    severity=severity_map.get(
                        detail.get("severity", "medium"), IssueSeverity.MEDIUM
                    ),
                    status=IssueStatus.OPEN,
                    rule_name=detail["rule_name"],
                    rule_category=detail.get("category", "data_quality"),
                    run_id=run.id,
                    affected_records=detail.get("issues", []),
                    impact_description=f"Found {detail['issues_found']} affected records",
                    recommendation=_generate_recommendation(detail["rule_id"]),
                    fix_priority=_calculate_priority(detail.get("severity", "medium")),
                )
                db.add(issue)

        db.commit()

    except Exception as e:
        run.status = RunStatus.FAILED
        run.error_message = str(e)
        run.completed_at = datetime.utcnow()
        db.commit()


def _generate_recommendation(rule_id: str) -> str:
    """Generate recommendation based on rule type"""
    recommendations = {
        "duplicate_employees": "Review and merge duplicate employee records. Implement unique constraint validation in source system.",
        "missing_mandatory_fields": "Implement required field validation at data entry point. Add data completeness checks before integration.",
        "invalid_emails": "Validate email format at user registration. Update invalid emails through self-service portal.",
        "manager_hierarchy_loops": "Audit organizational hierarchy. Implement hierarchy validation in HR system to prevent circular references.",
        "invalid_country_codes": "Use standardized ISO country code dropdown in source system. Validate against ISO 3166-1 alpha-2 codes.",
    }
    return recommendations.get(
        rule_id, "Review and correct data in source system. Implement validation rules."
    )


def _calculate_priority(severity: str) -> int:
    """Calculate fix priority from severity"""
    priority_map = {"critical": 100, "high": 75, "medium": 50, "low": 25, "info": 10}
    return priority_map.get(severity, 50)


@router.post("/", response_model=RunResponse)
def create_run(
    run_data: RunCreate,
    background_tasks: BackgroundTasks,
    tenant_id: int = 1,
    db: Session = Depends(get_db),
):
    """
    Create and execute a data quality run

    This is the third screen in the MVP - "Run + Issues Table"
    """
    # Validate connector exists
    connector = (
        db.query(Connector).filter(Connector.id == run_data.connector_id).first()
    )
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    # Create run record
    run = Run(
        name=f"Data Quality Check - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
        run_type=run_data.run_type,
        status=RunStatus.PENDING,
        connector_id=run_data.connector_id,
        tenant_id=tenant_id,
        config={"file_path": run_data.file_path, "rule_ids": run_data.rule_ids},
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    # Execute in background
    background_tasks.add_task(
        execute_data_quality_check, run.id, run_data.file_path, run_data.rule_ids, db
    )

    return run


@router.get("/", response_model=List[RunResponse])
def list_runs(
    tenant_id: int = 1, limit: int = 50, db: Session = Depends(get_db)
):
    """List recent runs for a tenant"""
    runs = (
        db.query(Run)
        .filter(Run.tenant_id == tenant_id)
        .order_by(Run.created_at.desc())
        .limit(limit)
        .all()
    )
    return runs


@router.get("/{run_id}", response_model=RunResponse)
def get_run(run_id: int, db: Session = Depends(get_db)):
    """Get a specific run"""
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.get("/{run_id}/issues", response_model=List[IssueResponse])
def get_run_issues(run_id: int, db: Session = Depends(get_db)):
    """
    Get all issues for a specific run

    This powers the "Issues Table" on the third screen
    """
    run = db.query(Run).filter(Run.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")

    issues = db.query(Issue).filter(Issue.run_id == run_id).all()
    return issues
