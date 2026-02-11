# UKHSA Infectious Disease Surveillance Pipeline

**End-to-end Azure data engineering project analyzing weekly infectious disease trends across NHS England regions**

---

## Project Overview

Built a cloud-based data warehouse and analytics dashboard to track infectious disease surveillance data (Influenza, RSV, COVID-19) across England's NHS regions. The pipeline ingests weekly testing positivity rates, implements star schema dimensional modeling in Azure SQL Database, and visualizes trends with statistical anomaly detection in Power BI.

**Key Achievement:** Designed and deployed a production-grade data pipeline on Azure for under $3 using student credits, demonstrating cost-effective cloud architecture suitable for pharma/biotech analytics applications.

---

## Business Context

Public health agencies like UKHSA (UK Health Security Agency) monitor infectious disease spread to:
- Identify outbreak hotspots requiring intervention
- Track seasonal patterns for resource allocation
- Compare regional performance against national baselines
- Detect statistical anomalies warranting investigation

This project replicates enterprise health surveillance workflows using Azure cloud infrastructure.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                              │
│          Synthetic UKHSA Weekly Surveillance Data                │
│     (Influenza, RSV, COVID-19 across 10 geographies)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   AZURE BLOB STORAGE                             │
│   Container: raw/ukhsa/YYYYMMDD/data.csv                        │
│   Role: Raw data landing zone                                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    ETL PIPELINE (Python)                         │
│   ┌──────────────────────────────────────────────────┐          │
│   │  1. Extract: Read CSV from Blob Storage          │          │
│   │  2. Transform: Parse dates, map codes to IDs     │          │
│   │  3. Validate: Non-negative values, dedupe        │          │
│   │  4. Load: INSERT into fact_health table          │          │
│   └──────────────────────────────────────────────────┘          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│              AZURE SQL DATABASE (Star Schema)                    │
│                                                                  │
│   ┌──────────────┐      ┌──────────────┐      ┌─────────────┐  │
│   │  dim_date    │      │  dim_area    │      │ dim_metric  │  │
│   │  (731 rows)  │      │  (10 rows)   │      │  (3 rows)   │  │
│   └──────┬───────┘      └──────┬───────┘      └──────┬──────┘  │
│          │                     │                     │          │
│          └──────────┬──────────┴──────────┬──────────┘          │
│                     ▼                     ▼                     │
│              ┌────────────────────────────────┐                 │
│              │      fact_health               │                 │
│              │      (3,150 rows)              │                 │
│              │  Grain: (date, area, metric)   │                 │
│              └────────────────────────────────┘                 │
│                                                                  │
│   Service Tier: Basic (5 DTU) - ~$0.14/day                     │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    POWER BI DASHBOARD                            │
│                                                                  │
│   📈 KPIs: Current week positivity, WoW change                  │
│   📊 Time Series: 2-year trend with seasonal patterns           │
│   🗺️ Regional Comparison: Bar chart across NHS areas            │
│   🚨 Anomaly Detection: Z-score alerts (threshold ≥1.0)         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Cloud Platform** | Microsoft Azure | Infrastructure hosting |
| **Data Storage** | Azure Blob Storage | Raw file landing zone |
| **Data Warehouse** | Azure SQL Database (Basic tier) | Star schema OLAP database |
| **Orchestration** | Azure Data Factory | Pipeline framework (created but not configured) |
| **ETL Logic** | Python 3.12 (pandas, pyodbc) | Data transformation & loading |
| **Data Modeling** | SQL (T-SQL dialect) | Schema design, constraints, indexes |
| **Visualization** | Power BI Desktop/Service | Interactive dashboards |
| **Analytics** | DAX (Data Analysis Expressions) | KPIs, moving averages, z-scores |
| **Deployment** | Azure CLI, Cloud Shell | Infrastructure as Code |

---

## Data Model

### Star Schema Design

**Fact Table:**
- `fact_health` (3,150 rows)
  - `date_id` → Foreign key to `dim_date`
  - `area_id` → Foreign key to `dim_area`
  - `metric_id` → Foreign key to `dim_metric`
  - `metric_value` (DECIMAL) → Testing positivity percentage
  - `numerator` (INT) → Positive test count
  - `denominator` (INT) → Total tests conducted

**Dimension Tables:**
- `dim_date` (731 rows) → Every day 2023-2024, includes epi_week
- `dim_area` (10 rows) → England + 9 NHS regions with ONS codes
- `dim_metric` (3 rows) → Influenza, RSV, COVID-19 testing metrics

**Grain:** One row per (date, geography, disease) combination

### Sample Query
```sql
-- Latest week's positivity rates for England
SELECT 
    d.date_value,
    m.disease,
    f.metric_value AS positivity_pct,
    f.numerator AS positive_tests,
    f.denominator AS total_tests
FROM fact_health f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_area a ON f.area_id = a.area_id
JOIN dim_metric m ON f.metric_id = m.metric_id
WHERE a.area_name = 'England'
  AND d.date_value >= DATEADD(day, -7, GETDATE())
ORDER BY d.date_value DESC, m.disease;
```

