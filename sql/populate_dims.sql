-- Populate dim_date (2023-2024)
DECLARE @StartDate DATE = '2023-01-01';
DECLARE @EndDate DATE = '2024-12-31';
DECLARE @CurrentDate DATE = @StartDate;

WHILE @CurrentDate <= @EndDate
BEGIN
    INSERT INTO dim_date (date_id, date_value, year, month_number, epi_week)
    VALUES (
        CAST(FORMAT(@CurrentDate, 'yyyyMMdd') AS INT),
        @CurrentDate,
        YEAR(@CurrentDate),
        MONTH(@CurrentDate),
        DATEPART(ISO_WEEK, @CurrentDate)
    );
    SET @CurrentDate = DATEADD(DAY, 1, @CurrentDate);
END;

-- Populate dim_area
INSERT INTO dim_area (area_code, area_name, area_type, population) VALUES
('E92000001', 'England', 'Nation', 56550000),
('E12000001', 'North East', 'Region', 2647000),
('E12000002', 'North West', 'Region', 7366000),
('E12000003', 'Yorkshire and The Humber', 'Region', 5502000),
('E12000004', 'East Midlands', 'Region', 4835000),
('E12000005', 'West Midlands', 'Region', 5950000),
('E12000006', 'East of England', 'Region', 6269000),
('E12000007', 'London', 'Region', 8982000),
('E12000008', 'South East', 'Region', 9180000),
('E12000009', 'South West', 'Region', 5625000);

-- Populate dim_metric
INSERT INTO dim_metric (metric_code, metric_name, disease, category, unit) VALUES
('influenza_testing_positivityByWeek', 'Influenza Testing Positivity', 'influenza', 'testing', 'percentage'),
('rsv_testing_positivityByWeek', 'RSV Testing Positivity', 'RSV', 'testing', 'percentage'),
('covid_19_testing_positivityByWeek', 'COVID-19 Testing Positivity', 'COVID-19', 'testing', 'percentage');
