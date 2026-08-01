import os
import time
import json
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv

from .structured import search_structured_attractions
from .semantic import search_semantic_text
from .visual import search_visual_similarity
from .intent import extract_search_filters, rewrite_query

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, "../../.env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-3.1-flash-lite"

def generate_hybrid_rag_response(
    user_text_query: str = None,
    image_input = None,
    category: str = None,
    district: str = None,
    max_budget_lkr: int = None,
    chat_history: list = None
):

    """
    Executes hybrid RAG pipeline with Query Reformulation for Multi-Turn Memory, conditional intent extraction,
    dynamic SQL querying, text & image vector retrieval, and conversational synthesis.
    """

    context_blocks = []
    retrieved_metadata = {
        "applied_filters": {},
        "structured": [],
        "semantic": [],
        "visual": []
    }

    # 0. Query Reformulation for Multi-Turn Memory
    standalone_query = user_text_query
    if chat_history and user_text_query:
        standalone_query = rewrite_query(user_text_query, chat_history)
        retrieved_metadata["standalone_query"] = standalone_query

    # 1. Parameter Priority & Intent Extraction
    extracted_intent = {}
    if standalone_query:
        extracted_intent = extract_search_filters(standalone_query)

    # priority: Manual frontend filter > Extracted NL intent > None
    final_category = category if category is not None else extracted_intent.get("category")
    final_district = district if district is not None else extracted_intent.get("district")
    final_budget = max_budget_lkr if max_budget_lkr is not None else extracted_intent.get("max_budget_lkr")

    image_is_needed = extracted_intent.get("image_is_needed", True)

    retrieved_metadata["applied_filters"] = {
        "category": final_category,
        "district": final_district,
        "max_budget_lkr": final_budget
    }
    
    retrieved_metadata["image_is_needed"] = image_is_needed

    # 2. structured relationaldb Retrieval
    db_results = search_structured_attractions(
        category=final_category,
        district=final_district,
        max_budget_lkr=final_budget
    )
    retrieved_metadata["structured"] = db_results
    
    filter_summary = ", ".join([f"{k}: {v}" for k, v in retrieved_metadata["applied_filters"].items() if v is not None])
    filter_header = f" (Applied Filters: {filter_summary})" if filter_summary else " (No SQL Filters Applied)"
    context_blocks.append(f"--- Relational Database Facts{filter_header} ---\n{db_results}")

    # 3. semantic Txt vector search 
    if standalone_query:
        text_results = search_semantic_text(standalone_query, top_k=3)
        retrieved_metadata["semantic"] = text_results
        descriptions = [f"Attraction ID: {res['attraction_id']} | Details: {res['text']}" for res in text_results]
        context_blocks.append(f"--- Semantic Text Context ---\n" + "\n".join(descriptions))

    # 4. visual Img Vector Search
    if image_input is not None:
        visual_results = search_visual_similarity(image_input, top_k=2)
        retrieved_metadata["visual"] = visual_results
        img_info = [f"Visually Matching Attraction ID: {res['attraction_id']} (Score: {res['similarity_score']})" for res in visual_results]
        context_blocks.append(f"--- Visual Similarity Context ---\n" + "\n".join(img_info))

    # 5. format chat history for the LLM
    history_block = ""
    if chat_history:
        history_msgs = [f"{'Traveler' if msg['role'] == 'user' else 'LankaGuide AI'}: {msg['content']}" for msg in chat_history[-4:]]
        history_block = "==================================================\nRECENT CONVERSATION HISTORY\n==================================================\n" + "\n\n".join(history_msgs) + "\n\n"

    # 6. build augmented prompt
    full_context = "\n\n".join(context_blocks)
    
    prompt = f"""
        You are "LankaGuide AI", a friendly, engaging, and knowledgeable Sri Lanka Tourism Assistant.
        Your goal is to answer the user's query using a perfect balance of a warm, conversational tone and clean, structured formatting.

        {history_block}==================================================
        RETRIEVED CONTEXT FROM DATABASES
        ==================================================
        {full_context}
        ==================================================

        TRAVELER QUERY:
        {user_text_query if user_text_query else "Describe the best tourist destinations matching the provided visual image and constraints."}

        GUIDELINES FOR YOUR RESPONSE:
        1. NATURAL CONVERSATIONAL STYLE:
        - Write like an enthusiastic local expert giving personal travel recommendations in a conversation.
        - Start with a short, welcoming opening sentence acknowledging the traveler's request.
        - Present destinations using clear Markdown sub-headings (e.g., `### Destination Name`).
        - Use fluid paragraphs and natural sentences rather than rigid, bulleted key-value lists.
        - Smoothly weave factual details (such as district, opening hours, entrance fees, and ideal visiting seasons) straight into your prose.
        - If an entrance fee is 0 LKR, naturally mention that admission is free.

        2. STRICT GROUNDING:
        - Rely ONLY on the information provided in the retrieved context above. Do NOT introduce external facts, assumptions, or hallucinations.

        3. HIDE INTERNAL METADATA:
        - NEVER mention internal technical terms or database IDs (e.g., "B001", "T001", "chunk", "SQL"). Always refer to destinations by their actual names.

        4. FRIENDLY FALLBACK:
        - If no attractions in the context match the traveler's request, respond warmly explaining that you don't have matching destinations in your guide database right now.

        5. MEMORY CONTINUITY: 
        - Read the "RECENT CONVERSATION HISTORY" block above to ensure your answer flows naturally as a continuation of the chat.

        ANSWER:
    """

    max_retries = 4
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            break
        except (genai_errors.ServerError, genai_errors.ClientError) as e:
            retryable = getattr(e, 'status_code', None) in (429, 503)
            if retryable and attempt < max_retries - 1:
                wait = 2 ** attempt
                print(f"[Gemini] {e.status_code} - retrying in {wait}s...")
                time.sleep(wait)
            else:
                raise
    
    # debug
    print("\n" + "="*60)
    print("[Retrieved Metadata]")
    print("="*60)
    print(json.dumps(retrieved_metadata, indent=2, default=str))
    print("="*60)
    return {
        "llm_response": response.text,
        "retrieved_context": retrieved_metadata
    }

    return {
        "llm_response": response.text,
        "retrieved_context": retrieved_metadata
    }