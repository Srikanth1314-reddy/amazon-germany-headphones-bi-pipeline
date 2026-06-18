# Data Dictionary

## Table: `dim_products`

This dimension table stores stable descriptive information about each Amazon product.

| Column          | Data type    | Description                                                  |
| --------------- | ------------ | ------------------------------------------------------------ |
| `asin`          | VARCHAR(20)  | Unique Amazon Standard Identification Number and primary key |
| `product_title` | TEXT         | Full Amazon product title                                    |
| `brand`         | VARCHAR(100) | Detected or extracted product brand                          |
| `product_url`   | TEXT         | Link to the Amazon product page                              |
| `image_url`     | TEXT         | Link to the main product image                               |
| `marketplace`   | VARCHAR(100) | Amazon marketplace used for extraction                       |
| `search_query`  | VARCHAR(255) | Search phrase used for the API request                       |
| `created_at`    | TIMESTAMP    | Date and time when the product was first inserted            |
| `updated_at`    | TIMESTAMP    | Date and time when the product record was last updated       |

## Table: `fact_product_observations`

This fact table stores changing product values collected during each pipeline execution.

| Column                 | Data type     | Description                                    |
| ---------------------- | ------------- | ---------------------------------------------- |
| `observation_id`       | BIGSERIAL     | Unique identifier for each observation         |
| `asin`                 | VARCHAR(20)   | Foreign key linking to `dim_products`          |
| `current_price`        | NUMERIC(10,2) | Current listed product price                   |
| `original_price`       | NUMERIC(10,2) | Original or previous price, when available     |
| `currency`             | VARCHAR(10)   | Currency used for the product price            |
| `discount_percentage`  | NUMERIC(6,2)  | Calculated discount percentage                 |
| `price_category`       | VARCHAR(50)   | Budget, Mid-range, Premium or Luxury           |
| `rating`               | NUMERIC(3,2)  | Average product rating                         |
| `rating_category`      | VARCHAR(50)   | Low, Average, Good or Excellent                |
| `review_count`         | INTEGER       | Number of customer reviews                     |
| `search_position`      | INTEGER       | Product search position, when available        |
| `is_prime`             | BOOLEAN       | Indicates whether the product has Prime status |
| `is_sponsored`         | BOOLEAN       | Indicates whether the listing is sponsored     |
| `extraction_date`      | DATE          | Date when the product data was collected       |
| `extraction_timestamp` | TIMESTAMP     | Exact date and time of extraction              |

## Table: `etl_run_log`

This table records the execution status of every automated ETL pipeline run.

| Column                | Data type    | Description                                |
| --------------------- | ------------ | ------------------------------------------ |
| `run_id`              | BIGSERIAL    | Unique pipeline-run identifier             |
| `pipeline_name`       | VARCHAR(150) | Name of the ETL pipeline                   |
| `start_time`          | TIMESTAMP    | Pipeline start time                        |
| `end_time`            | TIMESTAMP    | Pipeline completion or failure time        |
| `status`              | VARCHAR(30)  | STARTED, SUCCESS, FAILED or PARTIAL        |
| `records_extracted`   | INTEGER      | Number of API records extracted            |
| `records_transformed` | INTEGER      | Number of cleaned records produced         |
| `records_loaded`      | INTEGER      | Number of observation records inserted     |
| `raw_file_path`       | TEXT         | Location of the saved raw JSON file        |
| `processed_file_path` | TEXT         | Location of the processed CSV file         |
| `error_message`       | TEXT         | Error details when a run fails             |
| `created_at`          | TIMESTAMP    | Date and time when the log row was created |

## Calculated Analytical Fields

### Price category

| Category  |       Price range |
| --------- | ----------------: |
| Budget    |         Up to €30 |
| Mid-range |  Above €30 to €60 |
| Premium   | Above €60 to €120 |
| Luxury    |        Above €120 |

### Rating category

| Category  |     Rating range |
| --------- | ---------------: |
| Low       |        Up to 3.5 |
| Average   | Above 3.5 to 4.0 |
| Good      | Above 4.0 to 4.5 |
| Excellent | Above 4.5 to 5.0 |

### Value score

The exploratory value score combines rating, review volume and current price:

`rating × natural logarithm(review count + 1) ÷ current price`

A higher result suggests stronger rating and review performance relative to price. It is a project-created analytical measure and not an official Amazon metric.
