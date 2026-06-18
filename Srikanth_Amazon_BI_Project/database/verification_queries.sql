-- ============================================================
-- Project: Amazon Germany Wireless Headphones BI Pipeline
-- File: verification_queries.sql
-- Purpose: Database and data-quality verification
-- ============================================================


-- 1. List project tables
SELECT
    table_schema,
    table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;


-- 2. Display table columns and data types
SELECT
    table_name,
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_schema = 'public'
  AND table_name IN (
      'dim_products',
      'fact_product_observations',
      'etl_run_log'
  )
ORDER BY
    table_name,
    ordinal_position;


-- 3. Check table row counts
SELECT
    'dim_products' AS table_name,
    COUNT(*) AS row_count
FROM dim_products

UNION ALL

SELECT
    'fact_product_observations',
    COUNT(*)
FROM fact_product_observations

UNION ALL

SELECT
    'etl_run_log',
    COUNT(*)
FROM etl_run_log;


-- 4. Check database connection details
SELECT
    current_database() AS database_name,
    current_user AS database_user,
    version() AS postgresql_version;


-- 5. Check orphan observation records
SELECT
    COUNT(*) AS orphan_observations
FROM fact_product_observations f
LEFT JOIN dim_products p
    ON f.asin = p.asin
WHERE p.asin IS NULL;


-- 6. Check duplicate product observations
SELECT
    asin,
    extraction_timestamp,
    COUNT(*) AS duplicate_count
FROM fact_product_observations
GROUP BY
    asin,
    extraction_timestamp
HAVING COUNT(*) > 1;


-- 7. Check invalid numeric values
SELECT
    COUNT(*) FILTER (
        WHERE current_price < 0
    ) AS negative_prices,

    COUNT(*) FILTER (
        WHERE rating < 0
           OR rating > 5
    ) AS invalid_ratings,

    COUNT(*) FILTER (
        WHERE review_count < 0
    ) AS negative_review_counts,

    COUNT(*) FILTER (
        WHERE discount_percentage < 0
           OR discount_percentage > 100
    ) AS invalid_discount_percentages
FROM fact_product_observations;


-- 8. Check required fields for missing values
SELECT
    COUNT(*) FILTER (
        WHERE asin IS NULL
    ) AS missing_asins,

    COUNT(*) FILTER (
        WHERE current_price IS NULL
    ) AS missing_current_prices,

    COUNT(*) FILTER (
        WHERE extraction_date IS NULL
    ) AS missing_extraction_dates,

    COUNT(*) FILTER (
        WHERE extraction_timestamp IS NULL
    ) AS missing_extraction_timestamps
FROM fact_product_observations;


-- 9. Verify product dimension completeness
SELECT
    COUNT(*) FILTER (
        WHERE asin IS NULL
    ) AS missing_asins,

    COUNT(*) FILTER (
        WHERE product_title IS NULL
           OR TRIM(product_title) = ''
    ) AS missing_titles,

    COUNT(*) FILTER (
        WHERE brand IS NULL
           OR TRIM(brand) = ''
    ) AS missing_brands
FROM dim_products;


-- 10. Check primary and foreign-key constraints
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name
FROM information_schema.table_constraints tc
LEFT JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
WHERE tc.table_schema = 'public'
  AND tc.table_name IN (
      'dim_products',
      'fact_product_observations',
      'etl_run_log'
  )
ORDER BY
    tc.table_name,
    tc.constraint_type,
    tc.constraint_name;