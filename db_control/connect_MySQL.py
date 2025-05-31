# connect_MySQL.py -

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from pathlib import Path

# 1. .envファイルのパスを指定して読み込む
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# 2. 環境変数を取得
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_PORT = os.getenv('DB_PORT')
SSL_CA_PATH = os.getenv('SSL_CA_PATH')

# 3. SSL証明書のフルパスを組み立てる
ssl_ca_full_path = None
if SSL_CA_PATH: # SSL_CA_PATHが設定されている場合のみパスを組み立てる
    if not os.path.isabs(SSL_CA_PATH):
        ssl_ca_full_path = Path(__file__).resolve().parent.parent / SSL_CA_PATH
    else:
        ssl_ca_full_path = SSL_CA_PATH

# データベース接続URLを組み立て
DATABASE_URL = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 接続引数を準備
connect_args_dict = {}
if ssl_ca_full_path:
    connect_args_dict["ssl"] = {
        "ca":str(ssl_ca_full_path)
    }

# データベースエンジンを作成
engine = create_engine(
    DATABASE_URL,
    echo=False,  # 通常運用時はFalseにすることが多い（SQLログを非表示）
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args=connect_args_dict
)

# 動作確認用に、接続先ホスト名だけは残しておく
print(f"--- Connecting to database: {DB_HOST} ---")