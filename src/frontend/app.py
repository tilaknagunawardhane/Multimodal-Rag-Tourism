import sys
import os
import streamlit as st
from PIL import Image

# Ensure the app can find the src module when run from any directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.retrieval.hybrid import generate_hybrid_rag_response

# Helper to find images for retrieved attractions
def get_images_for_attractions(attraction_ids):
    img_dir = os.path.join(ROOT_DIR, "data", "images")
    found_images = []
    if os.path.exists(img_dir):
        for img_file in os.listdir(img_dir):
            if any(img_file.startswith(aid + "_") for aid in attraction_ids):
                found_images.append(os.path.join(img_dir, img_file))
    # Limit to max 4 images to avoid cluttering the chat
    return found_images[:4]

# --- Page Configuration ---
st.set_page_config(
    page_title="Sri Lanka Tourism AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Modern UI CSS Injection ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700&display=swap');

    /* Global Font */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif !important;
    }

    /* Background and Text Colors */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%);
        color: #f8fafc;
    }

    /* Hide Streamlit Header & Footer for a native app feel */
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.4) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Gradient Titles */
    h1 {
        background: -webkit-linear-gradient(45deg, #38bdf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    h2, h3 {
        color: #e2e8f0 !important;
        font-weight: 500;
    }

    /* Chat Message Glassmorphism */
    .stChatMessage {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
        backdrop-filter: blur(8px) !important;
    }

    /* Avatar adjustments */
    [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, #10b981, #059669) !important;
    }
    [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    }

    /* Customizing the Button */
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 14px 0 rgba(99, 102, 241, 0.39) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6) !important;
    }

    /* File Uploader styling */
    [data-testid="stFileUploadDropzone"] {
        background: rgba(255,255,255,0.02) !important;
        border: 2px dashed rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploadDropzone"]:hover {
        border-color: #3b82f6 !important;
        background: rgba(59, 130, 246, 0.05) !important;
    }
    
    /* Input Chat Box */
    [data-testid="stChatInput"] {
        border: 1px solid rgba(255,255,255,0.1) !important;
        background: rgba(15, 23, 42, 0.7) !important;
        border-radius: 16px !important;
    }
</style>
""", unsafe_allow_html=True)

# --- Initialize Chat History in Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Sidebar Controls (Structured & Visual Inputs) ---
with st.sidebar:
    st.markdown("<h1>✨ Control Panel</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8;'>Fine-tune your RAG retrieval parameters.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    # Structured Query Control
    st.subheader("💰 Maximum Budget (LKR)")
    max_budget = st.slider("Select maximum entrance fee:", min_value=0, max_value=20000, value=15000, step=500)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Visual Query Control
    st.subheader("📸 Visual Search")
    uploaded_image = st.file_uploader("Upload an attraction photo", type=["jpg", "png", "jpeg"])
    
    if uploaded_image is not None:
        st.image(uploaded_image, caption="Uploaded Image", use_container_width=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()

# --- Main Chat Interface ---
st.markdown("<h1>🇱🇰 Explore Sri Lanka Tourism</h1>", unsafe_allow_html=True)
st.markdown("<p style='color: #cbd5e1; font-size: 1.1rem;'>Ask natural language questions about waterfalls, national parks, historical temples, or beaches. Our AI will synthesize facts, descriptions, and visual matches.</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

# Display existing chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Render related images if present
        if msg.get("images"):
            st.markdown("<p style='color: #cbd5e1; font-size: 0.9rem; margin-top: 10px;'>📸 Related Database Images:</p>", unsafe_allow_html=True)
            cols = st.columns(len(msg["images"]))
            for col, img_path in zip(cols, msg["images"]):
                with col:
                    st.image(img_path, use_container_width=True)
        
        # If the AI message contains retrieved metadata context, display it in an expander
        if msg["role"] == "assistant" and "context" in msg and msg["context"]:
            with st.expander("🔍 View Retrieved Database Metadata"):
                st.json(msg["context"])

# --- Handle User Chat Input ---
if prompt := st.chat_input("E.g., 'What are some quiet historical temples with beautiful architecture?'"):
    
    # 1. Add user message to UI and session state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call backend Hybrid RAG pipeline
    with st.chat_message("assistant"):
        with st.spinner("Searching vector space and executing SQL..."):
            
            # Prepare image if uploaded
            img_input = Image.open(uploaded_image) if uploaded_image else None
            
            # Fetch response from backend
            try:
                rag_result = generate_hybrid_rag_response(
                    user_text_query=prompt,
                    image_input=img_input,
                    max_budget_lkr=max_budget
                )
                
                llm_text = rag_result["llm_response"]
                context_data = rag_result["retrieved_context"]
                
                # Render LLM Answer
                st.markdown(llm_text)
                
                # Extract candidate attraction IDs from context
                candidate_ids = set()
                if "semantic" in context_data:
                    for item in context_data["semantic"]:
                        if "attraction_id" in item:
                            candidate_ids.add(item["attraction_id"])
                if "visual" in context_data:
                    for item in context_data["visual"]:
                        if "attraction_id" in item:
                            candidate_ids.add(item["attraction_id"])
                            
                # Map attraction_id to name from structured context
                id_to_name = {}
                if "structured" in context_data:
                    for row in context_data["structured"]:
                        if "attraction_id" in row and "name" in row:
                            id_to_name[row["attraction_id"]] = row["name"]
                            
                # Filter to only show images of places the LLM actually talked about
                attraction_ids = set()
                for aid in candidate_ids:
                    name = id_to_name.get(aid)
                    if name:
                        # Check if the main part of the name (e.g. "Sigiriya", "Temple", "Mirissa") is in the response
                        first_word = name.split()[0].lower()
                        if first_word in llm_text.lower():
                            attraction_ids.add(aid)
                    else:
                        attraction_ids.add(aid) # Fallback if we don't have the name mapping
                            
                # Fetch and display images
                images_to_show = []
                if attraction_ids:
                    images_to_show = get_images_for_attractions(attraction_ids)
                    if images_to_show:
                        st.markdown("<p style='color: #cbd5e1; font-size: 0.9rem; margin-top: 10px;'>📸 Related Database Images:</p>", unsafe_allow_html=True)
                        cols = st.columns(len(images_to_show))
                        for col, img_path in zip(cols, images_to_show):
                            with col:
                                st.image(img_path, use_container_width=True)
                
                # Render Metadata Expander
                with st.expander("🔍 View Retrieved Database Metadata"):
                    st.json(context_data)
                
                # Save assistant response and context to session state
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": llm_text,
                    "context": context_data,
                    "images": images_to_show
                })
                
            except Exception as e:
                error_msg = f"❌ An error occurred during retrieval: {str(e)}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})