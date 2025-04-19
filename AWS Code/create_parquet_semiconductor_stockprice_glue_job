import sys
import boto3

client = boto3.client('athena')

SOURCE_TABLE_NAME = 'sc_2025'
NEW_TABLE_NAME = 'semiconductor_stock_price'
NEW_TABLE_S3_BUCKET = 's3://army-sc-bucket-parquet/'
MY_DATABASE = 'semiconductorstock'
QUERY_RESULTS_S3_BUCKET = 's3://army-sc-query-results-bucket'

# Refresh the table
queryStart = client.start_query_execution(
	QueryString = f"""
	CREATE TABLE {NEW_TABLE_NAME} WITH
	(external_location='{NEW_TABLE_S3_BUCKET}',
	format='PARQUET',
	write_compression='SNAPPY',
	partitioned_by = ARRAY['yr_mo_partition'])
	AS

	SELECT
    	date
    	,symbol
    	,open
    	,high
    	,low
    	,close
    	,volume
    	,round((close - open),2) AS daily_return
    	,round((open + high + low + close) / 4,2) AS avg_daily_price
    	,SUBSTRING(date,1,7) AS yr_mo_partition
	FROM "{MY_DATABASE}"."{SOURCE_TABLE_NAME}"

	;
	""",
	QueryExecutionContext = {
    	'Database': f'{MY_DATABASE}'
	},
	ResultConfiguration = { 'OutputLocation': f'{QUERY_RESULTS_S3_BUCKET}'}
)

# list of responses
resp = ["FAILED", "SUCCEEDED", "CANCELLED"]

# get the response
response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])

# wait until query finishes
while response["QueryExecution"]["Status"]["State"] not in resp:
	response = client.get_query_execution(QueryExecutionId=queryStart["QueryExecutionId"])

# if it fails, exit and give the Athena error message in the logs
if response["QueryExecution"]["Status"]["State"] == 'FAILED':
	sys.exit(response["QueryExecution"]["Status"]["StateChangeReason"])
