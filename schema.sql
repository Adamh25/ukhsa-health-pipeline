-- Drop existing tables
DROP TABLE IF EXISTS fact_health;
DROP TABLE IF EXISTS dim_metric;
DROP TABLE IF EXISTS dim_area;
DROP TABLE IF EXISTS dim_date;

-- dim_date
CREATE TABLE dim_date (
    date_id INT PRIMARY KEY,
    date_value DATE NOT NULL UNIQUE,
    year INT,
    month_number INT,
    epi_week INT
);

-- dim_area
CREATE TABLE dim_area (
    area_id INT IDENTITY(1,1) PRIMARY KEY,
    area_code VARCHAR(20) NOT NULL UNIQUE,
    area_name VARCHAR(100) NOT NULL,
    area_type VARCHAR(50),
    population INT
);

-- dim_metric
CREATE TABLE dim_metric (
    metric_id INT IDENTITY(1,1) PRIMARY KEY,
    metric_code VARCHAR(100) NOT NULL UNIQUE,
    metric_name VARCHAR(200),
    disease VARCHAR(50),
    category VARCHAR(50),
    unit VARCHAR(50)
);

-- fact_health
CREATE TABLE fact_health (
    health_id BIGINT IDENTITY(1,1) PRIMARY KEY,
    date_id INT NOT NULL,
    area_id INT NOT NULL,
    metric_id INT NOT NULL,
    metric_value DECIMAL(18,4),
    numerator INT,
    denominator INT,
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (area_id) REFERENCES dim_area(area_id),
    FOREIGN KEY (metric_id) REFERENCES dim_metric(metric_id)
);
