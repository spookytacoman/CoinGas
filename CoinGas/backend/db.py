from dotenv import load_dotenv
from pymongo import MongoClient
from typing import Optional, Dict, Any, List
import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("db")

# Load environment variables from .env file
load_dotenv()

# Create MongoDB client and connect to the correct DB and collection
# Use default values if environment variables are not set
mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
mongo_db = os.getenv("MONGO_DB", "gas_tracker")
mongo_collection = os.getenv("MONGO_COLLECTION", "gas_data")

# Global MongoDB client and collection
client: Optional[MongoClient] = None
gas_collection = None

def get_mongo_client() -> MongoClient:
    """
    Get or create a MongoDB client with connection pooling.
    
    Returns:
        MongoClient: A configured MongoDB client
    """
    global client
    if client is None:
        try:
            # Connect to MongoDB with a timeout and connection pooling
            client = MongoClient(
                mongo_uri, 
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            # Test the connection
            client.server_info()
            logger.info(f"✅ Connected to MongoDB: {mongo_uri}")
        except Exception as e:
            logger.error(f"❌ MongoDB connection error: {e}")
            # Don't raise the exception, just return None
            return None
    
    return client

def get_gas_collection():
    """
    Get the gas collection from MongoDB.
    
    Returns:
        Collection: The MongoDB collection for gas data
    """
    global gas_collection
    
    if gas_collection is None:
        try:
            # Get the MongoDB client
            mongo_client = get_mongo_client()
            
            if mongo_client is None:
                logger.error("❌ MongoDB collection error: Could not get MongoDB client")
                return MockCollection()
            
            # Get the database and collection
            db = mongo_client[mongo_db]
            gas_collection = db[mongo_collection]
            
            # Test the collection
            gas_collection.find_one()
            logger.info(f"✅ Connected to MongoDB collection: {mongo_collection}")
            
        except Exception as e:
            logger.error(f"❌ MongoDB collection error: {e}")
            logger.info("Using mock data instead")
            return MockCollection()
    
    return gas_collection

class MockCollection:
    """
    A mock collection for when MongoDB is not available.
    """
    def __init__(self):
        self.data = []
    
    def insert_one(self, document):
        """
        Insert a document into the mock collection.
        
        Args:
            document: The document to insert
            
        Returns:
            InsertOneResult: A mock result
        """
        self.data.append(document)
        return type('InsertOneResult', (), {'inserted_id': 'mock_id'})()
    
    def find_one(self, filter=None, sort=None):
        """
        Find one document in the mock collection.
        
        Args:
            filter: The filter to apply
            sort: The sort to apply
            
        Returns:
            dict: The document or None
        """
        if not self.data:
            return None
        return self.data[-1]
    
    def find(self, filter=None, sort=None, limit=None):
        """
        Find documents in the mock collection.
        
        Args:
            filter: The filter to apply
            sort: The sort to apply
            limit: The limit to apply
            
        Returns:
            list: The documents
        """
        return self.data

# Initialize the gas collection
gas_collection = get_gas_collection()
