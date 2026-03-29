from app.core.config import settings
from app.services.diagnosis import TBDiagnosticEngine
from app.services.blockchain import MediFlowBlockchain
from app.utils.security import DoctorSignatureValidator

# Singleton instances
diagnostic_engine = TBDiagnosticEngine(ml_model_path=settings.ML_MODEL_PATH)
blockchain_service = MediFlowBlockchain(
    provider_url=settings.BLOCKCHAIN_PROVIDER_URL,
    contract_address=settings.CONTRACT_ADDRESS,
    private_key=settings.PRIVATE_KEY
)
signature_validator = DoctorSignatureValidator()

def get_diagnostic_engine():
    return diagnostic_engine

def get_blockchain_service():
    return blockchain_service

def get_signature_validator():
    return signature_validator
