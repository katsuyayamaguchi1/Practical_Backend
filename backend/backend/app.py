from fastapi import FastAPI, HTTPException, Query # Queryは不要なら削除してもOK
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests # /fetchtest でのみ使用
import json
from db_control import crud,  mymodels_MySQL as mymodels


# Customerモデルはリクエストボディの型定義として使います
# PUT /customers/{id} の場合、リクエストボディには更新するデータのみを含めるのが一般的で、
# IDはパスから取得します。そのため、更新用モデルを別途定義することが多いです。
class CustomerUpdatePayload(BaseModel):
    customer_name: str
    age: int
    gender: str
    # customer_id はパスから取るので、ボディには含めなくても良いか、
    # 含める場合はパスのIDと一致するか検証するなどの考慮ができます。

# 元のCustomerモデルも残しておきます（POST /customers などで使うため）
class Customer(BaseModel):
    customer_id: str
    customer_name: str
    age: int
    gender: str


app = FastAPI()

# CORSミドルウェアの設定 (これは問題なさそうです)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 開発中は "*" でも良いですが、本番では具体的なオリジンを指定推奨
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"message": "FastAPI top page!"}


@app.post("/customers")
def create_customer(customer: Customer): # Customerモデルを使用
    values = customer.dict()
    # crud.myinsert が customer_id を自動生成しない場合は、ここで生成するか、
    # フロントエンドから送られてきた customer_id を使う
    tmp = crud.myinsert(mymodels.Customers, values) 
    result = crud.myselect(mymodels.Customers, values.get("customer_id"))

    if result:
        result_obj = json.loads(result)
        return result_obj if result_obj else None # result_obj がリストなら result_obj[0] かも
    return None


@app.get("/customers") # これは特定の顧客を取得するエンドポイントのようですね
def read_one_customer(customer_id: str = Query(...)): # Queryパラメータでcustomer_idを受け取っている
    result = crud.myselect(mymodels.Customers, customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found")
    result_obj = json.loads(result)
    return result_obj[0] if result_obj else None


@app.get("/allcustomers")
def read_all_customer():
    result = crud.myselectAll(mymodels.Customers)
    if not result:
        return []
    return json.loads(result)


# ▼▼▼ ここを修正 ▼▼▼
# app.py 内の update_customer 関数

# app.py の update_customer 関数

@app.put("/customers/{received_customer_id}")
async def update_customer(received_customer_id: str, customer_payload: CustomerUpdatePayload):
    print(f"Attempting to update customer with ID from path: {received_customer_id}")
    print(f"Data received in body: {customer_payload.dict()}")

    # crud.myupdate に渡すための 'values' 辞書を作成
    # この辞書には、更新対象を特定するための 'customer_id' と、更新するフィールドが含まれている必要がある
    values_for_crud = customer_payload.dict()  # customer_name, age, gender が入る
    values_for_crud['customer_id'] = received_customer_id # ★パスから受け取ったIDを 'customer_id' キーで追加

    try:
        # crud.myupdate を2つの引数で呼び出す
        tmp = crud.myupdate(mymodels.Customers, values_for_crud) # ★引数を2つに修正
        print(f"crud.myupdate result: {tmp}")
    except Exception as e:
        print(f"Error during crud.myupdate call: {e}")
        # エラーの型や内容に応じて、より適切なHTTPExceptionを返すことも検討
        raise HTTPException(status_code=500, detail=f"Error processing update in crud: {str(e)}")

    # 更新後のデータを再取得して返す (この部分は crud.myupdate の結果によって調整が必要かもしれません)
    result = crud.myselect(mymodels.Customers, received_customer_id)
    if not result:
        raise HTTPException(status_code=404, detail="Customer not found after supposed update")
    
    result_obj = json.loads(result)
    return result_obj[0] if result_obj and isinstance(result_obj, list) and len(result_obj) > 0 else (result_obj if result_obj else None)
# ▲▲▲ ここまで修正 ▲▲▲


@app.delete("/customers/{customer_id_to_delete}") # DELETEもIDをパスで受け取るのが一般的です
def delete_customer(customer_id_to_delete: str):  # Query(...) ではなくパスパラメータとして受け取る
    # customer_id を Query パラメータで受け取る delete_customer は、
    # GET /customers?customer_id=xxx のような形で呼び出す read_one_customer と混同しやすいので注意
    result = crud.mydelete(mymodels.Customers, customer_id_to_delete)
    if not result: # crud.mydelete が成功/失敗や削除件数などを返すかによります
        raise HTTPException(status_code=404, detail="Customer not found for deletion or delete failed")
    return {"customer_id": customer_id_to_delete, "status": "deleted"}


@app.get("/fetchtest")
def fetchtest():
    response = requests.get('https://jsonplaceholder.typicode.com/users')
    return response.json()
