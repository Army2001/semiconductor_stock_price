import sys
import awswrangler as wr

# This check counts NULLs in avg_daily_price and daily_return
NULL_DQ_CHECK = """
SELECT
	SUM(CASE WHEN avg_daily_price IS NULL THEN 1 ELSE 0 END) AS avg_daily_price_nulls,
	SUM(CASE WHEN daily_return IS NULL THEN 1 ELSE 0 END) AS daily_return_nulls
FROM "semiconductorstock"."semiconductor_stock_price"
;
"""

# Run the quality check
df = wr.athena.read_sql_query(sql=NULL_DQ_CHECK, database="semiconductorstock")

# Exit if any of the results > 0
if df['avg_daily_price_nulls'][0] > 0 or df['daily_return_nulls'][0] > 0:
	print(df)  # optional: show which failed
	sys.exit('Results returned. Quality check failed.')
else:
	print('Quality check passed.')
