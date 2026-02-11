import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

def generate_data():
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    
    dates = []
    current = start_date
    while current <= end_date:
        dates.append(current)
        current += timedelta(days=7)
    
    regions = [
        ('England', 'E92000001', 'Nation'),
        ('North East', 'E12000001', 'Region'),
        ('North West', 'E12000002', 'Region'),
        ('Yorkshire and The Humber', 'E12000003', 'Region'),
        ('East Midlands', 'E12000004', 'Region'),
        ('West Midlands', 'E12000005', 'Region'),
        ('East of England', 'E12000006', 'Region'),
        ('London', 'E12000007', 'Region'),
        ('South East', 'E12000008', 'Region'),
        ('South West', 'E12000009', 'Region'),
    ]
    
    diseases = [
        ('influenza', 8.0, 1.5),
        ('RSV', 3.0, 1.3),
        ('COVID-19', 5.0, 0.8),
    ]
    
    records = []
    
    for disease, base_pos, seasonal in diseases:
        for region_name, region_code, geo_type in regions:
            for date in dates:
                day_of_year = date.timetuple().tm_yday
                seasonal_wave = np.sin((day_of_year - 230) * 2 * np.pi / 365) * seasonal
                
                positivity = base_pos + seasonal_wave * base_pos * 0.7
                positivity += np.random.normal(0, base_pos * 0.1)
                positivity = max(0.1, min(positivity, 40.0))
                
                population_factor = 1.0 if geo_type == 'Nation' else np.random.uniform(0.05, 0.15)
                tests_conducted = int(50000 * population_factor)
                positive_tests = int(tests_conducted * positivity / 100)
                
                if region_name != 'England':
                    regional_variation = np.random.uniform(0.8, 1.2)
                    positive_tests = int(positive_tests * regional_variation)
                    positivity = (positive_tests / tests_conducted * 100) if tests_conducted > 0 else 0
                
                records.append({
                    'date': date.strftime('%Y-%m-%d'),
                    'epiweek': date.isocalendar()[1],
                    'year': date.year,
                    'month': date.month,
                    'geography': region_name,
                    'geography_code': region_code,
                    'geography_type': geo_type,
                    'disease': disease,
                    'metric': f'{disease.lower().replace("-", "_")}_testing_positivityByWeek',
                    'positivity_percent': round(positivity, 2),
                    'positive_tests': positive_tests,
                    'total_tests': tests_conducted,
                    'age': 'all',
                    'sex': 'all'
                })
    
    return pd.DataFrame(records)

df = generate_data()
df.to_csv('ukhsa_surveillance_data_raw.csv', index=False)
print(f"✅ Generated {len(df)} records")
