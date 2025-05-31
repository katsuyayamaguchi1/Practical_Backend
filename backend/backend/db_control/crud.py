# uname() error回避
import platform
print("platform", platform.uname())


from sqlalchemy import create_engine, insert, delete, update, select
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import json
import pandas as pd
from db_control.connect import engine
from .mymodels_MySQL import Customers


def myinsert(mymodel, values):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()

    query = insert(mymodel).values(values)
    try:
        # トランザクションを開始
        with session.begin():
            # データの挿入
            result = session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()

    # セッションを閉じる
    session.close()
    return "inserted"


def myselect(mymodel, customer_id):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(mymodel).filter(mymodel.customer_id == customer_id)
    try:
        # トランザクションを開始
        with session.begin():
            result = query.all()
        # 結果をオブジェクトから辞書に変換し、リストに追加
        result_dict_list = []
        for customer_info in result:
            result_dict_list.append({
                "customer_id": customer_info.customer_id,
                "customer_name": customer_info.customer_name,
                "age": customer_info.age,
                "gender": customer_info.gender
            })
        # リストをJSONに変換
        result_json = json.dumps(result_dict_list, ensure_ascii=False)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")

    # セッションを閉じる
    session.close()
    return result_json


def myselectAll(mymodel):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    query = select(mymodel)
    try:
        # トランザクションを開始
        with session.begin():
            df = pd.read_sql_query(query, con=engine)
            result_json = df.to_json(orient='records', force_ascii=False)

    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        result_json = None

    # セッションを閉じる
    session.close()
    return result_json


# db_control/crud.py の myupdate 関数

def myupdate(mymodel, values): # values には 'customer_id' と更新フィールドが含まれている想定
    Session = sessionmaker(bind=engine)
    session = Session()
    return_message = "update failed" # デフォルトのメッセージ

    try:
        target_customer_id = values.pop("customer_id", None)

        if target_customer_id is None:
            print("Error: customer_id not found in values for update.")
            session.close()
            return "Update failed: customer_id missing"

        # SQLAlchemy の update 文を作成
        stmt = (
            update(mymodel)
            .where(mymodel.customer_id == target_customer_id) # mymodels.Customers.customer_id など、実際のカラム名に合わせる
            .values(values) # 更新するデータ (例: {'customer_name': 'New Name', 'age': 30})
        )
        
        with session.begin(): # トランザクション管理
            result = session.execute(stmt)
        
        if result.rowcount > 0:
            print(f"Update successful for customer_id: {target_customer_id}. Rows affected: {result.rowcount}")
            return_message = "updated"
        else:
            print(f"No rows updated for customer_id: {target_customer_id} (customer not found or data unchanged).")
            return_message = "no rows updated"

    except sqlalchemy.exc.IntegrityError as e:
        print(f"一意制約違反により、更新に失敗しました: {e}")
        # session.rollback() # session.begin() を使っていれば自動ロールバック
        return_message = "IntegrityError during update"
    except Exception as e:
        print(f"An error occurred during update: {e}")
        # session.rollback() # 必要に応じて
        return_message = f"Error during update: {e}"
    finally:
        session.close()
    
    return return_message


def mydelete(mymodel, customer_id):
    # session構築
    Session = sessionmaker(bind=engine)
    session = Session()
    query = delete(mymodel).where(mymodel.customer_id == customer_id)
    try:
        # トランザクションを開始
        with session.begin():
            result = session.execute(query)
    except sqlalchemy.exc.IntegrityError:
        print("一意制約違反により、挿入に失敗しました")
        session.rollback()

    # セッションを閉じる
    session.close()
    return customer_id + " is deleted"