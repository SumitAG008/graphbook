"""
Connectors API - Module 1
Endpoints for managing data connectors and uploads
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.connector_service import ConnectorService
from app.models.connector import Connector, ConnectorType, ConnectorStatus
from pydantic import BaseModel
from datetime import datetime


router = APIRouter(prefix="/connectors", tags=["connectors"])


class ConnectorCreate(BaseModel):
    name: str
    description: str = None
    type: ConnectorType
    config: dict = {}
    field_mapping: dict = {}


class ConnectorResponse(BaseModel):
    id: int
    name: str
    description: str = None
    type: ConnectorType
    status: ConnectorStatus
    created_at: datetime
    last_sync: datetime = None
    success_count: int
    failure_count: int

    class Config:
        from_attributes = True


@router.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    """
    Upload a CSV file for data quality assessment

    This is the first screen in the MVP - "Upload CSV"
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    connector_service = ConnectorService()

    # Read file content
    content = await file.read()

    # Process upload
    result = await connector_service.upload_csv(content, file.filename)

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("error"))

    return result


@router.post("/", response_model=ConnectorResponse)
def create_connector(
    connector: ConnectorCreate, tenant_id: int = 1, db: Session = Depends(get_db)
):
    """Create a new connector"""
    db_connector = Connector(
        name=connector.name,
        description=connector.description,
        type=connector.type,
        config=connector.config,
        field_mapping=connector.field_mapping,
        tenant_id=tenant_id,
    )
    db.add(db_connector)
    db.commit()
    db.refresh(db_connector)
    return db_connector


@router.get("/", response_model=List[ConnectorResponse])
def list_connectors(tenant_id: int = 1, db: Session = Depends(get_db)):
    """List all connectors for a tenant"""
    connectors = db.query(Connector).filter(Connector.tenant_id == tenant_id).all()
    return connectors


@router.get("/{connector_id}", response_model=ConnectorResponse)
def get_connector(connector_id: int, db: Session = Depends(get_db)):
    """Get a specific connector"""
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    return connector


@router.get("/{connector_id}/health")
def get_connector_health(connector_id: int, db: Session = Depends(get_db)):
    """Get health metrics for a connector"""
    connector = db.query(Connector).filter(Connector.id == connector_id).first()
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")

    connector_service = ConnectorService()
    health = connector_service.get_connector_health(connector_id, db)

    return health
