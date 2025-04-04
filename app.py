from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from vector_rag import get_pinecone_context, initialize_pinecone
from dotenv import load_dotenv
from pymongo import MongoClient
from bson import ObjectId
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure CORS to allow requests from your frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],  # Your frontend URL
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize MongoDB
try:
    client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    db = client["piazzahut"]
    posts_collection = db["posts"]
    print("Successfully connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Initialize Pinecone on startup
initialize_pinecone()

@app.route("/", methods=["GET", "POST"])
def index():
    output_text = ""
    if request.method == "POST":
        input_text = request.form["input_text"]
        output_text = get_pinecone_context(input_text)
    return render_template("index.html", output_text=output_text)

@app.route("/query", methods=["POST", "OPTIONS"])
def query():
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        data = request.json
        if not data or 'query' not in data:
            return jsonify({"error": "No query provided"}), 400
        
        query_text = data['query']
        top_k = data.get('top_k', 5)  # Optional parameter with default value
        
        # Get context from vector store
        results = get_pinecone_context(
            query=query_text,
            top_k=top_k
        )
        
        return jsonify({
            "query": query_text,
            "results": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/post/<post_id>", methods=["GET", "OPTIONS"])
def get_post(post_id):
    if request.method == "OPTIONS":
        return "", 200
        
    try:
        # Validate post_id format
        if not ObjectId.is_valid(post_id):
            return jsonify({"error": "Invalid post ID"}), 400

        # Find the post in MongoDB
        post = posts_collection.find_one({"_id": ObjectId(post_id)})
        
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        # Convert ObjectId to string for JSON serialization
        post["_id"] = str(post["_id"])
        
        # Get similar posts using vector search
        if post.get("description"):
            similar_posts = get_pinecone_context(
                query=post["description"],
                top_k=3  # Get 3 similar posts
            )
        else:
            similar_posts = []
        
        return jsonify({
            "post": post,
            "similar_posts": similar_posts
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3000')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

if __name__ == "__main__":
    app.run(debug=True)
