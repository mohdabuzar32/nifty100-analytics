-- Query 1: Total companies in the database
SELECT COUNT(*) AS total_companies FROM companies;

-- Query 2: Top 10 companies by latest year sales (profitandloss)
SELECT company_id, year, sales
FROM profitandloss
WHERE year = 2024
ORDER BY sales DESC
LIMIT 10;

-- Query 3: Companies with highest net profit margin (latest year)
SELECT company_id, year, net_profit, sales,
       ROUND((net_profit * 100.0 / sales), 2) AS net_margin_pct
FROM profitandloss
WHERE year = 2024 AND sales > 0
ORDER BY net_margin_pct DESC
LIMIT 10;

-- Query 4: Average ROE by sector
SELECT s.broad_sector, ROUND(AVG(c.roe_percentage), 2) AS avg_roe
FROM companies c
JOIN sectors s ON c.id = s.company_id
WHERE c.roe_percentage IS NOT NULL
GROUP BY s.broad_sector
ORDER BY avg_roe DESC;

-- Query 5: Companies with debt_to_equity > 1 (highly leveraged)
SELECT company_id, year, debt_to_equity
FROM financial_ratios
WHERE debt_to_equity > 1
ORDER BY debt_to_equity DESC
LIMIT 10;

-- Query 6: Year-over-year sales growth for a specific company (TCS)
SELECT year, sales,
       sales - LAG(sales) OVER (ORDER BY year) AS yoy_change
FROM profitandloss
WHERE company_id = 'TCS'
ORDER BY year;

-- Query 7: Stock price volatility (max - min close) per company in 2024
SELECT company_id,
       MAX(close_price) AS max_close,
       MIN(close_price) AS min_close,
       ROUND(MAX(close_price) - MIN(close_price), 2) AS price_range
FROM stock_prices
WHERE date LIKE '2024%'
GROUP BY company_id
ORDER BY price_range DESC
LIMIT 10;

-- Query 8: Companies in each peer group
SELECT peer_group_name, COUNT(*) AS member_count
FROM peer_groups
GROUP BY peer_group_name
ORDER BY member_count DESC;

-- Query 9: Companies with balance sheet mismatch (data quality spot-check)
SELECT company_id, year, total_liabilities, total_assets
FROM balancesheet
WHERE ABS(total_liabilities - total_assets) > 1
ORDER BY year DESC;

-- Query 10: Market cap leaders (latest year)
SELECT mc.company_id, c.company_name, mc.year, mc.market_cap_crore
FROM market_cap mc
JOIN companies c ON mc.company_id = c.id
WHERE mc.year = (SELECT MAX(year) FROM market_cap)
ORDER BY mc.market_cap_crore DESC
LIMIT 10;