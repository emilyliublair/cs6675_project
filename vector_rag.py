# import openai
# from openai import OpenAI
# from pinecone.exceptions import PineconeApiException
# from pinecone import Pinecone
# from dotenv import load_dotenv
# import os

def get_pinecone_context(query: str) -> str:
    return "Need to make this get context" + query
    # try:
    #     results = dense_index.search(
    #         namespace="example-namespace",
    #         query={
    #             "top_k": 10,
    #             "inputs": {
    #                 'text': query
    #             }
    #         }
    #     )
        
    #     try:
    #         reranked_results = dense_index.search(
    #             namespace="example-namespace",
    #             query={
    #                 "top_k": 10,
    #                 "inputs": {
    #                     'text': query
    #                 }
    #             },
    #             rerank={
    #                 "model": "bge-reranker-v2-m3",
    #                 "top_n": 10,
    #                 "rank_fields": ["chunk_text"]
    #             }   
    #         )
    #         search_results = reranked_results
    #     except PineconeApiException as e:
    #         # If reranking fails due to token limits, fall back to regular search results
    #         if debug:
    #             print(f"Reranking failed: Using standard search results instead.")
    #         search_results = results
            
    #     context_docs = []
    #     for hit in search_results['result']['hits']:
    #         context_docs.append(f"Category: {hit['fields']['category']}\n{hit['fields']['chunk_text']}")
        
    #     return context_docs
    # except PineconeApiException as e:
    #     print(f"Search failed: {e}")
    #     return []

