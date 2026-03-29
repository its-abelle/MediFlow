import json
import sys
from web3 import Web3
import hashlib

# Configuration - Replace with your Sepolia/Anvil details
RPC_URL = "http://127.0.0.1:8545" 
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

def verify_patient(patient_id):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    if not w3.is_connected():
        print("Error: Could not connect to blockchain node.")
        return

    # Load ABI
    with open("blockchain/out/MediFlow.sol/MediFlow.json", "r") as f:
        abi = json.load(f)["abi"]

    contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)

    # Compute Patient Hash
    patient_hash = hashlib.sha256(patient_id.encode()).digest()
    
    print(f"\n--- AUDITING BLOCKCHAIN FOR PATIENT: {patient_id} ---")
    print(f"Contract: {CONTRACT_ADDRESS}")
    print(f"Patient Hash (Lookup Key): {patient_hash.hex()}")

    try:
        prediction_ids = contract.functions.getPatientPredictions(patient_hash).call()
        
        if not prediction_ids:
            print("No records found on-chain for this patient.")
            return

        print(f"Found {len(prediction_ids)} records on the immutable ledger.\n")

        for pid in prediction_ids:
            pred = contract.functions.predictions(pid).call()
            valid = contract.functions.validations(pid).call()
            
            print(f"Record ID: {pid}")
            print(f"  - AI Prediction Hash: {pred[1].hex()}")
            print(f"  - Timestamp: {pred[3]}")
            print(f"  - Recorded By: {pred[4]}")
            
            if valid[0]: # If validation exists
                print(f"  - [DOCTOR VALIDATED]")
                print(f"    Decision: {valid[3]}")
                print(f"    Signature: {valid[4][:32]}...")
                print(f"    Doctor Addr: {valid[6]}")
            else:
                print("  - [AWAITING DOCTOR VALIDATION]")
            print("-" * 40)

    except Exception as e:
        print(f"Audit failed: {e}")

if __name__ == "__main__":
    p_id = sys.argv[1] if len(sys.argv) > 1 else "PT-2026-X89"
    verify_patient(p_id)
