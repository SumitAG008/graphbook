from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class AlertType(str, enum.Enum):
    INTEGRATION_FAILURE = "integration_failure"
    DATA_QUALITY = "data_quality"
    THRESHOLD_EXCEEDED = "threshold_exceeded"
    ANOMALY = "anomaly"
    SYSTEM = "system"


class AlertChannel(str, enum.Enum):
    EMAIL = "email"
    TEAMS = "teams"
    SLACK = "slack"
    WEBHOOK = "webhook"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)

    # Alert configuration
    condition = Column(JSON, nullable=False)  # Trigger conditions
    channels = Column(JSON, default=[])  # List of channels to notify

    is_active = Column(Boolean, default=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    # Notification settings
    throttle_minutes = Column(Integer, default=60)  # Don't spam
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="alerts")
