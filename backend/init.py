from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os
import pinecone

load_dotenv()


def connect_to_mongo():
    try:
        client = MongoClient(os.getenv("MONGODB_URI"))
        db = client["piazzahut"]
        posts_collection = db["posts"]
        return posts_collection
    except ConnectionFailure as e:
        print(f"Could not connect to MongoDB: {e}")

# def connect_to_pinecone():
#     try:
#         pinecone.init(
#             api_key=os.getenv("PINECONE_API_KEY"),
#             environment=os.getenv("PINECONE_ENVIRONMENT")
#         )
#         vector_rag = VectorRAG()
#         return vector_rag
#     except Exception as e:
#         print(f"Could not initialize Pinecone: {e}")