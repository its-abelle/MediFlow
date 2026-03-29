import hashlib
import hmac
import json
from datetime import datetime
from typing import Dict, Optional

class AIPredictionHasher:
    @staticmethod
    def create_prediction_hash(prediction_dict: Dict) -> str:
        """Create SHA256 hash of AI prediction dictionary."""
        prediction_json = json.dumps(prediction_dict, sort_keys=True)
        return hashlib.sha256(prediction_json.encode()).hexdigest()

class DoctorSignatureValidator:
    def __init__(self, doctor_private_keys: Dict[str, str]):
        self.doctor_keys = doctor_private_keys
    
    def create_validation_signature(
        self,
        doctor_id: str,
        ai_prediction_hash: str,
        decision: str,
        override_reason: Optional[str] = None
    ) -> str:
        if doctor_id not in self.doctor_keys:
            raise ValueError(f"Doctor {doctor_id} not found")
        
        doctor_key = self.doctor_keys[doctor_id]
        data_to_sign = {
            'ai_prediction_hash': ai_prediction_hash,
            'doctor_id': doctor_id,
            'decision': decision,
            'override_reason': override_reason,
            'timestamp': datetime.now().isoformat()
        }
        
        data_json = json.dumps(data_to_sign, sort_keys=True)
        return hmac.new(
            doctor_key.encode(),
            data_json.encode(),
            hashlib.sha256
        ).hexdigest()
