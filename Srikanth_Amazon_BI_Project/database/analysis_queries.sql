-- ============================================================
-- Project: Amazon Germany Wireless Headphones BI Pipeline
-- File: analysis_queries.sql
-- Purpose: Business analysis and KPI queries
-- ============================================================


-- 1. Total unique products
SELECT
    COUNT(*) AS total_unique_products
FROM dim_products;


-- 2. Total observations
SELECT
    COUNT(*) AS total_observations
FROM fact_product_observations;


-- 3. Main KPIs
SELECT
    COUNT(*) AS total_observations,
    ROUND(AVG(current_price), 2) AS average_price_eur,
    ROUND(MIN(current_price), 2) AS minimum_price_eur,
    ROUND(MAX(current_price), 2) AS maximum_price_eur,
    ROUND(AVG(rating), 2) AS average_rating,
    SUM(review_count) AS total_reviews
FROM fact_product_observations;


-- 4. Products by brand
SELECT
    brand,
    COUNT(*) AS product_count
FROM dim_products
GROUP BY brand
ORDER BY
    product_count DESC,
    brand;


-- 5. Brand performance
SELECT
    p.brand,
    COUNT(DISTINCT p.asin) AS product_count,
    ROUND(AVG(f.current_price), 2) AS average_price_eur,
    ROUND(MIN(f.current_price), 2) AS minimum_price_eur,
    ROUND(MAX(f.current_price), 2) AS maximum_price_eur,
    ROUND(AVG(f.rating), 2) AS average_rating,
    SUM(f.review_count) AS total_reviews
FROM dim_products p
JOIN fact_product_observations f
    ON p.asin = f.asin
GROUP BY p.brand
ORDER BY average_price_eur DESC;


-- 6. Price category analysis
SELECT
    price_category,
    COUNT(*) AS product_count,
    ROUND(AVG(current_price), 2) AS average_price_eur,
    ROUND(AVG(rating), 2) AS average_rating,
    SUM(review_count) AS total_reviews
FROM fact_product_observations
GROUP BY price_category
ORDER BY
    CASE price_category
        WHEN 'Budget' THEN 1
        WHEN 'Mid-range' THEN 2
        WHEN 'Premium' THEN 3
        WHEN 'Luxury' THEN 4
        ELSE 5
    END;


-- 7. Price category share
SELECT
    price_category,
    COUNT(*) AS product_count,
    ROUND(
        (
            COUNT(*) * 100.0
            / SUM(COUNT(*)) OVER ()
        )::numeric,
        2
    ) AS product_share_percentage
FROM fact_product_observations
GROUP BY price_category
ORDER BY product_count DESC;


-- 8. Rating category analysis
SELECT
    rating_category,
    COUNT(*) AS product_count,
    ROUND(AVG(rating), 2) AS average_rating,
    ROUND(AVG(current_price), 2) AS average_price_eur,
    SUM(review_count) AS total_reviews
FROM fact_product_observations
GROUP BY rating_category
ORDER BY
    CASE rating_category
        WHEN 'Low' THEN 1
        WHEN 'Average' THEN 2
        WHEN 'Good' THEN 3
        WHEN 'Excellent' THEN 4
        ELSE 5
    END;


-- 9. Top-rated products
SELECT
    p.asin,
    p.product_title,
    p.brand,
    f.current_price,
    f.rating,
    f.review_count,
    f.price_category
FROM dim_products p
JOIN fact_product_observations f
    ON p.asin = f.asin
ORDER BY
    f.rating DESC,
    f.review_count DESC
LIMIT 10;


-- 10. Most-reviewed products
SELECT
    p.asin,
    p.product_title,
    p.brand,
    f.current_price,
    f.rating,
    f.review_count,
    f.price_category
FROM dim_products p
JOIN fact_product_observations f
    ON p.asin = f.asin
ORDER BY
    f.review_count DESC,
    f.rating DESC
LIMIT 10;


