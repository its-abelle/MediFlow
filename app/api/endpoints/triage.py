from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import PatientDataRequest, TriageResponse
from app.api.deps import get_diagnostic_engine, get_blockchain_service
from app.services.diagnosis import PatientData
from app.utils.security import AIPredictionHasher
from uuid import uuid4
from datetime import datetime
import json
import os

router = APIRouter()

# Path to local audit store
AUDIT_STORE = "data/secure_audit_store.json"

def save_to_audit_store(record: dict):
    records = []
    if os.path.exists(AUDIT_STORE):
        with open(AUDIT_STORE, "r") as f:
            try:
                records = json.load(f)
            except:
                records = []
    
    records.append(record)
    with open(AUDIT_STORE, "w") as f:
        json.dump(records, f, indent=4)

@router.post("/", response_model=TriageResponse)
async def triage_patient(
    patient_data: PatientDataRequest,
    engine = Depends(get_diagnostic_engine),
    blockchain = Depends(get_blockchain_service)
):
    try:
        patient = PatientData(**patient_data.model_dump())
        ai_result, methodology = engine.diagnose(patient)
        
        prediction_id = str(uuid4())
        timestamp = datetime.now().isoformat()
        
        input_features = patient.to_dict()
        prediction_dict = {
            "prediction_id": prediction_id,
            "patient_id": patient.patient_id,
            "risk_level": ai_result.risk_level,
            "confidence": ai_result.confidence,
            "timestamp": timestamp,
            "input_features": input_features
        }
        ai_hash = AIPredictionHasher.create_prediction_hash(prediction_dict)
        
        # 1. RECORD ON BLOCKCHAIN (The Proof)
        tx_result = blockchain.record_ai_prediction(
            prediction_id=prediction_id,
            patient_id=patient.patient_id,
            prediction_hash=ai_hash
        )
        
        # 2. SAVE LOCALLY (The Data for Accountability)
        save_to_audit_store({
            "prediction_id": prediction_id,
            "patient_id": patient.patient_id,
            "ai_hash": ai_hash,
            "raw_data": prediction_dict,
            "ai_result": ai_result.to_dict(),
            "blockchain_tx": tx_result.get("transaction_hash")
        })
        
        status = "success" if tx_result.get("status") != "error" else "warning"
        
        return TriageResponse(
            status=status,
            patient_id=patient.patient_id,
            ai_prediction_id=prediction_id,
            risk_level=ai_result.risk_level,
            confidence=ai_result.confidence,
            methodology=methodology,
            reasoning=ai_result.reasoning,
            recommendation=ai_result.recommendation,
            ai_prediction_hash=ai_hash,
            timestamp=timestamp,
            blockchain_block=tx_result.get("block_number"),
            transaction_hash=tx_result.get("transaction_hash")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
