import sqlite3
import pandas as pd

DB_PATH = "../../data/musinsa.db"
CSV_PATH = "../../data/musinsa_processed.csv"

df = pd.read_csv(CSV_PATH)
print(f"데이터: {df.shape[0]}행 x {df.shape[1]}열")

conn = sqlite3.connect(DB_PATH)
df.to_sql("products", conn, if_exists="replace", index=False)
print(f"DB 적재: {DB_PATH}")

result = pd.read_sql("SELECT COUNT(*) AS 총_상품수 FROM products", conn)
print(result)
conn.close()