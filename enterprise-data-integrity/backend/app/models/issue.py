from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class IssueStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class IssueSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    severity = Column(Enum(IssueSeverity), nullable=False)
    status = Column(Enum(IssueStatus), default=IssueStatus.OPEN)

    # What rule detected this issue
    rule_name = Column(String, nullable=False)
    rule_category = Column(String)

    # Where the issue was found
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)

    # Details about the issue
    affected_records = Column(JSON, default=[])  # List of record IDs or data
    impact_description = Column(Text)

    # Recommendations
    recommendation = Column(Text)
    fix_priority = Column(Integer, default=0)  # Higher = more urgent

    # Resolution tracking
    resolved_at = Column(DateTime)
    resolved_by = Column(String)
    resolution_notes = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    run = relationship("Run", back_populates="issues")
