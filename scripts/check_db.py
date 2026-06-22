import sqlite3

conn = sqlite3.connect("nifty100.db")
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = [row[0] for row in cursor.fetchall()]
print("Tables in database:")
for t in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
    print(f"  {t}: {count} rows")
conn.close()