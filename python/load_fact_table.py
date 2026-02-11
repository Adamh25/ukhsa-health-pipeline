import pandas as pd
import pyodbc

# Read CSV
df = pd.read_csv('ukhsa_surveillance_data_raw.csv')
print(f"Loaded {len(df)} rows from CSV")

# Connect to Azure SQL
conn_str = (
    'DRIVER={ODBC Driver 18 for SQL Server};'
    'SERVER=sql-health-pipe4062.database.windows.net;'
    'DATABASE=health-dw;'
    'UID=sqladmin;'
    'PWD=SecurePass123!;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Insert data
inserted = 0
for _, row in df.iterrows():
    date_id = int(row['date'].replace('-', ''))
    
    # Get IDs from dimension tables
    cursor.execute("SELECT area_id FROM dim_area WHERE area_code = ?", row['geography_code'])
    area_id = cursor.fetchone()[0]
    
    cursor.execute("SELECT metric_id FROM dim_metric WHERE metric_code = ?", row['metric'])
    metric_id = cursor.fetchone()[0]
    
    # Insert into fact table
    cursor.execute("""
        INSERT INTO fact_health (date_id, area_id, metric_id, metric_value, numerator, denominator)
        VALUES (?, ?, ?, ?, ?, ?)
    """, date_id, area_id, metric_id, row['positivity_percent'], row['positive_tests'], row['total_tests'])
    
    inserted += 1
    if inserted % 100 == 0:
        print(f"Inserted {inserted} rows...")

conn.commit()
print(f"✅ Total inserted: {inserted}")
conn.close()
