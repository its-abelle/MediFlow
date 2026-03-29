import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional
from web3 import Web3
from eth_account import Account
import logging

logger = logging.getLogger("mediflow")

class MediFlowBlockchain:
    def __init__(self, provider_url: str = None, contract_address: str = None, private_key: str = None):
        self.w3 = None
        self.contract = None
        self.account = None
        self.mock_mode = True
        self.chain = [] # For mock mode simulation

        if provider_url and contract_address:
            try:
                self.w3 = Web3(Web3.HTTPProvider(provider_url))
                if self.w3.is_connected():
                    # Load contract ABI from Foundry artifacts
                    abi_path = "blockchain/out/MediFlow.sol/MediFlow.json"
                    if os.path.exists(abi_path):
                        with open(abi_path, "r") as f:
                            contract_json = json.load(f)
                            self.contract = self.w3.eth.contract(
                                address=Web3.to_checksum_address(contract_address), 
                                abi=contract_json["abi"]
                            )
                        
                        if private_key:
                            self.account = Account.from_key(private_key)
                            self.mock_mode = False
                            logger.info(f"Connected to blockchain at {provider_url}")
                    else:
                        logger.warning(f"ABI file not found at {abi_path}. Using mock mode.")
                else:
                    logger.warning("Blockchain provider not reachable. Using mock mode.")
            except Exception as e:
                logger.error(f"Blockchain init error: {e}. Falling back to mock mode.")

    def _get_patient_id_hash(self, patient_id: str) -> bytes:
        return hashlib.sha256(patient_id.encode()).digest()

    def record_ai_prediction(self, prediction_id: str, patient_id: str, prediction_hash: str) -> Dict:
        patient_id_hash = self._get_patient_id_hash(patient_id)
        pred_hash_bytes = bytes.fromhex(prediction_hash)

        if self.mock_mode:
            logger.info(f"[Mock] Recording AI prediction {prediction_id}")
            tx = {
                "transaction_id": f"mock_tx_ai_{prediction_id[:8]}",
                "prediction_id": prediction_id,
                "patient_id_hash": patient_id_hash.hex(),
                "prediction_hash": prediction_hash,
                "timestamp": datetime.now().isoformat(),
                "block_number": len(self.chain) + 1
            }
            self.chain.append(tx)
            return tx
        
        try:
            # Build and send transaction
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx_data = self.contract.functions.recordAIPrediction(
                prediction_id,
                pred_hash_bytes,
                patient_id_hash
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, private_key=self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "transaction_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"On-chain AI record failed: {e}")
            return {"status": "error", "message": str(e)}

    def record_doctor_validation(self, validation_id: str, prediction_id: str, doctor_id: str, decision: str, signature: str) -> Dict:
        if self.mock_mode:
            logger.info(f"[Mock] Recording Doctor validation for {prediction_id}")
            return {"status": "success", "message": "Mock validation recorded", "transaction_hash": f"mock_tx_val_{validation_id[:8]}"}

        try:
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            tx_data = self.contract.functions.recordDoctorValidation(
                validation_id,
                prediction_id,
                doctor_id,
                decision,
                signature
            ).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.w3.eth.account.sign_transaction(tx_data, private_key=self.account.key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            return {
                "transaction_hash": tx_hash.hex(),
                "block_number": receipt.blockNumber,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"On-chain validation record failed: {e}")
            return {"status": "error", "message": str(e)}

    def get_audit_trail(self, patient_id: str) -> List[Dict]:
        patient_id_hash = self._get_patient_id_hash(patient_id)
        
        if self.mock_mode:
            return [tx for tx in self.chain if tx.get("patient_id_hash") == patient_id_hash.hex()]
        
        try:
            prediction_ids = self.contract.functions.getPatientPredictions(patient_id_hash).call()
            trail = []
            for pid in prediction_ids:
                pred = self.contract.functions.predictions(pid).call()
                valid = self.contract.functions.validations(pid).call()
                trail.append({
                    "prediction": {
                        "id": pred[0],
                        "hash": pred[1].hex(),
                        "timestamp": pred[3],
                        "recorded_by": pred[4]
                    },
                    "validation": {
                        "id": valid[0],
                        "decision": valid[3],
                        "signature": valid[4],
                        "timestamp": valid[5],
                        "doctor_address": valid[6]
                    } if valid[0] else None
                })
            return trail
        except Exception as e:
            logger.error(f"Failed to fetch audit trail: {e}")
            return []
