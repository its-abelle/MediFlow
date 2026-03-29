from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import DoctorApprovalRequest
from app.api.deps import get_blockchain_service, get_signature_validator
from datetime import datetime

router = APIRouter()

@router.post("/")
async def validate_ai_prediction(
    approval_data: DoctorApprovalRequest,
    blockchain = Depends(get_blockchain_service),
    signature_validator = Depends(get_signature_validator)
):
    try:
        # 1. Create digital signature
        doctor_signature = signature_validator.create_validation_signature(
            doctor_id=approval_data.doctor_id,
            ai_prediction_hash=approval_data.ai_prediction_hash,
            decision=approval_data.decision,
            override_reason=approval_data.override_reason
        )
        
        # 2. Record on blockchain
        tx_result = blockchain.record_doctor_validation(
            validation_id=approval_data.ai_prediction_id + "_val", # Simplified
            prediction_id=approval_data.ai_prediction_id,
            doctor_id=approval_data.doctor_id,
            decision=approval_data.decision,
            signature=doctor_signature
        )
        
        return {
            "status": "success",
            "doctor_id": approval_data.doctor_id,
            "decision": approval_data.decision,
            "signature": doctor_signature,
            "blockchain_tx": tx_result.get("transaction_hash"),
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
