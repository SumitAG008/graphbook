"""
Rules API - Module 2
Endpoints for managing data quality rules
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.rules_engine import DataQualityEngine
from app.models.rule import Rule, RuleCategory, RuleSeverity
from pydantic import BaseModel
from datetime import datetime


router = APIRouter(prefix="/rules", tags=["rules"])


class RuleResponse(BaseModel):
    id: int
    name: str
    description: str = None
    category: RuleCategory
    severity: RuleSeverity
    is_builtin: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AvailableRuleResponse(BaseModel):
    id: str
    name: str
    description: str
    severity: str


@router.get("/available", response_model=List[AvailableRuleResponse])
def get_available_rules():
    """
    Get list of available built-in rules

    This is shown on the second screen in the MVP - "Define Rules" (checkbox list)
    """
    engine = DataQualityEngine()
    return engine.get_available_rules()


@router.get("/", response_model=List[RuleResponse])
def list_rules(tenant_id: int = 1, db: Session = Depends(get_db)):
    """List all rules for a tenant"""
    rules = db.query(Rule).filter(Rule.tenant_id == tenant_id).all()
    return rules


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: int, db: Session = Depends(get_db)):
    """Get a specific rule"""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule
