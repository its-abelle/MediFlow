from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class PatientDataRequest(BaseModel):
    """Patient data coming from frontend."""
    patient_id: str
    age: int
    fever_duration_days: int
    cough_duration_days: int
    weight_loss_kg: float
    night_sweats: int
    hemoptysis: int

class TriageResponse(BaseModel):
    """AI triage response."""
    status: str
    patient_id: str
    ai_prediction_id: str
    risk_level: str
    confidence: float
    methodology: str
    reasoning: str
    recommendation: str
    ai_prediction_hash: str
    timestamp: str
    blockchain_block: Optional[int] = None
    transaction_hash: Optional[str] = None

class DoctorApprovalRequest(BaseModel):
    """Doctor validation request."""
    doctor_id: str
    doctor_name: str
    ai_prediction_id: str
    ai_prediction_hash: str
    decision: str  # APPROVED, OVERRIDDEN, REQUIRES_FURTHER_TESTING
    override_reason: Optional[str] = None
    override_risk_level: Optional[str] = None

class AuditTrailResponse(BaseModel):
    """Audit trail response."""
    patient_id: str
    total_transactions: int
    ai_predictions: int
    doctor_validations: int
    transactions: List[Dict]
