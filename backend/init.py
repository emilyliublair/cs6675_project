from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os
from pinecone import Pinecone

load_dotenv()


def connect_to_mongo(collection = "posts"):
    try:
        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client["piazzahut"]
        col = db[collection]
        return col
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")

def connect_to_pinecone():
    try:
        pineAPI = os.getenv("PINECONE_API")
        pc = Pinecone(api_key=pineAPI)
        return pc
    except Exception as e:
        print(f"Could not initialize Pinecone: {e}")