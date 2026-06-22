# Sprint 1 Retrospective

## What went well
- All 12 source files loaded successfully into SQLite
- 16 DQ rules implemented and caught real data issues
- 38 unit tests passing (target was 35+)
- FK violations resolved to 0

## Issues found & fixed
- TCS cashflow had duplicate rows (Mar-13 vs Mar 2013 formats) — 35 rows removed
- financial_ratios had 119 duplicate (company_id, year) rows — removed
- 10 companies (WIPRO, ZOMATO, VEDL etc.) were missing from companies.xlsx — added with real names/websites
- JIOFIN and ATGL have genuine data gaps (recent listings) — flagged, not bugs

## Final database state
- companies: 101 (92 original + 9 added)
- profitandloss: 1276
- balancesheet: 1312
- cashflow: 1152 (after dedup)
- financial_ratios: 1065 (after dedup)
- FK violations: 0