import json
import boto3
import urllib3
import datetime
import time


FIREHOSE_NAME = 'PUT-S3-naxEK'
BASE_URL = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey=WCE5JCRHA0EIM2SC'
SYMBOLS = ["AMD", "NVDA", "INTC", "MU", "QCOM", "TXN", "AMAT", "AVGO", "LSCC", "KLAC"]


def lambda_handler(event, context):
    http = urllib3.PoolManager()
    fh = boto3.client('firehose')

    for symbol in SYMBOLS:
        url = BASE_URL.format(symbol=symbol)
        r = http.request("GET", url)
        data = json.loads(r.data.decode('utf-8'))

        time_series = data.get("Time Series (Daily)", {})
        if not time_series:
            print(f"No time series data returned for {symbol}")
            continue

        # Get the most recent trading day
        latest_date = sorted(time_series.keys(), reverse=True)[0]
        values = time_series[latest_date]


        processed = {
            "date": latest_date,
            "symbol": symbol,
            "open": float(values["1. open"]),
            "high": float(values["2. high"]),
            "low": float(values["3. low"]),
            "close": float(values["4. close"]),
            "volume": int(values["5. volume"]),
            "row_ts": str(datetime.datetime.now())
        }


        msg = json.dumps(processed) + '\n'

        fh.put_record(
            DeliveryStreamName=FIREHOSE_NAME,
            Record={'Data': msg}
        )


        time.sleep(15)  # respect API limits

    return {
        'statusCode': 200,
        'body': f"Daily data for {len(SYMBOLS)} symbols ingested to Firehose."
    }
