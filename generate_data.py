import pandas as pd
import numpy as np
import random

def generate_synthetic_tb_data(num_records=1000):
    print("Escaping the matrix: Generating synthetic patient records...")
    
    data = []
    for _ in range(num_records):
        # 1. Generate Base Patient Features
        age = random.randint(18, 85)
        fever_duration_days = random.randint(0, 30)
        cough_duration_days = random.randint(0, 40)
        weight_loss_kg = round(random.uniform(0.0, 15.0), 1)
        night_sweats = random.choice([0, 1]) # 0 = No, 1 = Yes
        hemoptysis = random.choice([0, 1])   # Coughing blood
        
        # 2. Establish the "Ground Truth" Logic for the AI to learn
        # We mathematically weight the probability of having TB based on WHO symptoms
        tb_probability = 0.05 # Base risk
        
        if hemoptysis == 1:
            tb_probability += 0.50
        if cough_duration_days > 14:
            tb_probability += 0.30
        if fever_duration_days > 7:
            tb_probability += 0.15
        if night_sweats == 1:
            tb_probability += 0.15
        if weight_loss_kg > 5.0:
            tb_probability += 0.10
            
        # Cap probability at 95% to introduce slight real-world noise
        tb_probability = min(tb_probability, 0.95)
        
        # 3. Assign Final Diagnosis based on probability
        high_tb_risk = 1 if random.random() < tb_probability else 0
        
        # Append to our dataset
        data.append([
            age, fever_duration_days, cough_duration_days, 
            weight_loss_kg, night_sweats, hemoptysis, high_tb_risk
        ])

    # 4. Convert to a Pandas DataFrame and Save
    columns = [
        "age", "fever_duration_days", "cough_duration_days", 
        "weight_loss_kg", "night_sweats", "hemoptysis", "high_tb_risk"
    ]
    df = pd.DataFrame(data, columns=columns)
    
    file_path = "data/tb_patients_data.csv"
    df.to_csv(file_path, index=False)
    print(f"Success. {num_records} patient records generated and saved to {file_path}")

if __name__ == "__main__":
    generate_synthetic_tb_data(1000)