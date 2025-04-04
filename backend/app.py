from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from bson import ObjectId
from vector_rag import intake_question
from init import connect_to_mongo

app = Flask(__name__)
CORS(app)

# MongoDB connection
posts_collection = connect_to_mongo()

# Helper function to convert MongoDB ObjectId to string
def serialize_post(post):
    post['_id'] = str(post['_id'])
    return post

# Routes
@app.route('/')
def root():
    return jsonify({"message": "Welcome to PiazzaHut API"})

@app.route('/posts', methods=['GET'])
def get_posts():
    try:
        posts = list(posts_collection.find().sort("publishDate", -1))
        return jsonify([serialize_post(post) for post in posts])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/posts', methods=['POST'])
def create_post():
    try:
        post_data = request.json
        post_data["publishDate"] = datetime.now()
        
        result = posts_collection.insert_one(post_data)
        
        post_data["_id"] = str(result.inserted_id)
        return jsonify(post_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/post/<id>', methods=['GET', 'OPTIONS'])
def get_post(id):
    try:
        result = posts_collection.find_one(filter=ObjectId(id))
        
        llm_response = intake_question(result['description'])
        
        return jsonify({'post': serialize_post(result), 'answer': llm_response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500  
    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
