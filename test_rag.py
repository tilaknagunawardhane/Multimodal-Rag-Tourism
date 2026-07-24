from src.retrieval.hybrid import generate_hybrid_rag_response

if __name__ == "__main__":
    print("Testing Hybrid Multimodal RAG Pipeline...\n")
    
    query = "Tell me about historical places with beautiful architecture and wild animals."
    result = generate_hybrid_rag_response(
        user_text_query=query,
        max_budget_lkr=10000
    )
    
    print("🤖 Generated Response:")
    print(result["llm_response"])