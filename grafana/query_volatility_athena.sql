SELECT
  CAST(date AS TIMESTAMP) AS date,
  symbol,
  ROUND(
	0.5 * POWER(LN(high / low), 2) -
	(2 * LN(2) - 1) * POWER(LN(close / open), 2),
	4
  ) AS volatility
FROM semiconductor_stock_price_tbl_prod
WHERE $__timeFilter(CAST(date AS TIMESTAMP))
  --AND symbol <> 'KLAC'
ORDER BY 1
