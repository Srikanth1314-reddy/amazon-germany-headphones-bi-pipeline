import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL


# ============================================================
# 1. PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
LOG_DIR = PROJECT_ROOT / "logs"
ENV_FILE = PROJECT_ROOT / ".env"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

PIPELINE_NAME = "Amazon Germany Wireless Headphones ETL"

API_URL = (
    "https://api.amazonscraperapi.com"
    "/api/v1/amazon/search"
)

SEARCH_QUERY = "wireless headphones"
AMAZON_DOMAIN = "de"
SORT_BY = "best_match"


# ============================================================
# 2. LOGGING CONFIGURATION
# ============================================================

LOG_FILE = LOG_DIR / "etl_pipeline.log"

logging.basicConfig(
    level=logging.INFO,
    format=(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    ),
    handlers=[
        logging.FileHandler(
            LOG_FILE,
            encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("amazon_etl_pipeline")


# ============================================================
# 3. ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(ENV_FILE)

API_KEY = os.getenv("AMAZON_SCRAPER_API_KEY")

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def validate_environment_variables() -> None:
    """
    Confirm that all required credentials and configuration
    values exist before starting the pipeline.
    """
    required_values = {
        "AMAZON_SCRAPER_API_KEY": API_KEY,
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT,
        "DB_NAME": DB_NAME,
        "DB_USER": DB_USER,
        "DB_PASSWORD": DB_PASSWORD
    }

    missing_values = [
        key
        for key, value in required_values.items()
        if not value
    ]

    if missing_values:
        raise ValueError(
            "Missing required environment variables: "
            + ", ".join(missing_values)
        )


# ============================================================
# 4. DATABASE CONNECTION
# ============================================================

def get_database_engine() -> Engine:
    """
    Create and return a PostgreSQL SQLAlchemy engine.
    """
    database_url = URL.create(
        drivername="postgresql+psycopg2",
        username=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
        database=DB_NAME
    )

    return create_engine(
        database_url,
        pool_pre_ping=True
    )


def test_database_connection(engine: Engine) -> None:
    """
    Test the PostgreSQL connection before loading data.
    """
    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database();")
        ).scalar_one()

    logger.info(
        "PostgreSQL connection successful. Database: %s",
        database_name
    )


# ============================================================
# 5. EXTRACTION
# ============================================================

def extract_amazon_data() -> tuple[dict[str, Any], Path]:
    """
    Request Amazon Germany search data and save the raw JSON.
    """
    logger.info(
        "Starting API extraction for query: %s",
        SEARCH_QUERY
    )

    params = {
        "query": SEARCH_QUERY,
        "domain": AMAZON_DOMAIN,
        "sort_by": SORT_BY,
        "api_key": API_KEY
    }

    response = requests.get(
        API_URL,
        params=params,
        timeout=90
    )

    logger.info(
        "Amazon API response status: %s",
        response.status_code
    )

    response.raise_for_status()

    api_data = response.json()

    if not isinstance(api_data, dict):
        raise ValueError(
            "The API response is not a JSON dictionary."
        )

    product_list = api_data.get("products")

    if not isinstance(product_list, list):
        raise ValueError(
            "The API response does not contain "
            "a valid products list."
        )

    if not product_list:
        raise ValueError(
            "The Amazon API returned zero products."
        )

    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    raw_file_path = (
        RAW_DATA_DIR
        / f"amazon_wireless_headphones_de_{timestamp}.json"
    )

    with open(
        raw_file_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            api_data,
            file,
            indent=2,
            ensure_ascii=False
        )

    logger.info(
        "Raw JSON saved: %s",
        raw_file_path
    )

    logger.info(
        "Products extracted: %s",
        len(product_list)
    )

    return api_data, raw_file_path


# ============================================================
# 6. TRANSFORMATION HELPERS
# ============================================================

def clean_numeric_value(value: Any) -> float:
    """
    Convert text-based prices, ratings, and counts into numbers.
    """
    if pd.isna(value):
        return np.nan

    if isinstance(
        value,
        (
            int,
            float,
            np.integer,
            np.floating
        )
    ):
        return float(value)

    value_text = str(value).strip()

    value_text = (
        value_text
        .replace("\xa0", "")
        .replace("€", "")
        .replace("$", "")
        .replace("£", "")
        .replace(" ", "")
    )

    number_match = re.search(
        r"-?\d+(?:[.,]\d+)?",
        value_text
    )

    if not number_match:
        return np.nan

    number_text = number_match.group()

    if "," in number_text and "." in number_text:
        if (
            number_text.rfind(",")
            > number_text.rfind(".")
        ):
            number_text = (
                number_text
                .replace(".", "")
                .replace(",", ".")
            )
        else:
            number_text = number_text.replace(
                ",",
                ""
            )

    elif "," in number_text:
        decimal_part = number_text.split(",")[-1]

        if len(decimal_part) == 2:
            number_text = number_text.replace(
                ",",
                "."
            )
        else:
            number_text = number_text.replace(
                ",",
                ""
            )

    return pd.to_numeric(
        number_text,
        errors="coerce"
    )


def clean_boolean(value: Any) -> bool:
    """
    Standardise different Boolean representations.
    """
    if pd.isna(value):
        return False

    if isinstance(value, bool):
        return value

    value_text = str(value).strip().lower()

    return value_text in {
        "true",
        "1",
        "yes",
        "y",
        "prime",
        "sponsored"
    }


def extract_brand(product_title: str) -> str:
    """
    Extract a known brand from the product title.
    """
    known_brands = [
        "JBL",
        "Sony",
        "Soundcore",
        "Anker",
        "Bose",
        "Sennheiser",
        "Apple",
        "Beats",
        "Samsung",
        "Philips",
        "Logitech",
        "Jabra",
        "Skullcandy",
        "Marshall",
        "Xiaomi",
        "Huawei",
        "Fachixy",
        "ZZU"
    ]

    if pd.isna(product_title):
        return "Unknown"

    for brand in known_brands:
        if re.search(
            rf"\b{re.escape(brand)}\b",
            str(product_title),
            flags=re.IGNORECASE
        ):
            if brand == "JBL":
                return "JBL"

            if brand == "ZZU":
                return "ZZU"

            return brand.title()

    return "Unknown"


# ============================================================
# 7. TRANSFORMATION
# ============================================================

def transform_amazon_data(
    api_data: dict[str, Any]
) -> tuple[pd.DataFrame, Path]:
    """
    Clean the API product data and save a processed CSV file.
    """
    logger.info("Starting transformation stage.")

    product_list = api_data.get("products", [])

    raw_df = pd.json_normalize(product_list)

    required_source_columns = [
        "asin",
        "title",
        "price",
        "rating",
        "reviews_count",
        "url",
        "image",
        "is_sponsored",
        "is_prime"
    ]

    missing_source_columns = [
        column
        for column in required_source_columns
        if column not in raw_df.columns
    ]

    if missing_source_columns:
        raise ValueError(
            "Required API fields are missing: "
            + ", ".join(missing_source_columns)
        )

    transformed_df = pd.DataFrame({
        "asin": raw_df["asin"],
        "product_title": raw_df["title"],
        "current_price": (
            raw_df["price"]
            .apply(clean_numeric_value)
        ),
        "original_price": np.nan,
        "currency": "EUR",
        "rating": (
            raw_df["rating"]
            .apply(clean_numeric_value)
        ),
        "review_count": (
            raw_df["reviews_count"]
            .apply(clean_numeric_value)
        ),
        "search_position": np.nan,
        "is_prime": (
            raw_df["is_prime"]
            .apply(clean_boolean)
        ),
        "is_sponsored": (
            raw_df["is_sponsored"]
            .apply(clean_boolean)
        ),
        "marketplace": "Amazon Germany",
        "search_query": SEARCH_QUERY,
        "product_url": raw_df["url"],
        "image_url": raw_df["image"]
    })

    transformed_df["asin"] = (
        transformed_df["asin"]
        .astype("string")
        .str.strip()
    )

    transformed_df["product_title"] = (
        transformed_df["product_title"]
        .astype("string")
        .str.replace(
            r"\s+",
            " ",
            regex=True
        )
        .str.strip()
    )

    rows_before_cleaning = len(transformed_df)

    transformed_df = transformed_df[
        transformed_df["asin"].notna()
        & transformed_df["product_title"].notna()
        & transformed_df["current_price"].notna()
    ].copy()

    transformed_df["duplicate_key"] = (
        transformed_df["asin"]
        .fillna(
            transformed_df["product_title"]
        )
    )

    transformed_df = (
        transformed_df
        .drop_duplicates(
            subset=["duplicate_key"],
            keep="first"
        )
        .copy()
    )

    transformed_df["brand"] = (
        transformed_df["product_title"]
        .apply(extract_brand)
    )

    transformed_df["discount_percentage"] = 0.0

    transformed_df["price_category"] = pd.cut(
        transformed_df["current_price"],
        bins=[
            -np.inf,
            30,
            60,
            120,
            np.inf
        ],
        labels=[
            "Budget",
            "Mid-range",
            "Premium",
            "Luxury"
        ]
    ).astype("string")

    transformed_df["rating_category"] = pd.cut(
        transformed_df["rating"],
        bins=[
            -np.inf,
            3.5,
            4.0,
            4.5,
            5.0
        ],
        labels=[
            "Low",
            "Average",
            "Good",
            "Excellent"
        ],
        include_lowest=True
    ).astype("string")

    transformed_df["review_count"] = (
        transformed_df["review_count"]
        .round()
        .astype("Int64")
    )

    transformed_df["search_position"] = (
        transformed_df["search_position"]
        .astype("Int64")
    )

    extraction_timestamp = datetime.now()

    transformed_df["extraction_timestamp"] = (
        extraction_timestamp
    )

    transformed_df["extraction_date"] = (
        extraction_timestamp.date()
    )

    transformed_df = transformed_df.drop(
        columns=["duplicate_key"],
        errors="ignore"
    )

    final_columns = [
        "asin",
        "product_title",
        "brand",
        "current_price",
        "original_price",
        "currency",
        "discount_percentage",
        "price_category",
        "rating",
        "rating_category",
        "review_count",
        "search_position",
        "is_prime",
        "is_sponsored",
        "marketplace",
        "search_query",
        "product_url",
        "image_url",
        "extraction_date",
        "extraction_timestamp"
    ]

    transformed_df = transformed_df[
        final_columns
    ].copy()

    validate_transformed_data(
        transformed_df
    )

    processed_file_path = (
        PROCESSED_DATA_DIR
        / "amazon_wireless_headphones_cleaned.csv"
    )

    transformed_df.to_csv(
        processed_file_path,
        index=False,
        encoding="utf-8-sig"
    )

    logger.info(
        "Rows before cleaning: %s",
        rows_before_cleaning
    )

    logger.info(
        "Rows after transformation: %s",
        len(transformed_df)
    )

    logger.info(
        "Processed CSV saved: %s",
        processed_file_path
    )

    return transformed_df, processed_file_path


def validate_transformed_data(
    dataframe: pd.DataFrame
) -> None:
    """
    Run key data-quality checks before database loading.
    """
    if dataframe.empty:
        raise ValueError(
            "The transformed dataset is empty."
        )

    required_non_null_columns = [
        "asin",
        "product_title",
        "brand",
        "current_price",
        "rating",
        "review_count",
        "extraction_date",
        "extraction_timestamp"
    ]

    missing_counts = (
        dataframe[
            required_non_null_columns
        ]
        .isna()
        .sum()
    )

    if missing_counts.sum() > 0:
        raise ValueError(
            "Required transformed fields contain "
            f"missing values: {missing_counts.to_dict()}"
        )

    if (
        dataframe["current_price"] < 0
    ).any():
        raise ValueError(
            "Negative prices were detected."
        )

    if (
        (dataframe["rating"] < 0)
        | (dataframe["rating"] > 5)
    ).any():
        raise ValueError(
            "Ratings outside the 0–5 range were detected."
        )

    if dataframe["asin"].duplicated().any():
        raise ValueError(
            "Duplicate ASIN values remain "
            "after transformation."
        )

    logger.info(
        "Data-quality validation passed."
    )


# ============================================================
# 8. DATABASE LOADING
# ============================================================

DIMENSION_UPSERT_SQL = text("""
    INSERT INTO dim_products (
        asin,
        product_title,
        brand,
        product_url,
        image_url,
        marketplace,
        search_query
    )
    VALUES (
        :asin,
        :product_title,
        :brand,
        :product_url,
        :image_url,
        :marketplace,
        :search_query
    )
    ON CONFLICT (asin)
    DO UPDATE SET
        product_title = EXCLUDED.product_title,
        brand = EXCLUDED.brand,
        product_url = EXCLUDED.product_url,
        image_url = EXCLUDED.image_url,
        marketplace = EXCLUDED.marketplace,
        search_query = EXCLUDED.search_query,
        updated_at = CURRENT_TIMESTAMP;
""")


FACT_INSERT_SQL = text("""
    INSERT INTO fact_product_observations (
        asin,
        current_price,
        original_price,
        currency,
        discount_percentage,
        price_category,
        rating,
        rating_category,
        review_count,
        search_position,
        is_prime,
        is_sponsored,
        extraction_date,
        extraction_timestamp
    )
    VALUES (
        :asin,
        :current_price,
        :original_price,
        :currency,
        :discount_percentage,
        :price_category,
        :rating,
        :rating_category,
        :review_count,
        :search_position,
        :is_prime,
        :is_sponsored,
        :extraction_date,
        :extraction_timestamp
    )
    ON CONFLICT (
        asin,
        extraction_timestamp
    )
    DO NOTHING;
""")


ETL_LOG_INSERT_SQL = text("""
    INSERT INTO etl_run_log (
        pipeline_name,
        start_time,
        end_time,
        status,
        records_extracted,
        records_transformed,
        records_loaded,
        raw_file_path,
        processed_file_path,
        error_message
    )
    VALUES (
        :pipeline_name,
        :start_time,
        :end_time,
        :status,
        :records_extracted,
        :records_transformed,
        :records_loaded,
        :raw_file_path,
        :processed_file_path,
        :error_message
    );
""")


def load_data_to_postgresql(
    engine: Engine,
    dataframe: pd.DataFrame
) -> int:
    """
    Upsert product records and insert observation records.
    """
    logger.info(
        "Starting PostgreSQL loading stage."
    )

    dim_products_df = (
        dataframe[
            [
                "asin",
                "product_title",
                "brand",
                "product_url",
                "image_url",
                "marketplace",
                "search_query"
            ]
        ]
        .drop_duplicates(
            subset=["asin"]
        )
        .copy()
    )

    fact_observations_df = dataframe[
        [
            "asin",
            "current_price",
            "original_price",
            "currency",
            "discount_percentage",
            "price_category",
            "rating",
            "rating_category",
            "review_count",
            "search_position",
            "is_prime",
            "is_sponsored",
            "extraction_date",
            "extraction_timestamp"
        ]
    ].copy()

    dim_records = (
        dim_products_df
        .astype(object)
        .where(
            pd.notna(dim_products_df),
            None
        )
        .to_dict(orient="records")
    )

    fact_records = (
        fact_observations_df
        .astype(object)
        .where(
            pd.notna(fact_observations_df),
            None
        )
        .to_dict(orient="records")
    )

    with engine.begin() as connection:
        connection.execute(
            DIMENSION_UPSERT_SQL,
            dim_records
        )

        fact_result = connection.execute(
            FACT_INSERT_SQL,
            fact_records
        )

    inserted_fact_rows = fact_result.rowcount

    logger.info(
        "Dimension records inserted or updated: %s",
        len(dim_records)
    )

    logger.info(
        "Fact observations inserted: %s",
        inserted_fact_rows
    )

    return inserted_fact_rows


def insert_etl_log(
    engine: Engine,
    *,
    start_time: datetime,
    end_time: datetime,
    status: str,
    records_extracted: int,
    records_transformed: int,
    records_loaded: int,
    raw_file_path: Path | None,
    processed_file_path: Path | None,
    error_message: str | None
) -> None:
    """
    Insert one ETL execution record into PostgreSQL.
    """
    log_record = {
        "pipeline_name": PIPELINE_NAME,
        "start_time": start_time,
        "end_time": end_time,
        "status": status,
        "records_extracted": records_extracted,
        "records_transformed": records_transformed,
        "records_loaded": records_loaded,
        "raw_file_path": (
            str(raw_file_path)
            if raw_file_path
            else None
        ),
        "processed_file_path": (
            str(processed_file_path)
            if processed_file_path
            else None
        ),
        "error_message": error_message
    }

    with engine.begin() as connection:
        connection.execute(
            ETL_LOG_INSERT_SQL,
            log_record
        )


# ============================================================
# 9. PIPELINE EXECUTION
# ============================================================

def run_pipeline() -> None:
    """
    Execute the complete ETL pipeline.
    """
    start_time = datetime.now()

    raw_file_path = None
    processed_file_path = None

    records_extracted = 0
    records_transformed = 0
    records_loaded = 0

    engine = None

    logger.info("=" * 60)
    logger.info("ETL pipeline started.")
    logger.info("=" * 60)

    try:
        validate_environment_variables()

        engine = get_database_engine()

        test_database_connection(engine)

        api_data, raw_file_path = (
            extract_amazon_data()
        )

        records_extracted = len(
            api_data.get("products", [])
        )

        transformed_df, processed_file_path = (
            transform_amazon_data(api_data)
        )

        records_transformed = len(
            transformed_df
        )

        records_loaded = (
            load_data_to_postgresql(
                engine,
                transformed_df
            )
        )

        end_time = datetime.now()

        insert_etl_log(
            engine,
            start_time=start_time,
            end_time=end_time,
            status="SUCCESS",
            records_extracted=records_extracted,
            records_transformed=records_transformed,
            records_loaded=records_loaded,
            raw_file_path=raw_file_path,
            processed_file_path=processed_file_path,
            error_message=None
        )

        logger.info(
            "ETL pipeline completed successfully."
        )

        logger.info(
            "Extracted: %s | Transformed: %s | Loaded: %s",
            records_extracted,
            records_transformed,
            records_loaded
        )

    except Exception as error:
        end_time = datetime.now()

        logger.exception(
            "ETL pipeline failed: %s",
            error
        )

        if engine is not None:
            try:
                insert_etl_log(
                    engine,
                    start_time=start_time,
                    end_time=end_time,
                    status="FAILED",
                    records_extracted=records_extracted,
                    records_transformed=records_transformed,
                    records_loaded=records_loaded,
                    raw_file_path=raw_file_path,
                    processed_file_path=processed_file_path,
                    error_message=str(error)[:5000]
                )
            except Exception as log_error:
                logger.exception(
                    "Failed to insert ETL failure log: %s",
                    log_error
                )

        raise

    finally:
        if engine is not None:
            engine.dispose()

        logger.info("=" * 60)
        logger.info("ETL pipeline execution ended.")
        logger.info("=" * 60)


if __name__ == "__main__":
    run_pipeline()