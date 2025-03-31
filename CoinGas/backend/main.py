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
from fastapi import FastAPI, HTTPException

app:FastAPI = FastAPI()

@app.get("/")
def read_root() -> Dict[str, str]:
    return {"message": "Hello, FastAPI World!"}