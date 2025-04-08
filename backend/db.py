from dotenv import load_dotenv
from pymongo import MongoClient
import os

# Load environment variables from .env file
load_dotenv()

# Create MongoDB client and connect to the correct DB and collection
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
gas_collection = db[os.getenv("MONGO_COLLECTION")]
