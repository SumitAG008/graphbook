"""
Health Monitor API - Module 3
Endpoints for integration health monitoring
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.health_monitor import HealthMonitor


router = APIRouter(prefix="/health-monitor", tags=["health-monitor"])


@router.get("/dashboard")
def get_health_dashboard(tenant_id: int = 1, db: Session = Depends(get_db)):
    """
    Get overall health dashboard

    Shows health status for all connectors, failure rates, and anomalies
    """
    monitor = HealthMonitor(db)
    return monitor.get_connector_health_dashboard(tenant_id)


@router.get("/connector/{connector_id}")
def get_connector_health(connector_id: int, db: Session = Depends(get_db)):
    """Get detailed health metrics for a specific connector"""
    monitor = HealthMonitor(db)
    return monitor.get_connector_health(connector_id)


@router.get("/incidents")
def get_failure_incidents(
    tenant_id: int = 1, limit: int = 10, db: Session = Depends(get_db)
):
    """Get recent failure incidents"""
    monitor = HealthMonitor(db)
    return monitor.get_failure_incidents(tenant_id, limit)


@router.get("/uptime/{connector_id}")
def get_connector_uptime(
    connector_id: int, days: int = 7, db: Session = Depends(get_db)
):
    """Calculate uptime percentage for a connector"""
    monitor = HealthMonitor(db)
    uptime = monitor.calculate_uptime(connector_id, days)
    return {"connector_id": connector_id, "uptime_percentage": uptime, "days": days}
