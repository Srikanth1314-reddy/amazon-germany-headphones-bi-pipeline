-- ============================================================
-- Project: Amazon Germany Wireless Headphones BI Pipeline
-- File: create_database.sql
-- Purpose: Create the PostgreSQL project database
-- ============================================================

CREATE DATABASE amazon_competitor_bi
    WITH
    OWNER = postgres
    ENCODING = 'UTF8'
    CONNECTION LIMIT = -1;