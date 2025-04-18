
from dotenv import load_dotenv
from init import connect_to_pinecone
from openai import OpenAI
import os
import re
from pinecone.exceptions import PineconeApiException 
from anthropic import Anthropic

def parse_lab_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    question_match = re.search(r'Question:\s*(.*?)(?=Student Answer:|$)', content, re.DOTALL)
    student_answer_match = re.search(r'Student Answer:\s*(.*?)(?=Instructor Answer:|$)', content, re.DOTALL)
    instructor_answer_match = re.search(r'Instructor Answer:\s*(.*?)(?=Followup Discussions:|$)', content, re.DOTALL)
    followup_match = re.search(r'Followup Discussions:\s*(.*?)$', content, re.DOTALL)
    
    # Extract the content for each section, strip whitespace
    question = question_match.group(1).strip() if question_match else ""
    student_answer = student_answer_match.group(1).strip() if student_answer_match else ""
    instructor_answer = instructor_answer_match.group(1).strip() if instructor_answer_match else ""
    followups = followup_match.group(1).strip() if followup_match else ""
    
    # Create structured document
    return {
        "file_name": os.path.basename(file_path),
        "question": question,
        "student_answer": student_answer,
        "instructor_answer": instructor_answer,
        "followups": followups
    }

def process_lab_files(folder_path):
    results = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            file_path = os.path.join(folder_path, filename)
            parsed_data = parse_lab_file(file_path)
            results.append(parsed_data)
    return results

def format_for_rag(parsed_data, category):
    global num_docs
    rag_documents = []
    
    for i, item in enumerate(parsed_data):
        doc_id = f"rec{num_docs}"
        num_docs += 1
        
        # Format text the same way as before
        formatted_text = f"""Question:{item['question']}
        Student Answer:{item['student_answer']}
        Instructor Answer:{item['instructor_answer']}
        Followup Discussions:{item['followups']}""".strip()
        
        # Create record dictionary
        record = {
            "_id": doc_id,
            "chunk_text": formatted_text,
            "category": category
        }
        
        rag_documents.append(record)
    
    return rag_documents

def ask_query(query, debug):
    try:

        results = dense_index.search(
            namespace="example-namespace",
            query={
                "top_k": 10,
                "inputs": {
                    'text': query
                }
            }
        )
        
        try:
            reranked_results = dense_index.search(
                namespace="example-namespace",
                query={
                    "top_k": 10,
                    "inputs": {
                        'text': query
                    }
                },
                rerank={
                    "model": "bge-reranker-v2-m3",
                    "top_n": 10,
                    "rank_fields": ["chunk_text"]
                }   
            )
            search_results = reranked_results
        except PineconeApiException as e:
            # If reranking fails due to token limits, fall back to regular search results
            if debug:
                print(f"Reranking failed: Using standard search results instead.")
            search_results = results
            
        context_docs = []
        for hit in search_results['result']['hits']:
            context_docs.append(f"Category: {hit['fields']['category']}\n{hit['fields']['chunk_text']}")
        
        return context_docs
    except PineconeApiException as e:
        print(f"Search failed: {e}")
        return []
    
# def generate_response(query, context_docs):
#     # Prepare context from retrieved documents
#     context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
    
#     # Create prompt with context and query
#     prompt = f""" You are an AI assistant for a computer science course. Use the following retrieved documents to answer the question. If you don't know the answer, just say that you don't know, don't try to make up an answer. Context:
#     {context}
#     Question: {query}
#     Answer:
#     """
#     # Call OpenAI API
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",  
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant for a computer science course."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0.3,
#         max_tokens=500
#     )
    
#     return response.choices[0].message.content

def generate_response(query, context_docs, model="chatgpt"):
    context = "\n\n".join([f"Document {i+1}:\n{doc}" for i, doc in enumerate(context_docs)])
    
    prompt = f""" You are an AI assistant for a computer science course. Use the following retrieved documents to answer the question. If you don't know the answer, just say that you don't know, don't try to make up an answer. Context:
    {context}
    Question: {query}
    Answer:
    """
    
    # Select the appropriate model and generate response
    if model == "chatgpt":
        response = openAI_client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "system", "content": "You are a helpful assistant for a computer science course."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    elif model == "claude":
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=1000,
            temperature=0.1,
            system="You are a helpful assistant for a computer science course.",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.content[0].text
    
    else:
        raise ValueError(f"Unsupported model: {model}. Please choose from 'gpt-3.5-turbo', 'gpt-4', or 'claude-3-sonnet'.")



def intake_question(query, model):
    context = ask_query(query, False)
    return generate_response(query, context, model)




def combine_responses(query):
    chatgpt_response = intake_question(query, "chatgpt")
    claude_response = intake_question(query, "claude")
    
    response = openAI_client.chat.completions.create(
            model="gpt-3.5-turbo",  
            messages=[
                {"role": "user", "content": f"Based on these answers formulate a combined response that combines the information of both: {chatgpt_response} and {claude_response}"},
            ],
            temperature=0.1,
            max_tokens=1000
        )
    return response.choices[0].message.content

pc = connect_to_pinecone()
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY") 
openAI_client = OpenAI(api_key=openai_api_key)

claude_api_key = os.getenv("CLAUDE_API_KEY")
anthropic_client = Anthropic(api_key = claude_api_key)

# Create a dense index with integrated embedding
index_name = "dense-index"
if not pc.has_index(index_name):
    pc.create_index_for_model(
        name=index_name,
        cloud="aws",
        region="us-east-1",
        embed={
            "model":"llama-text-embed-v2",
            "field_map":{"text": "chunk_text"}
        }
    )

# print("created index")

# # Variables for parsing
num_docs = 0
labs  = ["lab0", "lab1", "lab2", "lab3"]
records = []

for lab in labs:
    cur_parsed = process_lab_files(f"../data/{lab}")
    cur_raw_docs = format_for_rag(cur_parsed, lab)
    records.extend(cur_raw_docs)

print("Proccesed ", num_docs, "documents")


batch_size = 96
dense_index = pc.Index(index_name)
for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]
    dense_index.upsert_records("example-namespace", batch)

stats = dense_index.describe_index_stats()

print("Done setup of vector rag")

# print(combine_responses("in lab3 how can I find the end of the parent's user stack?"))