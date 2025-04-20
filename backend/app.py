from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from bson import ObjectId
from vector_rag import intake_question, ask_query, generate_response
from init import connect_to_mongo
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)
CORS(app)

# MongoDB connection
posts_collection = connect_to_mongo("posts")
answers_collection = connect_to_mongo("answers")

# Create a thread pool executor
thread_pool = ThreadPoolExecutor(max_workers=4)  # Adjust number of workers as needed

# Helper function to convert MongoDB ObjectId to string
def serialize_post(post):
    if post is None:
        return None
    post['_id'] = str(post['_id'])
    if 'answer' in post and post['answer']:
        post['answer'] = str(post['answer'])
    return post

def get_feedback_context():
    """Get context from previous answers' feedback and edits to improve future responses"""
    try:
        # Get the most recent answers with significant feedback or edits
        recent_answers = answers_collection.find({
            "$or": [
                {"upvotes": {"$gt": 0}},
                {"downvotes": {"$gt": 0}},
                {"edited": True}
            ]
        }).sort("publishDate", -1).limit(5)
        
        feedback_context = []
        for answer in recent_answers:
            if answer.get('upvotes', 0) > answer.get('downvotes', 0):
                feedback_context.append({
                    "type": "positive",
                    "description": answer.get('description', ''),
                    "feedback": "This answer was well-received by users"
                })
            elif answer.get('downvotes', 0) > answer.get('upvotes', 0):
                feedback_context.append({
                    "type": "negative",
                    "description": answer.get('description', ''),
                    "feedback": "This answer was not well-received by users"
                })
            elif answer.get('edited', False):
                feedback_context.append({
                    "type": "edited",
                    "description": answer.get('description', ''),
                    "feedback": f"This answer was edited by {answer.get('editedBy', 'Teacher')} to improve clarity and accuracy"
                })
        
        return feedback_context
    except Exception as e:
        print(f"Error getting feedback context: {str(e)}")
        return []

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

