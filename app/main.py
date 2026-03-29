import logging
import os
import pandas as pd
import random
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from app.api.endpoints import triage, audit, validate
from app.api.deps import get_blockchain_service, get_signature_validator
from app.core.config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("mediflow")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-ready TB Diagnostic System with Blockchain Ledger"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred.", "details": str(exc) if settings.DEBUG else None}
    )

# Include routers
app.include_router(triage.router, prefix="/api/v1/triage", tags=["Triage"])
app.include_router(validate.router, prefix="/api/v1/validate", tags=["Validation"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])

@app.get("/")
async def serve_frontend():
    return FileResponse("frontend/index.html")

@app.get("/api/v1/doctors")
async def get_doctors(validator = Depends(get_signature_validator)):
    return [{"id": d['id'], "name": d['name']} for d in validator.doctor_registry.values()]

@app.get("/api/v1/patients/random")
async def get_random_patient():
    data_path = "data/tb_patients_data.csv"
    if not os.path.exists(data_path):
        return {"error": "Dataset not found. Run training script first."}
    
    df = pd.read_csv(data_path)
    random_row = df.sample(n=1).iloc[0]
    
    return {
        "patient_id": f"PT-{random.randint(1000, 9999)}",
        "age": int(random_row['age']),
        "fever_duration_days": int(random_row['fever_duration_days']),
        "cough_duration_days": int(random_row['cough_duration_days']),
        "weight_loss_kg": float(random_row['weight_loss_kg']),
        "night_sweats": int(random_row['night_sweats']),
        "hemoptysis": int(random_row['hemoptysis'])
    }

@app.get("/health")
async def health_check(blockchain = Depends(get_blockchain_service)):
    return {
        "status": "healthy",
        "blockchain_connected": blockchain.is_connected,
        "provider": settings.BLOCKCHAIN_PROVIDER_URL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
