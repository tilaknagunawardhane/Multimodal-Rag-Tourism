import os
import json
from src.retrieval.hybrid import generate_hybrid_rag_response

def print_test_result(test_name, result):
    """
    Helper function to display applied filters, retrieved context metadata,
    and the final LLM response in a clean format.
    """
    print(f"\n{'='*80}")
    print(f" TEST CASE: {test_name}")
    print(f"{'='*80}")
    
    print("\n[1. RETRIEVED METADATA & CONTEXT]")
    print(json.dumps(result["retrieved_context"], indent=2, default=str))
    
    print("\n[2. LLM GENERATED RESPONSE]")
    print(result["llm_response"])
    print(f"{'='*80}\n")

if __name__ == "__main__":
    print("Starting Multimodal RAG Pipeline Evaluation...\n")

    # =========================================================================
    # TEST CASE 1: Natural Language Intent Extraction
    # Tests Gemini Flash extracting Category="Temple", District="Kandy", Budget=0
    # =========================================================================
    # query_1 = "Tell me about free temples in Kandy that I can visit."
    # res_1 = generate_hybrid_rag_response(
    #     user_text_query=query_1
    # )
    # print_test_result("1. NL Query Intent Extraction (Free Temples in Kandy)", res_1)


    # =========================================================================
    # TEST CASE 2: Explicit Manual Filter Overrides
    # Tests manually passing frontend parameters (skips AI intent extraction)
    # =========================================================================
    query_2 = "What are the best places to relax and swim?"
    res_2 = generate_hybrid_rag_response(
        user_text_query=query_2,
        category="Beach",
        district="Galle",
        max_budget_lkr=500
    )
    print_test_result("2. Explicit Manual Filters (Beach in Galle <= 500 LKR)", res_2)


    # =========================================================================
    # TEST CASE 3: Unconstrained Semantic Text Search
    # Tests open-ended vector similarity when no SQL filters are passed or extracted
    # =========================================================================
    # query_3 = "Show me places with wildlife, ancient rock fortresses, and lion gates."
    # res_3 = generate_hybrid_rag_response(
    #     user_text_query=query_3
    # )
    # print_test_result("3. Unconstrained Semantic Search", res_3)


    # =========================================================================
    # TEST CASE 4: Multimodal Search (Image + Text + Budget)
    # Tests CLIP image similarity search combined with text query and budget cap
    # =========================================================================
    # test_image_path = "data/images/N001_1.jpg"  # Sample Yala National Park image
    # query_4 = "I want to see wild animals similar to this photo under 10000 LKR."
    # res_4 = generate_hybrid_rag_response(
    #     user_text_query=query_4,
    #     image_input=test_image_path,
    #     max_budget_lkr=10000
    # )
    # print_test_result("4. Multimodal Search (Image + Text + Budget)", res_4)


    # =========================================================================
    # TEST CASE 5: Fallback Test (No SQL Matches Found)
    # Tests how the LLM handles queries where SQL criteria return zero results
    # =========================================================================
    # query_5 = "Are there any beaches here?"
    # res_5 = generate_hybrid_rag_response(
    #     user_text_query=query_5,
    #     category="Beach",
    #     district="Nuwara Eliya"  # No beaches exist in Nuwara Eliya district
    # )
    # print_test_result("5. Fallback Test (No Matching Destinations in DB)", res_5)