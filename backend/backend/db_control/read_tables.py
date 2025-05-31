from tabulate import tabulate
from sqlalchemy import text
from db_control.connect_MySQL import engine

print("--- Connecting to database ---")

# SQL実行
with engine.connect() as conn:
    result = conn.execute(text("SELECT * FROM customers"))
    rows = result.fetchall()

# ヘッダー定義（カラム名）
headers = ["customer_id", "customer_name", "age", "gender"]

# 表形式で出力
print(tabulate(rows, headers=headers, tablefmt="grid"))
