\# Data Dictionary



\## Table: `dim\_products`



This dimension table stores stable descriptive information about each Amazon product.



| Column          | Data type    | Description                                                  |

| --------------- | ------------ | ------------------------------------------------------------ |

| `asin`          | VARCHAR(20)  | Unique Amazon Standard Identification Number and primary key |

| `product\_title` | TEXT         | Full Amazon product title                                    |

| `brand`         | VARCHAR(100) | Detected or extracted product brand                          |

| `product\_url`   | TEXT         | Link to the Amazon product page                              |

| `image\_url`     | TEXT         | Link to the main product image                               |

| `marketplace`   | VARCHAR(100) | Amazon marketplace used for extraction                       |

| `search\_query`  | VARCHAR(255) | Search phrase used for the API request                       |

| `created\_at`    | TIMESTAMP    | Date and time when the product was first inserted            |

| `updated\_at`    | TIMESTAMP    | Date and time when the product record was last updated       |



\## Table: `fact\_product\_observations`



This fact table stores changing product values collected during each pipeline execution.



| Column                 | Data type     | Description                                    |

| ---------------------- | ------------- | ---------------------------------------------- |

| `observation\_id`       | BIGSERIAL     | Unique identifier for each observation         |

| `asin`                 | VARCHAR(20)   | Foreign key linking to `dim\_products`          |

| `current\_price`        | NUMERIC(10,2) | Current listed product price                   |

| `original\_price`       | NUMERIC(10,2) | Original or previous price, when available     |

| `currency`             | VARCHAR(10)   | Currency used for the product price            |

| `discount\_percentage`  | NUMERIC(6,2)  | Calculated discount percentage                 |

| `price\_category`       | VARCHAR(50)   | Budget, Mid-range, Premium or Luxury           |

| `rating`               | NUMERIC(3,2)  | Average product rating                         |

| `rating\_category`      | VARCHAR(50)   | Low, Average, Good or Excellent                |

| `review\_count`         | INTEGER       | Number of customer reviews                     |

| `search\_position`      | INTEGER       | Product search position, when available        |

| `is\_prime`             | BOOLEAN       | Indicates whether the product has Prime status |

| `is\_sponsored`         | BOOLEAN       | Indicates whether the listing is sponsored     |

| `extraction\_date`      | DATE          | Date when the product data was collected       |

| `extraction\_timestamp` | TIMESTAMP     | Exact date and time of extraction              |



\## Table: `etl\_run\_log`



This table records the execution status of every automated ETL pipeline run.



| Column                | Data type    | Description                                |

| --------------------- | ------------ | ------------------------------------------ |

| `run\_id`              | BIGSERIAL    | Unique pipeline-run identifier             |

| `pipeline\_name`       | VARCHAR(150) | Name of the ETL pipeline                   |

| `start\_time`          | TIMESTAMP    | Pipeline start time                        |

| `end\_time`            | TIMESTAMP    | Pipeline completion or failure time        |

| `status`              | VARCHAR(30)  | STARTED, SUCCESS, FAILED or PARTIAL        |

| `records\_extracted`   | INTEGER      | Number of API records extracted            |

| `records\_transformed` | INTEGER      | Number of cleaned records produced         |

| `records\_loaded`      | INTEGER      | Number of observation records inserted     |

| `raw\_file\_path`       | TEXT         | Location of the saved raw JSON file        |

| `processed\_file\_path` | TEXT         | Location of the processed CSV file         |

| `error\_message`       | TEXT         | Error details when a run fails             |

| `created\_at`          | TIMESTAMP    | Date and time when the log row was created |



\## Calculated Analytical Fields



\### Price category



| Category  |       Price range |

| --------- | ----------------: |

| Budget    |         Up to €30 |

| Mid-range |  Above €30 to €60 |

| Premium   | Above €60 to €120 |

| Luxury    |        Above €120 |



\### Rating category



| Category  |     Rating range |

| --------- | ---------------: |

| Low       |        Up to 3.5 |

| Average   | Above 3.5 to 4.0 |

| Good      | Above 4.0 to 4.5 |

| Excellent | Above 4.5 to 5.0 |



\### Value score



The exploratory value score combines rating, review volume and current price:



`rating × natural logarithm(review count + 1) ÷ current price`



A higher result suggests stronger rating and review performance relative to price. It is a project-created analytical measure and not an official Amazon metric.



