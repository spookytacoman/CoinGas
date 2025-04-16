from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
import logging

from .db import gas_collection

# Configure logging
logger = logging.getLogger("historical")

# Create a router for historical endpoints
router = APIRouter(
    prefix="/history",
    tags=["historical"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{network}")
def get_network_history(network: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get historical gas fee data for a specific network.
    
    Args:
        network: The network to get history for (bitcoin, ethereum, or solana)
        limit: The maximum number of entries to return (default: 100)
        
    Returns:
        List[Dict[str, Any]]: A list of historical gas fee data for the specified network
    """
    # Map network names to their fee fields
    fee_fields = {
        "bitcoin": ("btc_high", "btc_medium", "btc_low"),
        "ethereum": ("eth_high", "eth_medium", "eth_low"),
        "solana": ("sol_high", "sol_medium", "sol_low")
    }
    
    if network not in fee_fields:
        raise HTTPException(status_code=400, detail=f"Invalid network. Must be one of: {', '.join(fee_fields.keys())}")
    
    high_field, medium_field, low_field = fee_fields[network]
    
    # Get historical data from MongoDB
    try:
        # Get data from the last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        history = list(gas_collection.find(
            {"timestamp": {"$gte": thirty_days_ago.isoformat()}},
            {
                "timestamp": 1,
                high_field: 1,
                medium_field: 1,
                low_field: 1,
                "_id": 0
            }
        ).sort("timestamp", -1).limit(limit))
        
        logger.info(f"Retrieved {len(history)} historical records for {network}")
        
        # Format the data for the frontend
        formatted_history = []
        for doc in history:
            formatted_history.append({
                "date": doc["timestamp"],
                "high": doc[high_field],
                "medium": doc[medium_field],
                "low": doc[low_field]
            })
        
        return formatted_history
    
    except Exception as e:
        logger.error(f"Error retrieving historical data for {network}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving historical data: {str(e)}")

@router.get("/")
def get_all_history(limit: int = 100) -> List[Dict[str, Any]]:
    """
    Get historical gas fee data for all networks.
    
    Args:
        limit: The maximum number of entries to return (default: 100)
        
    Returns:
        List[Dict[str, Any]]: A list of historical gas fee data
    """
    try:
        history = list(gas_collection.find().sort("timestamp", -1).limit(limit))
        for doc in history:
            doc["_id"] = str(doc["_id"])
        
        logger.info(f"Retrieved {len(history)} historical records")
        return history
    
    except Exception as e:
        logger.error(f"Error retrieving historical data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving historical data: {str(e)}") 