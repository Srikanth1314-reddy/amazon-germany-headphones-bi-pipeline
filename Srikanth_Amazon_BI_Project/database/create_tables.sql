-- ============================================================
-- Project: Amazon Germany Wireless Headphones BI Pipeline
-- File: create_tables.sql
-- Database: amazon_competitor_bi
-- Purpose: Create database tables, constraints, and indexes
-- ============================================================


-- ============================================================
-- 1. Product Dimension Table
-- Stores stable descriptive information about each product
-- ============================================================

CREATE TABLE IF NOT EXISTS dim_products (
    asin VARCHAR(20) PRIMARY KEY,
    product_title TEXT NOT NULL,
    brand VARCHAR(100) NOT NULL DEFAULT 'Unknown',
    product_url TEXT,
    image_url TEXT,
    marketplace VARCHAR(100) NOT NULL,
    search_query VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- 2. Product Observation Fact Table
-- Stores changing price, rating, and listing information
-- ============================================================

CREATE TABLE IF NOT EXISTS fact_product_observations (
    observation_id BIGSERIAL PRIMARY KEY,

    asin VARCHAR(20) NOT NULL,

    current_price NUMERIC(10, 2) NOT NULL,

    original_price NUMERIC(10, 2),

    currency VARCHAR(10) NOT NULL DEFAULT 'EUR',

    discount_percentage NUMERIC(6, 2)
        NOT NULL DEFAULT 0,

    price_category VARCHAR(50),

    rating NUMERIC(3, 2),

    rating_category VARCHAR(50),

    review_count INTEGER,

    search_position INTEGER,

    is_prime BOOLEAN NOT NULL DEFAULT FALSE,

    is_sponsored BOOLEAN NOT NULL DEFAULT FALSE,

    extraction_date DATE NOT NULL,

    extraction_timestamp TIMESTAMP NOT NULL,


    CONSTRAINT fk_product_observation_asin
        FOREIGN KEY (asin)
        REFERENCES dim_products(asin)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,


    CONSTRAINT chk_current_price_non_negative
        CHECK (
            current_price >= 0
        ),


    CONSTRAINT chk_original_price_non_negative
        CHECK (
            original_price IS NULL
            OR original_price >= 0
        ),


    CONSTRAINT chk_discount_percentage_range
        CHECK (
            discount_percentage >= 0
            AND discount_percentage <= 100
        ),


    CONSTRAINT chk_rating_range
        CHECK (
            rating IS NULL
            OR rating BETWEEN 0 AND 5
        ),


    CONSTRAINT chk_review_count_non_negative
        CHECK (
            review_count IS NULL
            OR review_count >= 0
        ),


    CONSTRAINT chk_search_position_positive
        CHECK (
            search_position IS NULL
            OR search_position > 0
        )
);


-- ============================================================
-- 3. ETL Run Log Table
-- Stores information about every pipeline execution
-- ============================================================

CREATE TABLE IF NOT EXISTS etl_run_log (
    run_id BIGSERIAL PRIMARY KEY,

    pipeline_name VARCHAR(150) NOT NULL,

    start_time TIMESTAMP NOT NULL,

    end_time TIMESTAMP,

    status VARCHAR(30) NOT NULL,

    records_extracted INTEGER
        NOT NULL DEFAULT 0,

    records_transformed INTEGER
        NOT NULL DEFAULT 0,

    records_loaded INTEGER
        NOT NULL DEFAULT 0,

    raw_file_path TEXT,

    processed_file_path TEXT,

    error_message TEXT,

    created_at TIMESTAMP
        NOT NULL DEFAULT CURRENT_TIMESTAMP,


    CONSTRAINT chk_etl_status
        CHECK (
            status IN (
                'STARTED',
                'SUCCESS',
                'FAILED',
                'PARTIAL'
            )
        ),


    CONSTRAINT chk_etl_record_counts
        CHECK (
            records_extracted >= 0
            AND records_transformed >= 0
            AND records_loaded >= 0
        ),


    CONSTRAINT chk_etl_end_time
        CHECK (
            end_time IS NULL
            OR end_time >= start_time
        )
);


-- ============================================================
-- 4. Indexes
-- Improve SQL analysis and Power BI performance
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_products_brand
    ON dim_products(brand);


CREATE INDEX IF NOT EXISTS idx_products_marketplace
    ON dim_products(marketplace);


CREATE INDEX IF NOT EXISTS idx_observations_asin
    ON fact_product_observations(asin);


CREATE INDEX IF NOT EXISTS idx_observations_extraction_date
    ON fact_product_observations(extraction_date);


CREATE INDEX IF NOT EXISTS idx_observations_extraction_timestamp
    ON fact_product_observations(extraction_timestamp);


CREATE INDEX IF NOT EXISTS idx_observations_price_category
    ON fact_product_observations(price_category);


CREATE INDEX IF NOT EXISTS idx_observations_rating_category
    ON fact_product_observations(rating_category);


CREATE INDEX IF NOT EXISTS idx_observations_rating
    ON fact_product_observations(rating);


CREATE INDEX IF NOT EXISTS idx_observations_prime
    ON fact_product_observations(is_prime);


CREATE INDEX IF NOT EXISTS idx_observations_sponsored
    ON fact_product_observations(is_sponsored);


CREATE INDEX IF NOT EXISTS idx_etl_run_status
    ON etl_run_log(status);


CREATE INDEX IF NOT EXISTS idx_etl_run_start_time
    ON etl_run_log(start_time);


-- ============================================================
-- 5. Duplicate Prevention
-- Prevent the same product observation from being inserted twice
-- for the same extraction timestamp
-- ============================================================

CREATE UNIQUE INDEX IF NOT EXISTS
    uq_product_observation_timestamp
ON fact_product_observations (
    asin,
    extraction_timestamp
);
