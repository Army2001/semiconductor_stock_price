# Semiconductor Stock Data Pipeline with AWS

This project implements a **serverless data pipeline** using AWS services to ingest, transform, and visualize daily semiconductor stock data. It pulls data from the [Alpha Vantage API](https://www.alphavantage.co/) and enables querying through Athena and dashboarding with Grafana.

## Architecture Overview

- **Data Source**: Alpha Vantage API (`TIME_SERIES_DAILY`)
- **Storage**: Amazon S3
- **Compute**: AWS Lambda, AWS Glue
- **Orchestration**: AWS Glue Workflows, EventBridge
- **Analytics**: Amazon Athena
- **Visualization**: Grafana
- **Monitoring**: Amazon CloudWatch

# ![AWS Database Architecture](https://github.com/user-attachments/assets/d14f3fff-c0d6-4888-84a2-4299d0181ac1)

## Data Ingestion
1. S3 Bucket Setup
    - Created an S3 bucket to store raw and processed stock data.
    - Structured folders (e.g., /army-sc-bucket/, /army-sc-query-results-bucket/) for organizing batches of files needed for Athena.

2. Alpha Vantage API Integration
    - API Endpoint:
    - https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=WCE5JCRHA0EIM2SC
    -   {symbol} is a variable used in Lambda function

3. AWS Lambda Function

### Historical Backfill Function

#### `historical_stock_price_lambda`
- One-time Lambda function used to **retrieve historical stock data** from Alpha Vantage.
- Converts the data into CSV format and saves it into the appropriate S3 path (`/army-sc-bucket/`).
- Used to seed the dataset before setting up the automated daily ingestion pipeline.

## Daily ingestion
- Retrieves **daily data** from Alpha Vantage and stores JSON files in S3.
- Configured IAM role with AmazonS3FullAccess and AmazonKinesisFirehoseFullAccess.
- Introduced time.sleep(15) between API calls to comply with the free-tier limit of 5 calls/min.

4. EventBridge Trigger
    - Used Amazon EventBridge to trigger Lambda execution:
     ```
     cron(0 22 ? * MON-FRI *)
     ```
    - Runs Monday–Friday at 10:00 PM UTC, after the U.S. stock market closes.

5. Kinesis Firehose
    Buffers and streams data to S3 when either:
        5 MiB of data is received, or
        60 seconds have passed.
    Configured to invoke the Lambda function and deliver streaming data into a nested S3 path.

6. CloudWatch Monitoring
    Configured a CloudWatch Alarm to detect and alert when the Lambda function fails (e.g., due to timeout or errors).

<img width="758" alt="CloudWatch alarm" src="https://github.com/user-attachments/assets/c83693c1-531d-4798-91dd-d0683ddb39aa" />

# Data Transformation
1. AWS Glue Crawler
    - Scans S3 folders and builds a data catalog for Athena.
    - IAM role includes AWSGlueConsoleFullAccess and AmazonAthenaFullAccess.

2. AWS Glue ETL Jobs
    - Written in Python with embedded SQL logic.
    - Tasks include:
        - Dropping old temporary tables
        - Creating new temporary tables -> table stored in parquet bucket and output into query results bucket
        - Running data quality checks on parquet table
        - Publishing final tables in Parquet format -> table published in proc bucket

    -Jobs for Prod table is designed for **incremental inserts**:
        - If the table exists → append new data.
        - If not → create the table dynamically.

3. AWS Glue Workflows (write -> audit -> publish -> pattern)
    - Orchestrates ETL jobs using a defined sequence: on demand trigger -> Crawler: Load data from S3 -> Delete temporary tables -> Create temporary tables -> Data quality check ->   Publish final tables
    - Between each job, a trigger is added and logic configured to "Start after ANY watched event", so a job will only run if the previous job runs successfully
  
<img width="739" alt="workflow 1" src="https://github.com/user-attachments/assets/90cfa289-37cd-478b-af7a-3b7862e24116" />
<img width="647" alt="workflow 2" src="https://github.com/user-attachments/assets/812e49ea-9d65-46d2-babf-f1efd567b784" />
  
# Data Visualization
- Grafana Setup
    - Created IAM user with:
        - AmazonAthenaFullAccess
        - AmazonS3FullAccess
    - Generated access keys for Grafana.

- In Grafana:
    - Installed Amazon Athena plugin.
    - Configured access/secret keys and AWS region.
    - Set query output location to the correct S3 path.
    - Built dashboards to visualize stock trends using Athena queries.
 
# Average Price (last 90 days)
<img width="812" alt="Average Price" src="https://github.com/user-attachments/assets/25ca6827-650d-4703-b304-a3241eaee83e" />

# Daily Return
<img width="812" alt="Daily Return" src="https://github.com/user-attachments/assets/55c21be9-db58-44bc-9eb7-90c69caa2167" />

# Volatility
<img width="814" alt="Volatility" src="https://github.com/user-attachments/assets/b012a8a9-4730-4af9-a8ae-0262fc22e938" />

### Analysis & Observations

- **Average Price:**
  - The average price across tracked stocks **reached a low on 4/6–4/8**.
  - This was followed by a notable **rebound on 4/9**, suggesting a possible market correction or reaction to external events.

- **Daily Return:**
  - Daily return metrics hit a **trough on 4/7** and then **peaked on 4/8**, showing a sharp swing in sentiment or value.

- **Volatility:**
  - Volatility spiked **on 4/9**, indicating heightened uncertainty or rapid market movement during that time.

- **Correlated Movement Across Top Stocks:**
  - The top 10 stocks by market share demonstrated nearly identical movement patterns, implying a systemic or macro-level influence.
  - This alignment across major stocks supports the deduction that a broad market catalyst occurred.

- **Market Impact Hypothesis:**
  - The timing aligns with the **tariff announcement on 4/5**, which likely caused:
    - Market uncertainty leading into the weekend
    - A price drop and return trough on 4/8 (first trading day after)
    - A volatility spike and price rebound on 4/9, as investors reacted
 
##  Troubleshooting & Testing

### Lambda Development
- Developed and tested Lambda functions locally using Visual Studio Code.
- Added `print()` statements at key stages (e.g., after API call, before writing to S3) to validate data retrieval and process flow.

### CloudWatch Logs
- Monitored execution and debugging information via CloudWatch Logs tied to each Lambda invocation.

### SQL Testing for Glue Jobs
- Validated transformation SQL queries in Amazon Athena using test data before embedding them into AWS Glue job scripts.

---

##  Design Considerations

### Execution Timing
- Configured EventBridge rule using the cron expression:

     ```
     cron(0 22 ? * MON-FRI *)
     ```

- Runs ingestion Lambda only on **weekdays at 22:00 UTC**, aligning with U.S. market close times.

### API Rate Management
- Implemented `time.sleep(15)` in Lambda to delay between each stock symbol API request.
- This stays within Alpha Vantage’s free-tier limit of 5 calls per minute.

### ETL Publishing Strategy
- Glue job logic includes incremental insert behavior:
- If the destination table exists, insert new records.
- If the table does not exist, create it.
- Ensures daily updates without duplicating tables.

---

##  Future Improvements

### Workflow Scheduling
- Current Glue workflows are manually triggered.
- Could be improved by configuring automated scheduling to match the weekday ingestion schedule.

### Additional Calculated Columns

Current transformations:
- `daily_return = Close - Open`
- `avg_price = (Open + High + Low + Close) / 4`
- `volatility = 0.5 * POWER(LN(high / low), 2) - (2 * LN(2) - 1) * POWER(LN(close / open), 2)`

Planned enhancements:
| Column Name          | Description                                                  |
|----------------------|--------------------------------------------------------------|
| `price_change_pct`   | Percent change from previous day's close                     |
| `rolling_avg_5d`     | 5-day moving average of close price                          |
| `volume_surge_ratio` | Ratio of current volume to 7-day average volume              |
| `candle_type`        | Candlestick pattern classification (e.g., doji, hammer)      |
| `is_market_up`       | Boolean indicating if stock closed higher than it opened      

### Ingest data for stocks outside of US market
- Multinational comparison for semiconductor stock market
- Set up EventTrigger to run it multiple times a day to accommodate different stock market hours

