import sys
import boto3
from datetime import datetime
import pytz

QUERY_RESULTS_BUCKET = 's3://army-sc-query-results-bucket/'
MY_DATABASE = 'semiconductorstock'
SOURCE_PARQUET_TABLE_NAME = 'semiconductor_stock_price'
NEW_PROD_PARQUET_TABLE_NAME = 'semiconductor_stock_price_tbl_PROD'
NEW_PROD_PARQUET_TABLE_S3_BUCKET = 's3://army-sc-bucket-prod'

# Generate timestamp string for paths
DATETIME_NOW_STR = datetime.utcnow().strftime('%Y_%m_%d_%H_%M_%S')
# TODAY_DATE = datetime.now().strftime('%Y-%m-%d')  # Format: 2025-04-14
local_tz = pytz.timezone('America/Chicago')  #local time zone
TODAY_DATE = datetime.now(local_tz).strftime('%Y-%m-%d')

print(TODAY_DATE)

# AWS clients
athena = boto3.client('athena')
glue = boto3.client('glue')

# Check if table exists in Glue Catalog
try:
	glue.get_table(DatabaseName=MY_DATABASE, Name=NEW_PROD_PARQUET_TABLE_NAME)
	table_exists = True
	print("Table exists.")
except glue.exceptions.EntityNotFoundException:
	table_exists = False
	print("Table does not exist — will create it.")

# Build SQL query
if table_exists:
	query = f"""
	INSERT INTO {NEW_PROD_PARQUET_TABLE_NAME}
	SELECT *
	FROM "{MY_DATABASE}"."{SOURCE_PARQUET_TABLE_NAME}"
	WHERE date = '{TODAY_DATE}';
	"""
else:
	query = f"""
	CREATE TABLE {NEW_PROD_PARQUET_TABLE_NAME}
	WITH (
    	external_location = '{NEW_PROD_PARQUET_TABLE_S3_BUCKET}/{DATETIME_NOW_STR}/',
    	format = 'PARQUET',
    	write_compression = 'SNAPPY',
    	partitioned_by = ARRAY['yr_mo_partition']
	)
	AS
	SELECT *
	FROM "{MY_DATABASE}"."{SOURCE_PARQUET_TABLE_NAME}"
	"""

# Start Athena query execution
response = athena.start_query_execution(
	QueryString=query,
	QueryExecutionContext={'Database': MY_DATABASE},
	ResultConfiguration={'OutputLocation': QUERY_RESULTS_BUCKET}
)

query_execution_id = response['QueryExecutionId']

# Wait for the query to finish
while True:
	result = athena.get_query_execution(QueryExecutionId=query_execution_id)
	state = result['QueryExecution']['Status']['State']
	if state in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
    	break

# Handle query result
if state == 'SUCCEEDED':
	print("Query succeeded.")
else:
	reason = result['QueryExecution']['Status'].get('StateChangeReason', 'No reason provided')
	print(f"Query failed: {reason}")
	sys.exit(1)
