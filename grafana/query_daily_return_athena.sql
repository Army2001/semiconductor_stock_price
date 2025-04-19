SELECT
   CAST(date AS TIMESTAMP) AS date
  ,symbol
  ,daily_return
FROM semiconductor_stock_price_tbl_prod
WHERE $__timeFilter(CAST(date AS TIMESTAMP)) and symbol <> 'KLAC'
ORDER BY 1
