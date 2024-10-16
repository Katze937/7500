from flask import Flask, jsonify
from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# RPC connection settings
rpc_user = "__cookie__"
rpc_password = "b7281293a06c2496e4ebada7ec6c221bce3a59d34bffbfddbdc526a4f282662c"
rpc_host = "127.0.0.1"
rpc_port = "8332"

# Connect to Bitcoin Core
try:
    rpc_connection = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@{rpc_host}:{rpc_port}")
    latest_block_hash = rpc_connection.getbestblockhash()  # Test connection
    print("Successfully connected to Bitcoin Core. Latest Block Hash:", latest_block_hash)
except Exception as e:
    print("Error connecting to Bitcoin Core:", str(e))

app = Flask(__name__)

def get_latest_blocks(num_blocks=10):
    latest_block_hash = rpc_connection.getbestblockhash()
    blocks = []

    # Fetch the latest blocks
    for _ in range(num_blocks):
        block_info = rpc_connection.getblock(latest_block_hash)
        blocks.append({
            'height': block_info['height'],
            'time': block_info['time'],
            'size': block_info['size'],
            'tx_count': len(block_info['tx']),
            'merkle_root': block_info['merkleroot'],
        })
        latest_block_hash = block_info['previousblockhash']  # Get the previous block hash for the next iteration

    return blocks

@app.route('/api/block_data', methods=['GET'])
def get_block_data():
    try:
        blocks = get_latest_blocks()
        return jsonify(blocks)
    except Exception as e:
        print("Error fetching block data:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000)
