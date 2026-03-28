import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

def train_mediflow_ai():
    print("[MediFlow AI] Starting training sequence...")
    
    # 1. Load the data we generated
    data_path = "data/tb_patients_data.csv"
    if not os.path.exists(data_path):
        print(f"Error: {data_path} not found. Run generate_data.py first!")
        return

    df = pd.read_csv(data_path)

    # 2. Features (X) and Target (y)
    # We drop 'high_tb_risk' because that's what we want to predict
    X = df.drop("high_tb_risk", axis=1)
    y = df["high_tb_risk"]

    # 3. Split into Train (80%) and Test (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. Initialize and Train the Random Forest
    # n_estimators=100 means we are using 100 decision trees
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 5. Evaluate the "Brain"
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    
    print(f"\nTraining Complete!")
    print(f"Model Accuracy: {accuracy * 100:.2%}")
    print("\nClassification Report:")
    print(classification_report(y_test, predictions))

    # 6. Save the model for the Hybrid Engine to use
    os.makedirs("models", exist_ok=True)
    model_save_path = "models/rf_tb_model.pkl"
    joblib.dump(model, model_save_path)
    print(f"Model saved successfully at: {model_save_path}")

if __name__ == "__main__":
    train_mediflow_ai()