@app.route('/post', methods=['POST'])
def create_post():
    try:
        post_data = request.json
        post_data["publishDate"] = datetime.now()

        # Get feedback context from previous answers
        feedback_context = get_feedback_context()
        
        # Generate AI answer with feedback context and get relevant documents
        context_docs = ask_query(post_data['description'], False)
        llm_response = generate_response(
            post_data['description'], 
            context_docs,
            "chatgpt",
            feedback_context=feedback_context
        )
        
        # Create answer document with vote counts and feedback tracking
        answer_data = {
            "description": llm_response,
            "title": "AI-generated answer",
            "publishDate": datetime.now(),
            "upvotes": 0,
            "downvotes": 0,
            "feedback_context": feedback_context,  # Store the context used for this answer
            "relevant_documents": context_docs  # Store the relevant documents
        }
        
        # Insert answer first
        answer_result = answers_collection.insert_one(answer_data)
        
        # Link answer to post
        post_data["answer"] = answer_result.inserted_id
        
        # Insert post
        result = posts_collection.insert_one(post_data)
        post_data["_id"] = str(result.inserted_id)
        
        return jsonify(serialize_post(post_data))
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/post/<id>', methods=['GET', 'OPTIONS'])
def get_post(id):
    try:
        # Find the post
        post = posts_collection.find_one({"_id": ObjectId(id)})
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        # Find the associated answer if it exists
        answer = None
        if 'answer' in post and post['answer']:
            answer = answers_collection.find_one({"_id": post['answer']})
        
        return jsonify({
            'post': serialize_post(post),
            'answer': serialize_post(answer)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/answer/<id>/upvote', methods=['POST'])
def upvote_answer(id):
    try:
        result = answers_collection.update_one(
            {"_id": ObjectId(id)},
            {"$inc": {"upvotes": 1}}
        )
        if result.modified_count == 0:
            return jsonify({"error": "Answer not found"}), 404
        return jsonify({"message": "Upvote successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/answer/<id>/downvote', methods=['POST'])
def downvote_answer(id):
    try:
        result = answers_collection.update_one(
            {"_id": ObjectId(id)},
            {"$inc": {"downvotes": 1}}
        )
        if result.modified_count == 0:
            return jsonify({"error": "Answer not found"}), 404
        return jsonify({"message": "Downvote successful"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/answer/<id>/edit', methods=['POST'])
def edit_answer(id):
    try:
        answer_data = request.json
        result = answers_collection.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "description": answer_data["description"],
                "edited": True,
                "editedBy": answer_data.get("editedBy", "Teacher"),
                "editDate": datetime.now()
            }}
        )
        if result.modified_count == 0:
            return jsonify({"error": "Answer not found"}), 404
        return jsonify({"message": "Answer updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Benchmark endpoints
@app.route('/benchmark/single', methods=['GET'])
def benchmark_single():
    try:
        # Get parameters for benchmarking
        num_calls = int(request.args.get('num_calls', 1))
        model = request.args.get('model', 'chatgpt')  # Default to chatgpt
        question = request.args.get('question', "in lab3 how can I find the end of the parent's user stack?")
        
        start_time = time.time()
        
        # Run the specified number of sequential calls
        results = []
        for _ in range(num_calls):
            call_start = time.time()
            response = intake_question(question, model)
            call_end = time.time()
            
            results.append({
                'response': response[:100] + "...",  # Just store a snippet to save space
                'time_taken': call_end - call_start
            })
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        times = [r['time_taken'] for r in results]
        stats = {
            'total_time': total_time,
            'average_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'num_calls': num_calls,
            'model': model,
            'threading': 'single'
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/benchmark/threaded', methods=['GET'])
def benchmark_threaded():
    try:
        # Get parameters for benchmarking
        num_calls = int(request.args.get('num_calls', 1))
        model = request.args.get('model', 'chatgpt')  # Default to chatgpt
        question = request.args.get('question', "in lab3 how can I find the end of the parent's user stack?")
        
        start_time = time.time()
        
        # Define the function to run in each thread
        def run_intake(idx):
            call_start = time.time()
            response = intake_question(question, model)
            call_end = time.time()
            
            return {
                'index': idx,
                'response': response[:100] + "...",  # Just store a snippet to save space
                'time_taken': call_end - call_start
            }
        
        # Execute calls in parallel
        futures = []
        for i in range(num_calls):
            future = thread_pool.submit(run_intake, i)
            futures.append(future)
        
        # Wait for all to complete and collect results
        results = []
        for future in futures:
            results.append(future.result())
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate statistics
        times = [r['time_taken'] for r in results]
        stats = {
            'total_time': total_time,
            'average_time': sum(times) / len(times),
            'min_time': min(times),
            'max_time': max(times),
            'num_calls': num_calls,
            'model': model,
            'threading': 'multi'
        }
        
        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/benchmark/compare', methods=['GET'])
def benchmark_compare():
    try:
        # Get parameters for benchmarking
        num_calls = int(request.args.get('num_calls', 3))
        model = request.args.get('model', 'chatgpt')
        question = request.args.get('question', "in lab3 how can I find the end of the parent's user stack?")
        
        # Run single-threaded benchmark
        single_start = time.time()
        single_results = []
        
        for _ in range(num_calls):
            call_start = time.time()
            response = intake_question(question, model)
            call_end = time.time()
            
            single_results.append({
                'response_snippet': response[:50] + "...",
                'time_taken': call_end - call_start
            })
        
        single_end = time.time()
        single_total = single_end - single_start
        
        # Run multi-threaded benchmark
        multi_start = time.time()
        
        # Define the function to run in each thread
        def run_intake():
            call_start = time.time()
            response = intake_question(question, model)
            call_end = time.time()
            
            return {
                'response_snippet': response[:50] + "...",
                'time_taken': call_end - call_start
            }
        
        # Execute calls in parallel
        futures = []
        for _ in range(num_calls):
            future = thread_pool.submit(run_intake)
            futures.append(future)
        
        # Wait for all to complete and collect results
        multi_results = []
        for future in futures:
            multi_results.append(future.result())
        
        multi_end = time.time()
        multi_total = multi_end - multi_start
        
        # Calculate statistics
        single_times = [r['time_taken'] for r in single_results]
        multi_times = [r['time_taken'] for r in multi_results]
        
        # Calculate improvement percentage
        improvement = ((single_total - multi_total) / single_total) * 100
        
        # Return comparison results
        comparison = {
            'single_threaded': {
                'total_time': single_total,
                'average_time': sum(single_times) / len(single_times),
                'min_time': min(single_times),
                'max_time': max(single_times),
            },
            'multi_threaded': {
                'total_time': multi_total,
                'average_time': sum(multi_times) / len(multi_times),
                'min_time': min(multi_times),
                'max_time': max(multi_times),
            },
            'improvement_percentage': improvement,
            'parameters': {
                'num_calls': num_calls,
                'model': model,
                'question': question
            }
        }
        
        return jsonify(comparison)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True, threaded=True)