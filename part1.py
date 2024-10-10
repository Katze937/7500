import subprocess
import mysql.connector
import time
from flask import Flask, render_template

# Flask 應用程式初始化
app = Flask(__name__)

# 資料庫連接設定
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="bitcoin"
)
cursor = db.cursor()

# 從 Bitcoin 節點獲取區塊高度
def get_block_height():
    try:
        result = subprocess.run(['bitcoin-cli', 'getblockcount'], stdout=subprocess.PIPE, text=True)
        block_height = int(result.stdout.strip())
        return block_height
    except Exception as e:
        print(f"error: {e}")
        return None

# 將區塊高度更新到資料庫
def update_block_height_in_db(block_height):
    query = "REPLACE INTO blocks (block_height) VALUES (%s)"
    cursor.execute(query, (block_height,))
    db.commit()
    print(f"The block height {block_height} has updated to the database")

# 資料擷取程式，持續更新區塊高度
def start_ingestion():
    while True:
        block_height = get_block_height()
        if block_height is not None:
            update_block_height_in_db(block_height)
        time.sleep(10)

# 從資料庫中查詢區塊高度
def get_block_height_from_db():
    cursor.execute("SELECT block_height FROM blocks LIMIT 1")
    result = cursor.fetchone()
    return result[0] if result else None

# 網頁路由，顯示區塊高度
@app.route('/')
def block_height():
    block_height = get_block_height_from_db()
    return render_template('block_height.html', block_height=block_height)

if __name__ == '__main__':
    # 開啟資料擷取的子執行緒
    import threading
    ingestion_thread = threading.Thread(target=start_ingestion)
    ingestion_thread.start()

    # 啟動 Flask 網頁伺服器
    app.run(debug=True)
