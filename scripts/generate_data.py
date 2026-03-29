import pandas as pd
import numpy as np
import random
import os

def generate_synthetic_tb_data(num_records=1000, output_path="data/tb_patients_data.csv"):
    print(f"Generating {num_records} synthetic patient records...")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    data = []
    for _ in range(num_records):
        age = random.randint(0, 85)
        fever_duration_days = random.randint(0, 30)
        cough_duration_days = random.randint(0, 40)
        weight_loss_kg = round(random.uniform(0.0, 15.0), 1)
        night_sweats = random.choice([0, 1])
        hemoptysis = random.choice([0, 1])
        
        # Ground Truth Logic
        tb_probability = 0.05
        if hemoptysis == 1: tb_probability += 0.50
        if cough_duration_days > 14: tb_probability += 0.30
        if fever_duration_days > 7: tb_probability += 0.15
        if night_sweats == 1: tb_probability += 0.15
        if weight_loss_kg > 5.0: tb_probability += 0.10
            
        tb_probability = min(tb_probability, 0.95)
        high_tb_risk = 1 if random.random() < tb_probability else 0
        
        data.append([
            age, fever_duration_days, cough_duration_days, 
            weight_loss_kg, night_sweats, hemoptysis, high_tb_risk
        ])

    columns = [
        "age", "fever_duration_days", "cough_duration_days", 
        "weight_loss_kg", "night_sweats", "hemoptysis", "high_tb_risk"
    ]
    df = pd.DataFrame(data, columns=columns)
    df.to_csv(output_path, index=False)
    print(f"Success. Saved to {output_path}")

if __name__ == "__main__":
    generate_synthetic_tb_data(1000)
