from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class ConnectorType(str, enum.Enum):
    CSV = "csv"
    API = "api"
    SUCCESSFACTORS = "successfactors"
    WORKDAY = "workday"
    SAP = "sap"
    DATABASE = "database"
    SFTP = "sftp"


class ConnectorStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    TESTING = "testing"


class Connector(Base):
    __tablename__ = "connectors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String)
    type = Column(Enum(ConnectorType), nullable=False)
    status = Column(Enum(ConnectorStatus), default=ConnectorStatus.TESTING)

    # Configuration (credentials, endpoints, etc.)
    config = Column(JSON, default={})

    # Field mapping configuration
    field_mapping = Column(JSON, default={})

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_sync = Column(DateTime)

    # Health metrics
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_duration_seconds = Column(Integer, default=0)

    # Relationships
    tenant = relationship("Tenant", back_populates="connectors")
    runs = relationship("Run", back_populates="connector", cascade="all, delete-orphan")