---

## Dashboard

### Overview - All Diseases
Displays KPI cards (current week: 9.14%, WoW change: -0.01%), time series showing clear seasonal peaks (winter influenza reaching 10%), regional bar chart, and detailed table with week-over-week comparisons.

*Screenshot: `screenshots/dashboard_all.png`*

### Filtered View - Influenza Only
Interactive filter isolates influenza data, revealing sharper seasonal patterns with December-January peaks at 14-18%. Anomaly detection flags West Midlands at 17.80% (z-score 1.00), indicating 1 standard deviation above seasonal baseline.

*Screenshot: `screenshots/dashboard_influenza.png`*

**Key Features:**
- Interactive Filters: Toggle between COVID-19, Influenza, RSV
- KPI Cards: Current week positivity, week-over-week % change
- Time Series Chart: 2-year trend (Jan 2023 - Dec 2024) with seasonal patterns
- Regional Comparison: Horizontal bar chart ranking all NHS areas
- Detail Table: Sortable grid with precise metrics and WoW deltas
- Anomaly Alerts: Statistical outlier detection using rolling z-scores (threshold ≥1.0)

---

## Key Insights

### Epidemiological Findings
1. **Seasonal Patterns:** Influenza and RSV show strong winter seasonality with peaks in December-January (8-10% positivity)
2. **COVID-19 Behavior:** Less pronounced seasonal variation compared to traditional respiratory viruses (4-6% year-round)
3. **Regional Variation:** West Midlands consistently 15-20% above national average for influenza
4. **Anomaly Detection:** 3 region-disease combinations flagged as statistical outliers (z-score ≥1.0) in latest week

### Technical Outcomes
- Successfully deployed star schema with proper referential integrity
- ETL pipeline handles 3,150 records with zero data quality issues
- Power BI connects live to Azure SQL with sub-second query performance
- Total infrastructure cost: **$0.42** for 3-day deployment (under $3 for full 2-week demo)

---

## Setup & Deployment

