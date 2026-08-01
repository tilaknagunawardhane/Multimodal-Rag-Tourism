import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(SCRIPT_DIR, "../../.env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)
GEMINI_MODEL = "gemini-3.1-flash-lite"

def extract_search_filters(user_query: str) -> dict:
    """
    Uses Gemini Flash to extract filters and determine if images should be displayed.
    Uses strict JSON Schema enforcement.
    """
    if not user_query:
        return {"category": None, "district": None, "max_budget_lkr": None, "image_is_needed": True}

    prompt = f"""
        Analyze the tourist query and extract structured criteria.
        
        Allowed Categories: Beach, Mountain, National Park, Temple, Historical Site, Waterfall.
        
        CRITICAL RULES:
        1. If an attribute is NOT explicitly mentioned, set it to null.
        2. For budget/fees, extract numerical values in LKR. "free" = 0.
        3. 'image_is_needed': Set to true if the user is asking to discover places, requesting recommendations, or asking to see something. Set to false if it's a purely informational follow-up (e.g., "how much does it cost?", "what should I wear?", "how far is it?").

        User Query: "{user_query}"
    """

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "category": types.Schema(type=types.Type.STRING, nullable=True),
                        "district": types.Schema(type=types.Type.STRING, nullable=True),
                        "max_budget_lkr": types.Schema(type=types.Type.INTEGER, nullable=True),
                        "image_is_needed": types.Schema(type=types.Type.BOOLEAN)
                    },
                    required=["image_is_needed"]
                )
            )
        )
        data = json.loads(response.text)
        return {
            "category": data.get("category"),
            "district": data.get("district"),
            "max_budget_lkr": data.get("max_budget_lkr"),
            "image_is_needed": data.get("image_is_needed", True)
        }
    except Exception as e:
        print(f"[Intent Extraction Error]: {e}")
        return {"category": None, "district": None, "max_budget_lkr": None, "image_is_needed": True}


def rewrite_query(user_query: str, chat_history: list) -> str:
    """
    Rewrites a conversational follow-up query into a standalone search query.
    Example: "How much does it cost?" -> "How much is the entrance fee for Sigiriya?"
    """
    if not chat_history:
        return user_query

    history_text = ""
    # Keep context window small (last 4 interactions) to save tokens and speed
    for msg in chat_history[-4:]: 
        role = "Traveler" if msg["role"] == "user" else "Guide"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""
        Rewrite the following follow-up query into a standalone, self-contained search query. 
        Use the conversation history to replace pronouns (like "it", "there", "the first one") with the actual names of the locations or categories mentioned.
        If the query is already standalone, return it exactly as is.
        DO NOT answer the question. ONLY output the rewritten text.

        Conversation History:
        {history_text}

        Follow-up Query: {user_query}

        Standalone Query:"""

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        print(f"[Query Rewrite Error]: {e}")
        return user_query