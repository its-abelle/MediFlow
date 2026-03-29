import os
from typing import Dict, Optional
try:
    from pydantic_settings import BaseSettings
except ImportError:
    class BaseSettings:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

class Settings(BaseSettings):
    PROJECT_NAME: str = "MediFlow Intelligence API"
    VERSION: str = "2.0"
    DEBUG: bool = os.getenv("DEBUG", "True") == "True"
    
    # Paths
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ML_MODEL_PATH: str = os.getenv("ML_MODEL_PATH", os.path.join(BASE_DIR, "app/resources/models/rf_tb_model.pkl"))
    
    # Blockchain settings (Anvil Defaults)
    BLOCKCHAIN_PROVIDER_URL: str = os.getenv("BLOCKCHAIN_PROVIDER_URL", "http://127.0.0.1:8545")
    # This should be updated after deployment
    CONTRACT_ADDRESS: Optional[str] = os.getenv("CONTRACT_ADDRESS") 
    # Anvil's first default private key
    PRIVATE_KEY: str = os.getenv("PRIVATE_KEY", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80")
    
    # Doctor keys for HMAC signatures (Accountability Layer)
    DOCTOR_KEYS: Dict[str, str] = {
        'DOC001': os.getenv('DOC001_KEY', 'secret_key_doctor_amina_2024'),
        'DOC002': os.getenv('DOC002_KEY', 'secret_key_doctor_james_2024'),
        'DOC003': os.getenv('DOC003_KEY', 'secret_key_doctor_okonkwo_2024')
    }

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
