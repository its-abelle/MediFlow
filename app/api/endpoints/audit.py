from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import AuditTrailResponse
from app.api.deps import get_blockchain_service
import json
import os

router = APIRouter()

AUDIT_STORE = "data/secure_audit_store.json"

@router.get("/{patient_id}")
async def get_audit_trail(
    patient_id: str,
    blockchain = Depends(get_blockchain_service)
):
    try:
        # 1. Fetch from Blockchain (The Proof)
        blockchain_trail = blockchain.get_audit_trail(patient_id)
        
        # 2. Fetch from Local Store (The Raw Data)
        local_records = []
        if os.path.exists(AUDIT_STORE):
            with open(AUDIT_STORE, "r") as f:
                all_records = json.load(f)
                local_records = [r for r in all_records if r['patient_id'] == patient_id]

        # 3. Merge Data
        transactions = []
        
        bc_map = {}
        for item in blockchain_trail:
            bc_map[item['prediction']['id']] = item

        for local in local_records:
            pid = local['prediction_id']
            bc_data = bc_map.get(pid)
            
            # Use local validation data if blockchain fetch is incomplete
            local_validation = local.get('validation')
            
            transactions.append({
                "prediction_id": pid,
                "timestamp": local['raw_data']['timestamp'],
                "ai_hash": local['ai_hash'],
                "risk_level": local['ai_result']['risk_level'],
                "raw_features": local['raw_data']['input_features'],
                "blockchain_verified": bc_data is not None,
                "validation": bc_data['validation'] if bc_data else local_validation
            })

        return {
            "patient_id": patient_id,
            "total_transactions": len(transactions),
            "transactions": transactions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
