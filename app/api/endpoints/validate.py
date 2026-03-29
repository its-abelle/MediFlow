from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import DoctorApprovalRequest
from app.api.deps import get_blockchain_service, get_signature_validator
from datetime import datetime
import json
import os

router = APIRouter()

AUDIT_STORE = "data/secure_audit_store.json"

def update_audit_with_validation(prediction_id: str, validation_data: dict):
    if os.path.exists(AUDIT_STORE):
        with open(AUDIT_STORE, "r") as f:
            records = json.load(f)
        
        for record in records:
            if record['prediction_id'] == prediction_id:
                record['validation'] = validation_data
                break
        
        with open(AUDIT_STORE, "w") as f:
            json.dump(records, f, indent=4)

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
            validation_id=approval_data.ai_prediction_id + "_val",
            prediction_id=approval_data.ai_prediction_id,
            doctor_id=approval_data.doctor_id,
            decision=approval_data.decision,
            signature=doctor_signature
        )
        
        # 3. Update local audit store for full accountability data
        validation_info = {
            "doctor_id": approval_data.doctor_id,
            "doctor_name": signature_validator.get_doctor_name(approval_data.doctor_id),
            "decision": approval_data.decision,
            "override_reason": approval_data.override_reason,
            "signature": doctor_signature,
            "timestamp": datetime.now().isoformat(),
            "blockchain_tx": tx_result.get("transaction_hash")
        }
        update_audit_with_validation(approval_data.ai_prediction_id, validation_info)
        
        return {
            "status": "success",
            "doctor_id": approval_data.doctor_id,
            "decision": approval_data.decision,
            "override_reason": approval_data.override_reason,
            "signature": doctor_signature,
            "blockchain_tx": tx_result.get("transaction_hash"),
            "timestamp": validation_info["timestamp"]
        }
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
