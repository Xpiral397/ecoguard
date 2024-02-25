import pandas as pd
import numpy as np

def generate_and_save_data(filename='training_data.csv'):
    np.random.seed(42)  # For reproducibility
    num_rows = 20000

    # Generate random data
    data = {
        'vegetation_cover': np.random.uniform(0, 1, num_rows),
        'land_use': np.random.uniform(0, 1, num_rows),
        'climate': np.random.uniform(20, 30, num_rows),
        'Deforestation_Rate': np.random.uniform(0, 0.1, num_rows),
        'Water_Turbidity': np.random.uniform(5, 15, num_rows),
        'Life_Measurement': np.random.randint(50, 100, num_rows),
        'NDVI': np.random.uniform(0.5, 0.9, num_rows),
        'Soil_Fertility': np.random.uniform(7, 9, num_rows),
        'NO2_Measurement': np.random.uniform(10, 20, num_rows),
        'Growth': np.random.uniform(0.01, 0.03, num_rows),
        'Population': np.random.randint(8000, 12000, num_rows),
        'Civilization': np.random.uniform(0.7, 0.9, num_rows),
        'Mortality_Rate': np.random.uniform(0.003, 0.009, num_rows),
        'Wildlife': np.random.randint(40, 70, num_rows)
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Save to CSV
    df.to_csv(filename, index=False)
    print(f'Data saved to {filename}')

# Call the function to generate and save data
generate_and_save_data()
