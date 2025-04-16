# poetry run uvicorn backend.main:app --reload
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/users/1234"
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/user/" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"ID": 123,"email": "mm@", "username": "mm"}'

# === Docker Dev ===
# docker build -f dev.Dockerfile -t my-fastapi-app-dev .
# docker run -it --name my-dev-container -p 8000:8000 my-fastapi-app-dev /bin/bash
# poetry run uvicorn backend.main:app --host 0.0.0.0 --port 8000
# http://localhost:8000
# http://localhost:8000/docs

# === Docker Prod ===
# docker build -f prod.Dockerfile -t my-fastapi-app-prod .
# docker run -d --name my-prod-container -p 8000:8000 my-fastapi-app-prod
# curl http://localhost:8000
# curl http://localhost:8000/docs

# === FastAPI WebSocket API for CoinGas ===

from typing import Dict, Any, Union, List
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.websockets import WebSocketState
from datetime import datetime, timedelta
import asyncio
import logging

# === Local modules ===
from .db import gas_collection
from .scheduler.collect import fetch_gas_fees as collector
from .historical import router as historical_router

# === Logging setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("api")

# === FastAPI App ===
app = FastAPI(
    title="CoinGas API",
    description="API for cryptocurrency gas fee information",
    version="1.0.0"
)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Active WebSocket connections ===
active_connections: List[WebSocket] = []

@app.websocket("/ws/gas")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time gas fee data.
    Handles both heartbeat messages and gas fee updates.
    """
    try:
        await websocket.accept()
        active_connections.append(websocket)
        logger.info("✅ WebSocket connection established")
        
        # Initialize last update time
        last_update = datetime.utcnow() - timedelta(seconds=5)
        
        while True:
            try:
                # Wait for either data to be available or a ping message
                try:
                    data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                    if data == "ping":
                        await websocket.send_text("pong")
                        continue
                except asyncio.TimeoutError:
                    # No message received, check if it's time to send an update
                    pass
                
                # Check if it's time to send a gas fee update
                now = datetime.utcnow()
                if (now - last_update).total_seconds() >= 5:
                    # Fetch and format the latest gas fee data
                    latest = collector()
                    logger.info(f"🧪 Latest gas data: {latest}")

                    timestamp = latest.get("timestamp", now.isoformat())

                    # Format data for each cryptocurrency
                    btc = format_btc_data(latest, timestamp)
                    eth = format_eth_data(latest, timestamp)
                    sol = format_sol_data(latest, timestamp)

                    # Send live gas data to frontend
                    payload = [btc, eth, sol]
                    logger.info(f"📤 Sending WebSocket payload")
                    logger.debug(f"Payload details: {payload}")
                    
                    await websocket.send_json(payload)
                    last_update = now
                
                # Small sleep to prevent tight loop
                await asyncio.sleep(0.1)
                
            except WebSocketDisconnect:
                logger.info("⚠️ Client disconnected")
                break
            except Exception as e:
                logger.error(f"❌ Error in WebSocket loop: {str(e)}")
                await asyncio.sleep(1)
                continue

    except WebSocketDisconnect:
        logger.info("⚠️ Client disconnected during handshake")
    except Exception as e:
        logger.error(f"❌ WebSocket error during setup: {str(e)}")
    finally:
        # Clean up resources
        if websocket in active_connections:
            active_connections.remove(websocket)
            logger.info("🧹 Removed connection from active connections")
        try:
            await websocket.close()
            logger.info("🔌 WebSocket connection closed gracefully")
        except Exception as e:
            logger.error(f"❌ Error during WebSocket cleanup: {str(e)}")

# === Formatters for each blockchain ===

def format_btc_data(latest: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    return {
        "network": "bitcoin",
        "symbol": "BTC",
        "speeds": [
            {"level": "high", "gasPrice": f"{latest.get('btc_high', 0)} sat/vB", "estimatedTime": "10-30 min"},
            {"level": "medium", "gasPrice": f"{latest.get('btc_medium', 0)} sat/vB", "estimatedTime": "30-60 min"},
            {"level": "low", "gasPrice": f"{latest.get('btc_low', 0)} sat/vB", "estimatedTime": "1+ hour"},
        ],
        "lastUpdated": timestamp
    }

def format_eth_data(latest: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    return {
        "network": "ethereum",
        "symbol": "ETH",
        "speeds": [
            {"level": "high", "gasPrice": f"{latest.get('eth_high', 0):.2f} gwei", "estimatedTime": "<2 min"},
            {"level": "medium", "gasPrice": f"{latest.get('eth_medium', 0):.2f} gwei", "estimatedTime": "2-5 min"},
            {"level": "low", "gasPrice": f"{latest.get('eth_low', 0):.2f} gwei", "estimatedTime": "5+ min"},
        ],
        "lastUpdated": timestamp
    }

def format_sol_data(latest: Dict[str, Any], timestamp: str) -> Dict[str, Any]:
    return {
        "network": "solana",
        "symbol": "SOL",
        "speeds": [
            {
                "level": "high",
                "gasPrice": f"{latest.get('sol_high', 0):.2e} SOL",
                "estimatedTime": "~2 sec"
            },
            {
                "level": "medium",
                "gasPrice": f"{latest.get('sol_medium', 0):.2e} SOL",
                "estimatedTime": "~5 sec"
            },
            {
                "level": "low",
                "gasPrice": f"{latest.get('sol_low', 0):.2e} SOL",
                "estimatedTime": "~10 sec"
            }
        ],
        "lastUpdated": timestamp
    }

# === REST Endpoints ===

@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Gas Fee API is running"}

@app.get("/latest")
def get_latest_fees() -> Dict[str, Any]:
    latest = gas_collection.find_one(sort=[("timestamp", -1)])
    if not latest:
        raise HTTPException(status_code=404, detail="No gas data found")
    latest["_id"] = str(latest["_id"])
    return latest

@app.get("/history")
def get_fee_history(limit: int = 100) -> List[Dict[str, Any]]:
    history = list(gas_collection.find().sort("timestamp", -1).limit(limit))
    for doc in history:
        doc["_id"] = str(doc["_id"])
    return history

@app.get("/history/{network}")
def get_network_history(network: str, limit: int = 100) -> List[Dict[str, Any]]:
    fee_fields = {
        "bitcoin": ("btc_high", "btc_medium", "btc_low"),
        "ethereum": ("eth_high", "eth_medium", "eth_low"),
        "solana": ("sol_high", "sol_medium", "sol_low")
    }

    if network not in fee_fields:
        raise HTTPException(status_code=400, detail=f"Invalid network. Must be one of: {', '.join(fee_fields.keys())}")

    high_field, medium_field, low_field = fee_fields[network]

    history = list(gas_collection.find(
        {},
        {"timestamp": 1, high_field: 1, medium_field: 1, low_field: 1, "_id": 0}
    ).sort("timestamp", -1).limit(limit))

    formatted_history = []
    for doc in history:
        formatted_history.append({
            "date": doc["timestamp"],
            "high": doc[high_field],
            "medium": doc[medium_field],
            "low": doc[low_field]
        })

    return formatted_history

# Include optional router
app.include_router(historical_router)
