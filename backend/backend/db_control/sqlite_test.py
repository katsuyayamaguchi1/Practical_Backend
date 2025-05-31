# PythonでSQLiteを直接使う簡単な例
import sqlite3

# データベースファイルに接続 (ファイルがなければ新規作成される)
conn = sqlite3.connect('sample.db')

# カーソルオブジェクトを作成
cursor = conn.cursor()

# テーブル作成のSQL (例)
cursor.execute('''　
CREATE TABLE IF NOT EXISTS sample_table (
    id INTEGER PRIMARY KEY ,
    name TEXT NOT NULL,
    age INTEGER NOT NULL
)
''')

# データを削除
cursor.execute('DELETE FROM sample_table')

sample_data = [(1, 'Alice', 30), (2, 'Bob', 25), (3, 'charlie' , 35)]

# データを挿入
cursor.executemany('INSERT INTO sample_table VALUES (?,?,?)', sample_data)

# 変更をコミット (保存)
conn.commit()

# 接続を閉じる
conn.close()