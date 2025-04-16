import sys
import os
import requests
import datetime

# Enable import from backend/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from backend.db import gas_collection

# Load environment variables
load_dotenv()

def fetch_gas_fees():
    now = datetime.datetime.utcnow().isoformat()

    # ✅ BTC – mempool.space API
    btc_url = "https://mempool.space/api/v1/fees/recommended"
    btc_data = requests.get(btc_url).json()
    btc_fee = btc_data["fastestFee"]  # sats/vByte

    # ✅ ETH – Etherscan API
    try:
        etherscan_url = (
            f"https://api.etherscan.io/api?module=gastracker&action=gasoracle"
            f"&apikey={os.getenv('ETHERSCAN_API_KEY')}"
        )
        eth_response = requests.get(etherscan_url)
        eth_response.raise_for_status()
        eth_data = eth_response.json()
        eth_fee = float(eth_data["result"]["FastGasPrice"])  # Gwei
    except Exception as e:
        print("⚠️ Etherscan ETH gas fetch failed:", e)
        return

    # ✅ SOL – mocked value (for now)
    sol_fee = 0.00001

    # ✅ Save to MongoDB
    entry = {
        "timestamp": now,
        "btc": btc_fee,
        "eth": eth_fee,
        "sol": sol_fee
    }

    gas_collection.insert_one(entry)
    print(f"✅ Stored gas fees @ {now}: BTC {btc_fee}, ETH {eth_fee}, SOL {sol_fee}")

if __name__ == "__main__":
    fetch_gas_fees()