-- 11. Prime versus non-Prime products
SELECT
    CASE
        WHEN is_prime = TRUE THEN 'Prime'
        ELSE 'Non-Prime'
    END AS prime_status,
    COUNT(*) AS product_count,
    ROUND(AVG(current_price), 2) AS average_price_eur,
    ROUND(AVG(rating), 2) AS average_rating,
    SUM(review_count) AS total_reviews
FROM fact_product_observations
GROUP BY is_prime
ORDER BY product_count DESC;


-- 12. Sponsored versus organic listings
SELECT
    CASE
        WHEN is_sponsored = TRUE THEN 'Sponsored'
        ELSE 'Organic'
    END AS listing_type,
    COUNT(*) AS product_count,
    ROUND(AVG(current_price), 2) AS average_price_eur,
    ROUND(AVG(rating), 2) AS average_rating,
    SUM(review_count) AS total_reviews
FROM fact_product_observations
GROUP BY is_sponsored
ORDER BY product_count DESC;


-- 13. Affordable and highly rated products
SELECT
    p.product_title,
    p.brand,
    f.current_price,
    f.rating,
    f.review_count,
    f.price_category
FROM dim_products p
JOIN fact_product_observations f
    ON p.asin = f.asin
WHERE
    f.rating >= 4.0
    AND f.current_price <= 60
ORDER BY
    f.rating DESC,
    f.review_count DESC,
    f.current_price ASC;


-- 14. Exploratory value score
-- Higher values indicate stronger rating/review performance
-- relative to price.
SELECT
    p.product_title,
    p.brand,
    f.current_price,
    f.rating,
    f.review_count,
    ROUND(
        (
            (
                f.rating * LN(f.review_count + 1)
            )
            / NULLIF(f.current_price, 0)
        )::numeric,
        4
    ) AS value_score
FROM dim_products p
JOIN fact_product_observations f
    ON p.asin = f.asin
WHERE
    f.current_price IS NOT NULL
    AND f.current_price > 0
    AND f.rating IS NOT NULL
    AND f.review_count IS NOT NULL
ORDER BY value_score DESC
LIMIT 10;


-- 15. Price and rating dataset
SELECT
    p.product_title,
    p.brand,
    f.current_price,
    f.rating,
    f.review_count
FROM dim_products p
JOIN fact_product_observations f
    ON p.asin = f.asin
WHERE
    f.current_price IS NOT NULL
    AND f.rating IS NOT NULL
ORDER BY f.current_price;


-- 16. Price-rating correlation
SELECT
    ROUND(
        CORR(current_price, rating)::numeric,
        4
    ) AS price_rating_correlation
FROM fact_product_observations
WHERE
    current_price IS NOT NULL
    AND rating IS NOT NULL;


-- 17. Latest observation for each product
WITH ranked_observations AS (
    SELECT
        f.*,
        ROW_NUMBER() OVER (
            PARTITION BY f.asin
            ORDER BY f.extraction_timestamp DESC
        ) AS row_number
    FROM fact_product_observations f
)

SELECT
    p.asin,
    p.product_title,
    p.brand,
    r.current_price,
    r.rating,
    r.review_count,
    r.price_category,
    r.is_prime,
    r.is_sponsored,
    r.extraction_timestamp
FROM ranked_observations r
JOIN dim_products p
    ON r.asin = p.asin
WHERE r.row_number = 1
ORDER BY
    p.brand,
    p.product_title;


-- 18. Latest extraction date and time
SELECT
    MAX(extraction_timestamp) AS latest_extraction_timestamp,
    MAX(extraction_date) AS latest_extraction_date
FROM fact_product_observations;


-- 19. ETL run history
SELECT
    run_id,
    pipeline_name,
    status,
    records_extracted,
    records_transformed,
    records_loaded,
    start_time,
    end_time,
    error_message
FROM etl_run_log
ORDER BY run_id DESC;


-- 20. ETL success summary
SELECT
    status,
    COUNT(*) AS run_count,
    SUM(records_extracted) AS total_records_extracted,
    SUM(records_transformed) AS total_records_transformed,
    SUM(records_loaded) AS total_records_loaded
FROM etl_run_log
GROUP BY status
ORDER BY status;