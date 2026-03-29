from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import PatientDataRequest, TriageResponse
from app.api.deps import get_diagnostic_engine, get_blockchain_service
from app.services.diagnosis import PatientData
from app.utils.security import AIPredictionHasher
from uuid import uuid4
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=TriageResponse)
async def triage_patient(
    patient_data: PatientDataRequest,
    engine = Depends(get_diagnostic_engine),
    blockchain = Depends(get_blockchain_service)
):
    try:
        # Map request to domain model
        patient = PatientData(**patient_data.model_dump())
        
        # Run diagnosis
        ai_result, methodology = engine.diagnose(patient)
        
        # Create prediction metadata
        prediction_id = str(uuid4())
        timestamp = datetime.now().isoformat()
        
        # Compute hash
        prediction_dict = {
            "prediction_id": prediction_id,
            "patient_id": patient.patient_id,
            "risk_level": ai_result.risk_level,
            "confidence": ai_result.confidence,
            "timestamp": timestamp,
            "input_features": patient.to_dict()
        }
        ai_hash = AIPredictionHasher.create_prediction_hash(prediction_dict)
        
        # Record on blockchain
        tx_result = blockchain.record_ai_prediction(
            prediction_id=prediction_id,
            patient_id=patient.patient_id,
            prediction_hash=ai_hash
        )
        
        return TriageResponse(
            status="success",
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
