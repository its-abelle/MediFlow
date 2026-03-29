import numpy as np
import pandas as pd
import joblib
from typing import Dict, Tuple, List, Optional
from dataclasses import dataclass

@dataclass
class PatientData:
    """Patient symptom data for TB diagnosis."""
    patient_id: str
    age: int
    fever_duration_days: int
    cough_duration_days: int
    weight_loss_kg: float
    night_sweats: int
    hemoptysis: int
    
    def to_array(self):
        return np.array([[
            self.age,
            self.fever_duration_days,
            self.cough_duration_days,
            self.weight_loss_kg,
            self.night_sweats,
            self.hemoptysis
        ]])
    
    def to_dict(self):
        return {
            'patient_id': self.patient_id,
            'age': self.age,
            'fever_duration_days': self.fever_duration_days,
            'cough_duration_days': self.cough_duration_days,
            'weight_loss_kg': self.weight_loss_kg,
            'night_sweats': self.night_sweats,
            'hemoptysis': self.hemoptysis
        }

@dataclass
class DiagnosticResult:
    """TB Diagnostic Result from models."""
    risk_level: str
    confidence: float
    risk_score: float
    methodology: str
    reasoning: str
    rule_based_result: str
    ml_confidence: float
    recommendation: str
    
    def to_dict(self):
        return {
            'risk_level': self.risk_level,
            'confidence': f'{self.confidence:.2%}',
            'risk_score': round(self.risk_score, 3),
            'methodology': self.methodology,
            'reasoning': self.reasoning,
            'recommendation': self.recommendation
        }

class RuleBasedTBDiagnostic:
    CRITICAL_THRESHOLDS = {
        'hemoptysis': True,
        'cough_min_days': 21,
        'fever_min_days': 14,
        'weight_loss_critical': 10.0,
    }
    
    RISK_LEVELS = {
        'HIGH': {'score': 0.85, 'action': 'Urgent TB testing recommended'},
        'MEDIUM': {'score': 0.50, 'action': 'TB testing recommended with follow-up'},
        'LOW': {'score': 0.15, 'action': 'Monitor for symptom progression'}
    }
    
    @staticmethod
    def diagnose(patient: PatientData) -> DiagnosticResult:
        red_flags = []
        risk_score = 0.0
        
        if patient.hemoptysis == 1:
            red_flags.append("Hemoptysis detected")
            risk_score += 0.35
        if patient.cough_duration_days >= RuleBasedTBDiagnostic.CRITICAL_THRESHOLDS['cough_min_days']:
            red_flags.append(f"Persistent cough ({patient.cough_duration_days} days)")
            risk_score += 0.25
        if patient.fever_duration_days >= RuleBasedTBDiagnostic.CRITICAL_THRESHOLDS['fever_min_days']:
            red_flags.append(f"Prolonged fever ({patient.fever_duration_days} days)")
            risk_score += 0.15
        if patient.night_sweats == 1:
            red_flags.append("Night sweats")
            risk_score += 0.12
        if patient.weight_loss_kg >= RuleBasedTBDiagnostic.CRITICAL_THRESHOLDS['weight_loss_critical']:
            red_flags.append(f"Weight loss ({patient.weight_loss_kg}kg)")
            risk_score += 0.10
            
        if patient.hemoptysis == 1:
            return DiagnosticResult(
                risk_level="HIGH", confidence=0.95, risk_score=0.95,
                methodology="Rule-Based (Hemoptysis)",
                reasoning="Hemoptysis is a strong TB indicator.",
                rule_based_result="HIGH", ml_confidence=0.95,
                recommendation="Urgent TB testing required."
            )
        
        risk_score = min(risk_score, 1.0)
        risk_level = "HIGH" if risk_score >= 0.75 else "MEDIUM" if risk_score >= 0.50 else "LOW"
        confidence = 0.90 if risk_level == "HIGH" else 0.70 if risk_level == "MEDIUM" else 0.60
        
        return DiagnosticResult(
            risk_level=risk_level, confidence=confidence, risk_score=risk_score,
            methodology=f"Rule-Based ({len(red_flags)} factors)",
            reasoning=", ".join(red_flags) if red_flags else "No significant factors.",
            rule_based_result=risk_level, ml_confidence=confidence,
            recommendation=RuleBasedTBDiagnostic.RISK_LEVELS[risk_level]['action']
        )

class RandomForestTBDiagnostic:
    def __init__(self, model_path: str = None):
        self.model = None
        self.feature_names = ['age', 'fever_duration_days', 'cough_duration_days', 'weight_loss_kg', 'night_sweats', 'hemoptysis']
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str):
        try:
            self.model = joblib.load(model_path)
        except Exception as e:
            print(f"Failed to load model: {e}")
            
    def diagnose(self, patient: PatientData) -> DiagnosticResult:
        if self.model is None:
            raise ValueError("Model not loaded")
        
        features = patient.to_array()
        probabilities = self.model.predict_proba(features)[0]
        confidence_high_risk = probabilities[1]
        
        risk_level = "HIGH" if confidence_high_risk > 0.75 else "MEDIUM" if confidence_high_risk > 0.50 else "LOW"
        
        return DiagnosticResult(
            risk_level=risk_level, confidence=confidence_high_risk, risk_score=confidence_high_risk,
            methodology="Random Forest ML Model",
            reasoning="ML pattern identification.",
            rule_based_result=risk_level, ml_confidence=confidence_high_risk,
            recommendation="Refer for testing" if confidence_high_risk > 0.5 else "Monitor"
        )

class TBDiagnosticEngine:
    def __init__(self, ml_model_path: str = None):
        self.rule_based = RuleBasedTBDiagnostic()
        self.ml_model = RandomForestTBDiagnostic(model_path=ml_model_path)
    
    def diagnose(self, patient: PatientData) -> Tuple[DiagnosticResult, str]:
        rule_result = self.rule_based.diagnose(patient)
        if rule_result.risk_level == "HIGH" and "Hemoptysis" in rule_result.reasoning:
            return rule_result, "Rule-Based (Critical)"
        
        try:
            ml_result = self.ml_model.diagnose(patient)
            # Simple consensus logic
            if rule_result.risk_level == ml_result.risk_level:
                return rule_result, "Hybrid (Consensus)"
            return ml_result, "Hybrid (ML-Lead)"
        except Exception:
            return rule_result, "Rule-Based (Fallback)"
