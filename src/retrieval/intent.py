# Parses user natural language queries into structured JSON parameters for relational filtering.
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
    Uses Gemini Flash in JSON mode to extract category, district, or budget constraints from user text.
    STRICT RULE: Returns null for any parameter not explicitly mentioned or directly implied.
    """
    if not user_query:
        return {"category": None, "district": None, "max_budget_lkr": None}

    prompt = f"""
    Analyze the following tourist query and extract structured filter criteria.
    
    Allowed Categories: Beach, Mountain, National Park, Temple, Historical Site, Waterfall.
    
    CRITICAL RULES:
    1. Do NOT assume or invent default values.
    2. If a attribute (category, district, or max_budget_lkr) is NOT explicitly mentioned or clearly stated in the query, set its value to null.
    3. For budget/fees, extract numerical values in LKR. If the user mentions "free", set max_budget_lkr to 0.

    User Query: "{user_query}"

    Respond ONLY with a JSON object matching this structure:
    {{
        "category": string or null,
        "district": string or null,
        "max_budget_lkr": integer or null
    }}
    """

    try:
        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        data = json.loads(response.text)
        return {
            "category": data.get("category"),
            "district": data.get("district"),
            "max_budget_lkr": data.get("max_budget_lkr")
        }
    except Exception as e:
        print(f"[Intent Extraction Error]: {e}")
        return {"category": None, "district": None, "max_budget_lkr": None}