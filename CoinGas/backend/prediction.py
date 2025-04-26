import google.generativeai as genai
import logging
import os
import json
from datetime import datetime, timedelta

from .db import gas_collection

# === Logging setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("predictor")

# Configure Gemini API with key from environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")
genai.configure(api_key=GEMINI_API_KEY)

# Set up the model
model = genai.GenerativeModel('gemini-1.5-flash')

def network_to_short(network: str) -> str:
    """
    Convert full network name to shortened MongoDB field name.
    
    Args:
        network: Full network name (bitcoin, ethereum, solana)
    
    Returns:
        str: Shortened name (btc, eth, sol)
    """
    mapping = {
        "bitcoin": "btc",
        "ethereum": "eth", 
        "solana": "sol"
    }
    return mapping.get(network.lower(), network)


def predict_tomorrow(network:str):
    """
    Predict tomorrow's gas fees for a given network using historical data and Gemini AI.
    
    Args:
        network: The blockchain network to predict for (bitcoin, ethereum, solana)
    
    Returns:
        dict: Predicted gas fees with high, medium, low values
    """
    
    mongoDbNetworkName:str = network_to_short(network)
    # Get historical data
    history = list(gas_collection.find(
        {},
        {"timestamp": 1, f"{mongoDbNetworkName}_high": 1, f"{mongoDbNetworkName}_medium": 1, f"{mongoDbNetworkName}_low": 1, "_id": 0}
    ).sort("timestamp", -1).limit(100))
    
    if not history:
        logger.error(f"No historical data found for network: {network}")
        return {"high": 0, "medium": 0, "low": 0}
    
    # Prepare prompt with historical data
    prompt = f"""
    You are an expert cryptocurrency gas fee predictor. 
    Analyze the following historical gas fee data for {network} and predict tomorrow's gas fees.
    Provide your prediction in JSON format with high, medium, and low values.
    
    Historical Data:
    {[{
        "timestamp": entry["timestamp"],
        "high": entry.get(f"{mongoDbNetworkName}_high", 0),
        "medium": entry.get(f"{mongoDbNetworkName}_medium", 0), 
        "low": entry.get(f"{mongoDbNetworkName}_low", 0)
    } for entry in history]}
    
    Prediction Guidelines:
    1. Consider daily/weekly patterns
    2. Account for recent trends
    3. Output format: [{{"timestamp": "HH:00", "high": value, "medium": value, "low": value}}, ...] with predictions for each hour of the day (24 predictions total)
    
    Your prediction for tomorrow's {network} gas fees:
    """
    
    try:
        # Get prediction from Gemini
        response = model.generate_content(prompt)
        prediction = response.text
        
        # Parse the response (Gemini may return markdown with JSON)
        if '```json' in prediction:
            prediction = prediction.split('```json')[1].split('```')[0]
            
        # Parse JSON and update timestamps
        prediction_data = json.loads(prediction)
        tomorrow = datetime.utcnow() + timedelta(days=1)
        
        # Ensure each entry has a valid timestamp
        for i, entry in enumerate(prediction_data):
            hour = i % 24
            timestamp = tomorrow.replace(hour=hour, minute=0, second=0, microsecond=0)
            entry["timestamp"] = timestamp.isoformat()
            entry["date"] = timestamp.isoformat()  # Add a `date` field for frontend compatibility
        
        logger.info(f"Prediction data: {prediction_data}")
        return prediction_data
    
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        return []