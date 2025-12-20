from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class ReportType(str, enum.Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    DETAILED_ISSUES = "detailed_issues"
    INTEGRATION_HEALTH = "integration_health"
    TREND_ANALYSIS = "trend_analysis"
    COMPLIANCE_AUDIT = "compliance_audit"


class ReportFormat(str, enum.Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    report_type = Column(Enum(ReportType), nullable=False)
    format = Column(Enum(ReportFormat), default=ReportFormat.PDF)

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)

    # Report configuration
    config = Column(JSON, default={})  # Filters, date ranges, etc.

    # Report content
    summary = Column(JSON)  # High-level summary data
    file_path = Column(String)  # Path to generated file
    file_size = Column(Integer)

    # Metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="reports")
