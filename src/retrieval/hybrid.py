import os
import time
from google import genai
from google.genai import errors as genai_errors
from dotenv import load_dotenv

from .structured import run_structured_query
from .semantic import search_semantic_text
from .visual import search_visual_similarity

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, "../../.env"))

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

GEMINI_MODEL = "gemini-3.1-flash-lite"  # confirmed available from models.list()

def generate_hybrid_rag_response(user_text_query: str = None, image_input = None, max_budget_lkr: int = None):
    """
    Combines structured filtering, text vector search, and image similarity search into a single LLM prompt.
    """
    context_blocks = []
    retrieved_metadata = {
        "structured": [],
        "semantic": [],
        "visual": []
    }

    # 1. Structured DB Retrieval
    if max_budget_lkr is not None:
        sql = f"SELECT attraction_id, name, category, district, entrance_fee_lkr, opening_hours FROM attractions WHERE entrance_fee_lkr <= {max_budget_lkr};"
        db_results = run_structured_query(sql)
        retrieved_metadata["structured"] = db_results
        context_blocks.append(f"--- Structured Facts (Budget <= {max_budget_lkr} LKR) ---\n{db_results}")
    else:
        # Fetch all database facts for general context matching
        db_results = run_structured_query("SELECT * FROM attractions;")
        context_blocks.append(f"--- Relational Database Facts ---\n{db_results}")

    # 2. Semantic Text Search
    if user_text_query:
        text_results = search_semantic_text(user_text_query, top_k=2)
        retrieved_metadata["semantic"] = text_results
        descriptions = [res['text'] for res in text_results]
        context_blocks.append(f"--- Semantic Text Context ---\n" + "\n".join(descriptions))

    # 3. Visual Image Search
    if image_input is not None:
        visual_results = search_visual_similarity(image_input, top_k=2)
        retrieved_metadata["visual"] = visual_results
        img_info = [f"Matches Attraction ID: {res['attraction_id']} (Score: {res['similarity_score']})" for res in visual_results]
        context_blocks.append(f"--- Visual Image Match Context ---\n" + "\n".join(img_info))

    # Build Augmented Prompt
    full_context = "\n\n".join(context_blocks)
    prompt = f"""
    You are an expert Sri Lanka Tourism Assistant. Answer the user's question accurately using ONLY the context provided below.
    If the context contains visual matches or budget information, synthesize them into a helpful, friendly response.

    {full_context}

    User Question: {user_text_query if user_text_query else "Describe the best tourist destinations matching the provided image and constraints."}
    
    Answer:
    """

 # Generate Response with Gemini — retry on transient 503/429 errors
    max_retries = 4
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )
            break  # success
        except (genai_errors.ServerError, genai_errors.ClientError) as e:
            retryable = getattr(e, 'status_code', None) in (429, 503)
            if retryable and attempt < max_retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s, 8s
                print(f"[Gemini] {e.status_code} — retrying in {wait}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(wait)
            else:
                raise  # re-raise after final attempt or non-retryable error

    return {
        "llm_response": response.text,
        "retrieved_context": retrieved_metadata
    }