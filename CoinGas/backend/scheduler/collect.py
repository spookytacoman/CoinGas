import os
import requests
from datetime import datetime
from dotenv import load_dotenv
import logging
from typing import Dict, Any, Tuple

# Import the centralized MongoDB connection
from ..db import get_gas_collection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("collector")

# Load environment variables
load_dotenv()

# Etherscan API key
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "")
logger.info(f"Loaded ETHERSCAN_API_KEY: {'[SET]' if ETHERSCAN_API_KEY else '[NOT SET]'}")

# Solana RPC URL
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")

# Get MongoDB collection
collection = get_gas_collection()

def fetch_gas_fees() -> Dict[str, Any]:
    timestamp = datetime.now().isoformat()

    btc_high, btc_medium, btc_low = fetch_btc_fees()
    eth_high, eth_medium, eth_low = fetch_eth_fees()
    sol_high, sol_medium, sol_low = fetch_sol_fees()

    entry = {
        "timestamp": timestamp,
        "btc_high": btc_high,
        "btc_medium": btc_medium,
        "btc_low": btc_low,
        "eth_high": eth_high,
        "eth_medium": eth_medium,
        "eth_low": eth_low,
        "sol_high": sol_high,
        "sol_medium": sol_medium,
        "sol_low": sol_low
    }

    logger.info(f"✅ Fetched gas fees @ {timestamp}")
    collection.insert_one(entry)
    logger.info(f"✅ Stored gas fees in MongoDB @ {timestamp}")

    return entry

def fetch_btc_fees() -> Tuple[int, int, int]:
    btc_url = "https://mempool.space/api/v1/fees/recommended"
    response = requests.get(btc_url, timeout=10)
    response.raise_for_status()
    data = response.json()

    btc_high = data["fastestFee"]
    btc_medium = data["halfHourFee"]
    btc_low = data["hourFee"]

    logger.info(f"BTC fees: high={btc_high}, medium={btc_medium}, low={btc_low}")
    return btc_high, btc_medium, btc_low

def fetch_eth_fees() -> Tuple[float, float, float]:
    if not ETHERSCAN_API_KEY:
        raise ValueError("ETHERSCAN_API_KEY not set")

    url = (
        f"https://api.etherscan.io/api?module=gastracker&action=gasoracle"
        f"&apikey={ETHERSCAN_API_KEY}"
    )
    logger.info(f"Fetching ETH fees from: {url}")
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()
    logger.info(f"Etherscan API response: {data}")

    if data.get("status") != "1" or "result" not in data:
        raise ValueError(f"Invalid Etherscan response: {data}")

    result = data["result"]
    eth_high = float(result["FastGasPrice"])
    eth_medium = float(result["ProposeGasPrice"])
    eth_low = float(result["SafeGasPrice"])

    logger.info(f"ETH fees: high={eth_high:.2f}, medium={eth_medium:.2f}, low={eth_low:.2f}")
    return eth_high, eth_medium, eth_low

def fetch_sol_fees() -> Tuple[float, float, float]:
    headers = {"Content-Type": "application/json"}
    
    # Step 1: Get recent blocks to analyze actual transaction fees
    blocks_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getLatestBlockhash",
        "params": [{"commitment": "finalized"}]
    }

    try:
        response = requests.post(SOLANA_RPC_URL, headers=headers, json=blocks_payload, timeout=10)
        response.raise_for_status()
        block_data = response.json()

        if "result" not in block_data or "value" not in block_data["result"]:
            logger.warning("Could not get latest blockhash, using default fees")
            return 0.000005, 0.00001, 0.000015  # Default fees in SOL
    except Exception as e:
        logger.warning(f"Error fetching blockhash: {str(e)}, using default fees")
        return 0.000005, 0.00001, 0.000015  # Default fees in SOL

    # Step 2: Get recent prioritization fees for accurate fee data
    fees_payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getRecentPrioritizationFees",
        "params": []
    }

    try:
        fees_response = requests.post(SOLANA_RPC_URL, headers=headers, json=fees_payload, timeout=10)
        fees_response.raise_for_status()
        fees_data = fees_response.json()

        if "result" not in fees_data:
            logger.warning("Could not get prioritization fees, using default fees")
            return 0.000005, 0.00001, 0.000015  # Default fees in SOL

        # Calculate base fee from recent prioritization fees
        recent_fees = fees_data["result"]
        if recent_fees:
            # Filter out zero fees and calculate average
            valid_fees = [fee.get("prioritizationFee", 0) for fee in recent_fees if fee.get("prioritizationFee", 0) > 0]
            if valid_fees:
                base_fee = sum(valid_fees) / len(valid_fees)
            else:
                base_fee = 5000  # Default if no valid fees found
        else:
            base_fee = 5000  # Default base fee in lamports

        # Convert to SOL
        base_fee_sol = base_fee / 1_000_000_000

        # Step 3: Get network performance metrics for accurate load calculation
        stats_payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getRecentPerformanceSamples",
            "params": [4]  # Get last 4 samples for better average
        }

        response = requests.post(SOLANA_RPC_URL, headers=headers, json=stats_payload, timeout=10)
        response.raise_for_status()
        stats_data = response.json()

        # Calculate load factor based on actual network metrics
        load_factor = 1.0
        if "result" in stats_data and stats_data["result"]:
            total_tps = 0
            total_slots = 0
            for sample in stats_data["result"]:
                total_tps += sample.get("numTransactions", 0)
                total_slots += sample.get("numSlots", 1)
            
            avg_tps = total_tps / max(total_slots, 1)
            # Calculate load factor based on actual TPS vs network capacity
            load_factor = min(max(avg_tps / 1000, 0.1), 2.0)  # Cap between 0.1 and 2.0

        # Calculate fees based on network load
        sol_low = base_fee_sol
        sol_medium = base_fee_sol * (1 + load_factor)
        sol_high = base_fee_sol * (1 + load_factor * 2)

        logger.info(f"SOL fees (in SOL): high={sol_high:.2e}, medium={sol_medium:.2e}, low={sol_low:.2e}")
        logger.info(f"Network load factor: {load_factor:.2f}")
        logger.info(f"Base fee (in lamports): {base_fee}")
        logger.info(f"Average TPS: {avg_tps if 'avg_tps' in locals() else 'N/A'}")
        return sol_high, sol_medium, sol_low

    except Exception as e:
        logger.error(f"Error calculating Solana fees: {str(e)}")
        return 0.000005, 0.00001, 0.000015  # Default fees in SOL
