import json
import boto3
import urllib3
import datetime

S3_BUCKET = 'army-sc-bucket'

# List of symbols for different companies
symbols = ["AMD", "NVDA", "INTC", "MU", "QCOM", "TXN", "AMAT", "AVGO", "LSCC", "KLAC"]


def lambda_handler(event, context):
	http = urllib3.PoolManager()

	# Create an empty list to store all processed data
	all_processed_data = []

	for symbol in symbols:
    	# API URL for each symbol
    	api_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=WCE5JCRHA0EIM2SC"
    	r = http.request("GET", api_url)

    	# Turn the response into a dictionary
    	data = json.loads(r.data.decode('utf-8'))

    	# Extract the time series data for the symbol
    	time_series = data.get("Time Series (Daily)", {})

    	# Process the data and add symbol to each entry
    	for date, daily_data in time_series.items():
        	row = {
            	"symbol": symbol,
            	"date": date,
            	"open": daily_data["1. open"],
            	"high": daily_data["2. high"],
            	"low": daily_data["3. low"],
            	"close": daily_data["4. close"],
            	"volume": daily_data["5. volume"],
            	"time_captured": str(datetime.datetime.now())
        	}
        	all_processed_data.append(row)

	# Convert processed data to CSV format
	csv_content = "symbol,date,open,high,low,close,volume,time_captured\n"
	for row in all_processed_data:
    	csv_content += f'{row["symbol"]},{row["date"]},{row["open"]},{row["high"]},{row["low"]},{row["close"]},{row["volume"]},{row["time_captured"]}\n'

	# Upload the CSV file to S3
	s3_client = boto3.client('s3')
	reply = s3_client.put_object(Body=csv_content, Bucket=S3_BUCKET, Key=f"semiconductorstock_data/{int(datetime.datetime.now().timestamp())}_all_stocks.csv")

	return reply
