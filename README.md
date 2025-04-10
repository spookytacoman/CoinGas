### Install Dependencies
1. `cd` into this dir
2. Ensure `poetry config virtualenvs.in-project true`
3. `poetry install`
4. `cd ./CoinGas/frontend/`
5. `npm install`  
   *Note: Ignore the warning*

### Run backend
1. `cd` into root dir
2. `poetry run uvicorn CoinGas.backend.main:app --reload`

### Run frontend
1. `cd ./CoinGas/frontend/`
2. `npm run dev`