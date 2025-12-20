from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, JSON, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
import enum


class RuleCategory(str, enum.Enum):
    DATA_QUALITY = "data_quality"
    INTEGRATION_HEALTH = "integration_health"
    COMPLIANCE = "compliance"
    PERFORMANCE = "performance"
    CUSTOM = "custom"


class RuleSeverity(str, enum.Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Rule(Base):
    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    category = Column(Enum(RuleCategory), nullable=False)
    severity = Column(Enum(RuleSeverity), default=RuleSeverity.MEDIUM)

    # Rule definition (Python expression, SQL query, or custom logic)
    rule_definition = Column(JSON, nullable=False)

    # Whether this is a built-in rule or custom
    is_builtin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    tenant = relationship("Tenant", back_populates="rules")
    executions = relationship("RuleExecution", back_populates="rule", cascade="all, delete-orphan")


class RuleExecution(Base):
    __tablename__ = "rule_executions"

    id = Column(Integer, primary_key=True, index=True)
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False)
    run_id = Column(Integer, ForeignKey("runs.id"), nullable=False)

    passed = Column(Boolean, default=False)
    issues_found = Column(Integer, default=0)
    execution_time_ms = Column(Integer)

    result = Column(JSON)  # Detailed results
    error_message = Column(Text)

    executed_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    rule = relationship("Rule", back_populates="executions")
    run = relationship("Run", back_populates="rule_executions")
