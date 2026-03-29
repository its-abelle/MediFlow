# MediFlow TB Diagnostic & Accountability System

MediFlow is an AI-powered Tuberculosis (TB) diagnostic platform that leverages Machine Learning for triage and Blockchain for accountability and an immutable audit trail.

## 🚀 Project Overview

- **AI Triage:** Uses a hybrid engine (Rule-Based + Random Forest) to assess TB risk based on clinical symptoms.
- **Blockchain Accountability:** Records every AI prediction and doctor validation on an immutable ledger (Solidity/Ethereum).
- **Privacy First:** Only non-reversible hashes of patient data are stored on-chain, ensuring patient privacy while maintaining a complete audit trail.
- **Modular Architecture:** Cleanly separated into API, Services, and Blockchain layers.

## 📂 Project Structure

```text
ai-backend/
├── app/
│   ├── api/                 # FastAPI Endpoints
│   ├── core/                # Configuration
│   ├── models/              # Pydantic Schemas
│   ├── services/            # Business Logic (Diagnosis & Blockchain)
│   ├── utils/               # Hashing & Security
│   └── resources/           # ML Model weights
├── blockchain/              # Foundry (Solidity) project
│   ├── src/                 # Smart Contracts
│   └── forge build/         # Compiled artifacts
├── scripts/                 # Utility scripts (Data gen, Training)
├── tests/                   # Test suite
└── README.md
```

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+
- [Foundry](https://book.getfoundry.sh/getting-started/installation) (for Solidity)

### Backend Setup

1. Install dependencies:
   ```bash
   pip install fastapi uvicorn joblib pandas numpy web3 pydantic
   ```

2. Run the API:
   ```bash
   python -m app.main
   ```

### Blockchain Setup

1. Compile the contracts:
   ```bash
   cd blockchain
   forge build
   ```

2. (Optional) Deploy to a local node (Anvil):
   ```bash
   # In a separate terminal
   anvil
   
   # Deploy
   forge create --rpc-url http://localhost:8545 --private-key <YOUR_PRIVATE_KEY> src/MediFlow.sol:MediFlow
   ```

## 🧪 AI Engine

The hybrid diagnostic engine combines:
1. **Rule-Based Tier:** Implements WHO clinical guidelines for immediate red-flag detection (e.g., Hemoptysis).
2. **ML Tier:** A Random Forest model trained on synthetic/real TB data to identify complex symptom patterns.

## 🔒 Security & Accountability

Every diagnostic decision follows this flow:
1. AI generates a prediction.
2. A unique SHA256 hash of the prediction is created.
3. The hash and an anonymized patient ID hash are recorded on the blockchain.
4. A doctor reviews the case and signs their decision using an HMAC-based digital signature.
5. The doctor's validation is linked to the original AI prediction on-chain.
