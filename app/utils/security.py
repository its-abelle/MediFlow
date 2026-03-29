import hashlib
import hmac
import json
import os
from datetime import datetime
from typing import Dict, Optional, List

class AIPredictionHasher:
    @staticmethod
    def create_prediction_hash(prediction_dict: Dict) -> str:
        prediction_json = json.dumps(prediction_dict, sort_keys=True)
        return hashlib.sha256(prediction_json.encode()).hexdigest()

class DoctorSignatureValidator:
    def __init__(self, doctors_file: str = "data/doctors.json"):
        self.doctors_file = doctors_file
        self._load_doctors()

    def _load_doctors(self):
        if os.path.exists(self.doctors_file):
            with open(self.doctors_file, "r") as f:
                doctors_list = json.load(f)
                self.doctor_registry = {d['id']: d for d in doctors_list}
        else:
            self.doctor_registry = {}

    def get_doctor_name(self, doctor_id: str) -> str:
        self._load_doctors() # Refresh
        return self.doctor_registry.get(doctor_id, {}).get("name", "Unknown Doctor")

    def create_validation_signature(
        self,
        doctor_id: str,
        ai_prediction_hash: str,
        decision: str,
        override_reason: Optional[str] = None
    ) -> str:
        self._load_doctors() # Ensure we have latest keys
        if doctor_id not in self.doctor_registry:
            raise ValueError(f"Doctor {doctor_id} is not registered in the system.")
        
        doctor_key = self.doctor_registry[doctor_id]['key']
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
