from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from bson import ObjectId
from vector_rag import intake_question
from init import connect_to_mongo
from concurrent.futures import ThreadPoolExecutor
import time

app = Flask(__name__)
CORS(app)

# MongoDB connection
posts_collection = connect_to_mongo()

# Create a thread pool executor
thread_pool = ThreadPoolExecutor(max_workers=4)  # Adjust number of workers as needed

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
        
        llm_response = intake_question(result['description'], "chatgpt")
        
        return jsonify({'post': serialize_post(result), 'answer': llm_response})
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