# poetry run uvicorn CoinGas.backend.main:app --reload
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/users/1234"
# Invoke-RestMethod -Uri "http://127.0.0.1:8000/user/" -Method Post -Headers @{"Content-Type"="application/json"} -Body '{"ID": 123,"email": "mm@", "username": "mm"}'

# === Docker Dev ===
# docker build -f dev.Dockerfile -t my-fastapi-app-dev .
# docker run -it --name my-dev-container -p 8000:8000 my-fastapi-app-dev /bin/bash
# poetry run uvicorn fastapi_lab.main:app --host 0.0.0.0 --port 8000
# http://localhost:8000
# http://localhost:8000/docs

# === Docker Prod ===
# docker build -f prod.Dockerfile -t my-fastapi-app-prod .
# docker run -d --name my-prod-container -p 8000:8000 my-fastapi-app-prod
# curl http://localhost:8000
# curl http://localhost:8000/docs

from typing import Dict, Any, Union
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
from datetime import datetime
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock gas data
MOCK_GAS_DATA = [
    {
        "network": "bitcoin",
        "symbol": "BTC",
        "speeds": [
            {
                "level": "low",
                "gasPrice": "1-5 sat/vB",
                "estimatedTime": "1+ hour"
            },
            {
                "level": "medium",
                "gasPrice": "6-15 sat/vB",
                "estimatedTime": "30-60 min"
            },
            {
                "level": "high",
                "gasPrice": "16+ sat/vB",
                "estimatedTime": "10-30 min"
            }
        ],
        "lastUpdated": None
    },
    {
        "network": "ethereum",
        "symbol": "ETH",
        "speeds": [
            {
                "level": "low",
                "gasPrice": "25 gwei",
                "estimatedTime": "5+ min"
            },
            {
                "level": "medium",
                "gasPrice": "30 gwei",
                "estimatedTime": "2-5 min"
            },
            {
                "level": "high",
                "gasPrice": "35 gwei",
                "estimatedTime": "<2 min"
            }
        ],
        "lastUpdated": None
    },
    {
        "network": "solana",
        "symbol": "SOL",
        "speeds": [
            {
                "level": "low",
                "gasPrice": "0.000005 SOL",
                "estimatedTime": "~10 sec"
            },
            {
                "level": "medium",
                "gasPrice": "0.00001 SOL",
                "estimatedTime": "~5 sec"
            },
            {
                "level": "high",
                "gasPrice": "0.00002 SOL",
                "estimatedTime": "~2 sec"
            }
        ],
        "lastUpdated": None
    }
]

@app.websocket("/ws/gas")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Update the lastUpdated timestamp
            current_time = datetime.now().isoformat()
            for network in MOCK_GAS_DATA:
                network["lastUpdated"] = current_time
            
            # Send the updated data
            await websocket.send_json(MOCK_GAS_DATA)
            
            # Wait for 5 seconds before sending the next update
            await asyncio.sleep(5)
    
    except WebSocketDisconnect:
        print("Client disconnected")
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        
    finally:
        try:
            await websocket.close()
        except:
            pass  # Ignore errors when trying to close an already closed connection

@app.get("/")
def read_root():
    return {"message": "Gas Fee API is running"}