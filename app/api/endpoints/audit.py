from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AuditTrailResponse
from app.api.deps import get_blockchain_service

router = APIRouter()

@router.get("/{patient_id}", response_model=AuditTrailResponse)
async def get_audit_trail(
    patient_id: str,
    blockchain = Depends(get_blockchain_service)
):
    try:
        trail = blockchain.get_audit_trail(patient_id)
        
        # Format the response
        ai_predictions = len(trail)
        doctor_validations = sum(1 for item in trail if item.get("validation"))
        
        return AuditTrailResponse(
            patient_id=patient_id,
            total_transactions=ai_predictions + doctor_validations,
            ai_predictions=ai_predictions,
            doctor_validations=doctor_validations,
            transactions=trail
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
