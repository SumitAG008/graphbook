"""
Integration Health Monitor - Module 3
Service for monitoring integration health and detecting anomalies
"""
from typing import Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.run import Run, RunStatus
from app.models.connector import Connector


class HealthMonitor:
    """Service for monitoring integration health"""

    def __init__(self, db: Session):
        self.db = db

    def get_connector_health_dashboard(self, tenant_id: int) -> Dict[str, Any]:
        """
        Get overall health dashboard for all connectors

        Returns health metrics, failure rates, and recent issues
        """
        connectors = (
            self.db.query(Connector).filter(Connector.tenant_id == tenant_id).all()
        )

        dashboard = {
            "overall_status": "healthy",
            "total_connectors": len(connectors),
            "healthy_connectors": 0,
            "warning_connectors": 0,
            "critical_connectors": 0,
            "connectors": [],
        }

        for connector in connectors:
            health = self.get_connector_health(connector.id)
            dashboard["connectors"].append(health)

            if health["status"] == "healthy":
                dashboard["healthy_connectors"] += 1
            elif health["status"] == "warning":
                dashboard["warning_connectors"] += 1
            else:
                dashboard["critical_connectors"] += 1

        # Set overall status
        if dashboard["critical_connectors"] > 0:
            dashboard["overall_status"] = "critical"
        elif dashboard["warning_connectors"] > 0:
            dashboard["overall_status"] = "warning"

        return dashboard

    def get_connector_health(self, connector_id: int) -> Dict[str, Any]:
        """
        Get health metrics for a specific connector

        Calculates:
        - Success rate (last 24 hours)
        - Average duration
        - Last successful run
        - Failure count
        - Anomaly detection
        """
        connector = (
            self.db.query(Connector).filter(Connector.id == connector_id).first()
        )

        if not connector:
            return {"error": "Connector not found"}

        # Get runs from last 24 hours
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_runs = (
            self.db.query(Run)
            .filter(Run.connector_id == connector_id, Run.started_at >= cutoff)
            .order_by(Run.started_at.desc())
            .all()
        )

        total_runs = len(recent_runs)
        successful_runs = [r for r in recent_runs if r.status == RunStatus.COMPLETED]
        failed_runs = [r for r in recent_runs if r.status == RunStatus.FAILED]

        success_rate = (
            (len(successful_runs) / total_runs * 100) if total_runs > 0 else 0
        )

        # Calculate average duration
        completed_runs = [r for r in recent_runs if r.duration_seconds is not None]
        avg_duration = (
            sum(r.duration_seconds for r in completed_runs) / len(completed_runs)
            if completed_runs
            else 0
        )

        # Get last successful run
        last_success = successful_runs[0] if successful_runs else None

        # Determine health status
        status = "healthy"
        if success_rate < 50:
            status = "critical"
        elif success_rate < 80:
            status = "warning"

        # Check for anomalies
        anomalies = self.detect_anomalies(connector_id, recent_runs)

        return {
            "connector_id": connector_id,
            "connector_name": connector.name,
            "status": status,
            "success_rate": round(success_rate, 2),
            "total_runs_24h": total_runs,
            "successful_runs": len(successful_runs),
            "failed_runs": len(failed_runs),
            "avg_duration_seconds": round(avg_duration, 2),
            "last_success": last_success.completed_at.isoformat()
            if last_success
            else None,
            "anomalies": anomalies,
        }

    def detect_anomalies(
        self, connector_id: int, recent_runs: List[Run]
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies in integration runs

        Checks for:
        - Sudden spikes in issues
        - Sudden drops in record count
        - Unusual duration times
        """
        anomalies = []

        if len(recent_runs) < 2:
            return anomalies

        completed_runs = [r for r in recent_runs if r.status == RunStatus.COMPLETED]

        if len(completed_runs) < 2:
            return anomalies

        # Check for spike in issues
        avg_issues = sum(r.total_issues for r in completed_runs) / len(completed_runs)
        latest_issues = completed_runs[0].total_issues

        if latest_issues > avg_issues * 2 and avg_issues > 0:
            anomalies.append(
                {
                    "type": "issue_spike",
                    "severity": "high",
                    "description": f"Issue count ({latest_issues}) is 2x higher than average ({avg_issues:.0f})",
                    "detected_at": datetime.utcnow().isoformat(),
                }
            )

        # Check for drop in record count
        avg_records = sum(r.total_records for r in completed_runs) / len(
            completed_runs
        )
        latest_records = completed_runs[0].total_records

        if latest_records < avg_records * 0.5 and avg_records > 0:
            anomalies.append(
                {
                    "type": "record_drop",
                    "severity": "medium",
                    "description": f"Record count ({latest_records}) is 50% lower than average ({avg_records:.0f})",
                    "detected_at": datetime.utcnow().isoformat(),
                }
            )

        # Check for unusual duration
        durations = [
            r.duration_seconds for r in completed_runs if r.duration_seconds
        ]
        if durations and len(durations) >= 2:
            avg_duration = sum(durations) / len(durations)
            latest_duration = durations[0]

            if latest_duration > avg_duration * 2 and avg_duration > 0:
                anomalies.append(
                    {
                        "type": "slow_execution",
                        "severity": "low",
                        "description": f"Execution time ({latest_duration}s) is 2x slower than average ({avg_duration:.0f}s)",
                        "detected_at": datetime.utcnow().isoformat(),
                    }
                )

        return anomalies

    def get_failure_incidents(
        self, tenant_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get recent failure incidents across all connectors"""
        failed_runs = (
            self.db.query(Run)
            .filter(Run.tenant_id == tenant_id, Run.status == RunStatus.FAILED)
            .order_by(Run.started_at.desc())
            .limit(limit)
            .all()
        )

        incidents = []
        for run in failed_runs:
            connector = (
                self.db.query(Connector).filter(Connector.id == run.connector_id).first()
            )

            incidents.append(
                {
                    "run_id": run.id,
                    "connector_name": connector.name if connector else "Unknown",
                    "failed_at": run.started_at.isoformat(),
                    "error_message": run.error_message or "Unknown error",
                    "duration_seconds": run.duration_seconds,
                }
            )

        return incidents

    def calculate_uptime(self, connector_id: int, days: int = 7) -> float:
        """Calculate uptime percentage for the last N days"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        runs = (
            self.db.query(Run)
            .filter(Run.connector_id == connector_id, Run.started_at >= cutoff)
            .all()
        )

        if not runs:
            return 100.0

        successful = len([r for r in runs if r.status == RunStatus.COMPLETED])
        return (successful / len(runs)) * 100
