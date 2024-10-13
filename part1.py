import subprocess
import mysql.connector
import time
from flask import Flask, render_template, jsonify
import threading

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

# 從 Bitcoin 節點獲取鏈上數據
def get_blockchain_data():
    try:
        # 獲取區塊高度
        result = subprocess.run(['bitcoin-cli', 'getblockcount'], stdout=subprocess.PIPE, text=True)
        block_height = int(result.stdout.strip())
        
        # 獲取最新區塊哈希
        block_hash_result = subprocess.run(['bitcoin-cli', 'getbestblockhash'], stdout=subprocess.PIPE, text=True)
        block_hash = block_hash_result.stdout.strip()
        
        # 根據哈希獲取區塊詳細信息
        block_info_result = subprocess.run(['bitcoin-cli', 'getblock', block_hash], stdout=subprocess.PIPE, text=True)
        block_info = block_info_result.stdout.strip()

        return {"block_height": block_height, "block_hash": block_hash, "block_info": block_info}
    except Exception as e:
        print(f"Error fetching blockchain data: {e}")
        return None

# 將區塊高度更新到資料庫
def update_block_height_in_db(block_data):
    query = "REPLACE INTO blocks (block_height, block_hash) VALUES (%s, %s)"
    cursor.execute(query, (block_data['block_height'], block_data['block_hash']))
    db.commit()
    print(f"The block height {block_data['block_height']} and block hash {block_data['block_hash']} have updated to the database")

# 資料擷取程式，持續更新區塊高度和哈希
def start_ingestion():
    while True:
        block_data = get_blockchain_data()
        if block_data:
            update_block_height_in_db(block_data)
        time.sleep(10)

# 從資料庫中查詢區塊高度
def get_block_height_from_db():
    cursor.execute("SELECT block_height, block_hash FROM blocks LIMIT 1")
    result = cursor.fetchone()
    return {"block_height": result[0], "block_hash": result[1]} if result else None

# 網頁路由，顯示區塊高度和區塊哈希
@app.route('/')
def block_height():
    block_data = get_block_height_from_db()
    return render_template('block_height.html', block_height=block_data['block_height'], block_hash=block_data['block_hash'])

# 提供 API 端點來獲取鏈上數據
@app.route('/api/block_data')
def get_block_data():
    block_data = get_block_height_from_db()
    return jsonify(block_data)

if __name__ == '__main__':
    # 開啟資料擷取的子執行緒
    ingestion_thread = threading.Thread(target=start_ingestion)
    ingestion_thread.start()

    # 啟動 Flask 網頁伺服器
    app.run(debug=True)