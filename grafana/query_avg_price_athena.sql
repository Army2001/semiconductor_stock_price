SELECT
CAST(date AS TIMESTAMP) AS date,
symbol,
avg_daily_price
FROM semiconductor_stock_price_tbl_prod
WHERE $__timeFilter(CAST(date AS TIMESTAMP)) and symbol <> 'KLAC'
order by 1