### Prerequisites
- Azure subscription (Azure for Students recommended - $100 free credits)
- Azure CLI installed ([installation guide](https://docs.microsoft.com/cli/azure/install-azure-cli))
- Python 3.8+ with `pandas`, `pyodbc`
- Power BI Desktop (Windows) or Power BI Service (web)

### Quick Start

**1. Clone Repository**
```bash
git clone https://github.com/YOUR_USERNAME/ukhsa-health-pipeline.git
cd ukhsa-health-pipeline
```

**2. Deploy Azure Resources**
```bash
# Set variables
LOCATION="spaincentral"  # Or your allowed region
RG_NAME="rg-health-pipeline"
STORAGE_NAME="sthealthpipe$(openssl rand -hex 4)"
SQL_SERVER="sql-health-pipe$(openssl rand -hex 4)"

# Create resource group
az group create --name $RG_NAME --location $LOCATION

# Create storage account
az storage account create \
  --name $STORAGE_NAME \
  --resource-group $RG_NAME \
  --location $LOCATION \
  --sku Standard_LRS

# Create SQL server & database
az sql server create \
  --name $SQL_SERVER \
  --resource-group $RG_NAME \
  --location $LOCATION \
  --admin-user sqladmin \
  --admin-password 'YOUR_SECURE_PASSWORD'

az sql db create \
  --resource-group $RG_NAME \
  --server $SQL_SERVER \
  --name health-dw \
  --service-objective Basic
```

**3. Load Database Schema**
```bash
# Add your IP to firewall
MY_IP=$(curl -s ifconfig.me)
az sql server firewall-rule create \
  --resource-group $RG_NAME \
  --server $SQL_SERVER \
  --name AllowMyIP \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP

# Run SQL scripts
sqlcmd -S $SQL_SERVER.database.windows.net \
  -d health-dw \
  -U sqladmin \
  -P 'YOUR_SECURE_PASSWORD' \
  -i sql/schema.sql

sqlcmd -S $SQL_SERVER.database.windows.net \
  -d health-dw \
  -U sqladmin \
  -P 'YOUR_SECURE_PASSWORD' \
  -i sql/populate_dims.sql
```

**4. Generate & Load Data**
```bash
python3 python/generate_data.py
python3 python/load_fact_table.py
```

**5. Connect Power BI**
- Open Power BI Desktop or go to https://app.powerbi.com
- Get Data → Azure SQL Database
- Server: `YOUR_SQL_SERVER.database.windows.net`
- Database: `health-dw`
- Authentication: SQL Server (username: `sqladmin`, password: `YOUR_SECURE_PASSWORD`)
- Import tables: `dim_date`, `dim_area`, `dim_metric`, `fact_health`
- Open `powerbi/ukhsa_health_dashboard.pbix` or build from scratch

### Cost Management
```bash
# Pause SQL database when not in use
az sql db pause --resource-group $RG_NAME --server $SQL_SERVER --name health-dw

# Delete all resources when done
az group delete --name $RG_NAME --yes --no-wait
```

**Estimated Costs:**
- 2-week deployment: ~$2-3 (Azure for Students: $100 free credits)
- Daily rate: $0.14 (SQL Basic tier only)

---

## DAX Measures (Power BI)

```dax
// Current Week Positivity
Current Week Positivity = 
CALCULATE(
    AVERAGE(fact_health[metric_value]),
    LASTDATE(dim_date[date_value])
)

// Week-over-Week Change
WoW Change % = 
VAR CurrentWeek = [Current Week Positivity]
VAR PreviousWeek = 
    CALCULATE(
        [Current Week Positivity],
        DATEADD(dim_date[date_value], -7, DAY)
    )
RETURN
    CurrentWeek - PreviousWeek

// Moving Average (4 weeks)
MA 4-Week = 
CALCULATE(
    AVERAGE(fact_health[metric_value]),
    DATESINPERIOD(dim_date[date_value], LASTDATE(dim_date[date_value]), -4, WEEK)
)

// Z-Score for Anomaly Detection
Z-Score = 
VAR CurrentValue = [Current Week Positivity]
VAR HistoricalMean = 
    CALCULATE(
        AVERAGE(fact_health[metric_value]),
        DATESINPERIOD(dim_date[date_value], LASTDATE(dim_date[date_value]), -12, WEEK)
    )
VAR HistoricalStdDev = 
    CALCULATE(
        STDEV.P(fact_health[metric_value]),
        DATESINPERIOD(dim_date[date_value], LASTDATE(dim_date[date_value]), -12, WEEK)
    )
RETURN
    DIVIDE(CurrentValue - HistoricalMean, HistoricalStdDev, 0)

// Anomaly Flag
Is Anomaly = IF([Z-Score] >= 1.0, 1, 0)
```

---

## Project Structure

```
ukhsa-health-pipeline/
├── README.md                          # This file
├── .gitignore                         # Excludes passwords, temp files
│
├── screenshots/                       # Dashboard visuals
│   ├── dashboard_all.png
│   └── dashboard_influenza.png
│
├── sql/                               # Database scripts
│   ├── schema.sql                     # DDL for all tables
│   └── populate_dims.sql              # Dimension data inserts
│
├── python/                            # ETL code
│   ├── generate_data.py               # Synthetic data generator
│   └── load_fact_table.py             # CSV → SQL loader
│
├── powerbi/                           # Dashboard assets
│   └── ukhsa_health_dashboard.pbix    # Power BI file
│
└── data/                              # Sample data
    └── ukhsa_surveillance_data_raw.csv # 2 years, 3,150 records
```

---

## Skills Demonstrated

### Technical Competencies
- Cloud Architecture: Azure resource provisioning, cost optimization
- Data Modeling: Star schema design, referential integrity, indexing
- ETL Development: Python data pipelines with error handling
- SQL Proficiency: Complex joins, window functions, T-SQL
- BI Development: Power BI DAX measures, interactive dashboards
- Statistical Analysis: Z-score anomaly detection, moving averages

### Domain Knowledge
- Healthcare Analytics: Epidemiological metrics, seasonal trends
- Public Health: Surveillance data interpretation, outbreak detection
- Data Quality: Validation rules, deduplication, data governance

---

## Future Enhancements

### Technical Improvements
1. **Automate ETL:** Configure Azure Data Factory pipelines with weekly scheduling
2. **Incremental Loading:** Implement change data capture (CDC) to avoid full refreshes
3. **Data Quality:** Add `dq_issues` logging table with constraint violation tracking
4. **ML Integration:** Azure ML for time-series forecasting (ARIMA/Prophet models)
5. **Real-time Alerts:** Azure Monitor + Logic Apps to email on anomaly threshold breach

### Analytics Expansion
1. **Age Stratification:** Break down by 0-4, 5-14, 15-44, 45-64, 65+ age bands
2. **Geospatial Analysis:** Add Power BI map visual with choropleth coloring
3. **Comparative Benchmarking:** Compare current season vs. 5-year historical average
4. **Vaccine Impact:** Correlate flu vaccination coverage with positivity rates
5. **Multi-disease Correlation:** Analyze co-circulation patterns (flu + COVID)

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Contact

**Adam Hussain** | Life Sciences Student  
[LinkedIn](https://www.linkedin.com/in/adamhussain25/) | hlahus17@liverpool.ac.uk | [GitHub](https://github.com/Adamh25)

---

## Acknowledgments

- **UKHSA** for open surveillance data methodologies
- **Azure for Students** program for free credits

---

*Last updated: February 2026*
