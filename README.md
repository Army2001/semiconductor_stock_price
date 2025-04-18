# Serverless Stock Data Pipeline with AWS

This project implements a **serverless data pipeline** using AWS services to ingest, transform, and visualize daily semiconductor stock data. It pulls data from the [Alpha Vantage API](https://www.alphavantage.co/) and enables querying through Athena and dashboarding with Grafana.

## Architecture Overview

- **Data Source**: Alpha Vantage API (`TIME_SERIES_DAILY`)
- **Storage**: Amazon S3
- **Compute**: AWS Lambda, AWS Glue
- **Orchestration**: AWS Glue Workflows, EventBridge
- **Analytics**: Amazon Athena
- **Visualization**: Grafana
- **Monitoring**: Amazon CloudWatch

# 

## Data Ingestion
1. S3 Bucket Setup
    - Created an S3 bucket to store raw and processed stock data.
    - Structured folders (e.g., /raw/, /query_results/) for organizing batches of files needed for Athena.

2. Alpha Vantage API Integration
    - API Endpoint:
    - https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=WCE5JCRHA0EIM2SC
    -   {symbol} is a variable used in Lambda function

3. AWS Lambda Function
    - Retrieves data from Alpha Vantage and stores CSV files in S3.
    - Configured IAM role with AmazonS3FullAccess and AmazonKinesisFirehoseFullAccess.
    - Introduced time.sleep(15) between API calls to comply with the free-tier limit of 5 calls/min.

4. EventBridge Trigger
    - Used Amazon EventBridge to trigger Lambda execution:
    - cron(0 22 ? * MON-FRI *)
    - Runs Monday–Friday at 10:00 PM UTC, after the U.S. stock market closes.

5. Kinesis Firehose
    Buffers and streams data to S3 when either:
        5 MiB of data is received, or
        60 seconds have passed.
    Configured to invoke the Lambda function and deliver streaming data into a nested S3 path.

6. CloudWatch Monitoring
    Configured a CloudWatch Alarm to detect and alert when the Lambda function fails (e.g., due to timeout or errors).

# Data Transformation
1. AWS Glue Crawler
    - Scans S3 folders and builds a data catalog for Athena.
    - IAM role includes AWSGlueConsoleFullAccess and AmazonAthenaFullAccess.

2. AWS Glue ETL Jobs
    - Written in Python with embedded SQL logic.
    - Tasks include:
        - Dropping old temporary tables
        - Creating new temporary tables
        - Running data quality checks
        - Publishing final tables in Parquet format

    -Jobs for Prod table is designed for incremental inserts:
        - If the table exists → append new data.
        - If not → create the table dynamically.

3. AWS Glue Workflows (write -> audit -> publish -> pattern)
    - Orchestrates ETL jobs using a defined sequence: on demand trigger -> Crawler: Load data from S3 -> Delete temporary tables -> Create temporary tables -> Data quality check ->   Publish final tables
    - Between each job, a trigger is added and logic configured to "Start after ANY watched event", so a job will only run if the previous job runs successfully
