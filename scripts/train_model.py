import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import os
from scripts.generate_data import generate_synthetic_tb_data

def train_production_model(data_path="data/tb_patients_data.csv", model_path="app/resources/models/rf_tb_model.pkl"):
    print("--- Training Production TB Model ---")
    
    # Generate fresh large dataset if not exists
    if not os.path.exists(data_path):
        generate_synthetic_tb_data(5000, data_path)
    
    df = pd.read_csv(data_path)
    
    X = df.drop("high_tb_risk", axis=1)
    y = df["high_tb_risk"]
    
    # Train with production settings
    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X, y)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    # Save model
    joblib.dump(model, model_path)
    print(f"✓ Model trained and saved to {model_path}")
    
    # Log some stats
    importances = pd.Series(model.feature_importances_, index=X.columns)
    print("\nFeature Importances:")
    print(importances.sort_values(ascending=False))

if __name__ == "__main__":
    train_production_model()
