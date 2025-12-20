from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class RunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RunType(str, enum.Enum):
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    TRIGGERED = "triggered"


class Run(Base):
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    run_type = Column(Enum(RunType), default=RunType.MANUAL)
    status = Column(Enum(RunStatus), default=RunStatus.PENDING)

    connector_id = Column(Integer, ForeignKey("connectors.id"), nullable=False)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    # Execution details
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Integer)

    # Results summary
    total_records = Column(Integer, default=0)
    total_issues = Column(Integer, default=0)
    rules_passed = Column(Integer, default=0)
    rules_failed = Column(Integer, default=0)

    # Metadata
    config = Column(JSON, default={})  # Run-specific configuration
    metadata = Column(JSON, default={})  # Additional metadata
    error_message = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="runs")
    connector = relationship("Connector", back_populates="runs")
    issues = relationship("Issue", back_populates="run", cascade="all, delete-orphan")
    rule_executions = relationship("RuleExecution", back_populates="run", cascade="all, delete-orphan")
