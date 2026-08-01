import sys
import os
import streamlit as st
from PIL import Image

# Ensure project root is in Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "../../"))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from src.retrieval.hybrid import generate_hybrid_rag_response
from src.frontend.styles import apply_dark_theme
from src.frontend.components.sidebar import render_sidebar
from src.frontend.components.chat import render_chat_history, render_assistant_response
from src.frontend.utils.image_helpers import get_images_for_attractions
from src.frontend.utils.error_handler import get_friendly_error_message

# --- Page Configuration ---
st.set_page_config(
    page_title="LankaGuideAI",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Theme Styling
apply_dark_theme()

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Render Sidebar & Retrieve Controls ---
filters = render_sidebar()

# --- Main Layout Header (compact) ---
st.markdown("<h1>LankaGuide AI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='color:#475569; font-size:0.95rem; margin-top:0;'>"
    "Ask about waterfalls, national parks, temples, beaches, or mountains</p>",
    unsafe_allow_html=True,
)

# --- Chat area: grows with content, no fixed-height scrollbar ---
chat_container = None
if st.session_state.messages:
    chat_container = st.container(border=False)
    with chat_container:
        render_chat_history()

# --- Handle User Input OR Retry Action ---
user_prompt = st.chat_input("E.g., 'Tell me about free historical temples in Kandy'")
is_retry = st.session_state.get("retry_action", False)

if user_prompt or is_retry:

    if is_retry:
        st.session_state.retry_action = False
        # Remove the previous error message from history
        if st.session_state.messages and st.session_state.messages[-1].get("is_error"):
            st.session_state.messages.pop()
        
        # The prompt to process is the last successful user message
        prompt_to_process = st.session_state.messages[-1]["content"]
    else:
        prompt_to_process = user_prompt
        # 1. Append New User Message
        st.session_state.messages.append({"role": "user", "content": prompt_to_process})

    # If container wasn't created yet, create it now
    if chat_container is None:
        chat_container = st.container(border=False)

    with chat_container:
        # Only render the user bubble if it's a new prompt (history handles retries)
        if not is_retry:
            with st.chat_message("user"):
                st.markdown(prompt_to_process)

        # 2. Process via Hybrid RAG Pipeline
        with st.chat_message("assistant"):
            with st.spinner("Searching..."):
                img_input = (
                    Image.open(filters["uploaded_image"])
                    if filters["uploaded_image"]
                    else None
                )

                try:
                    # Grab the last 4 messages, EXCLUDING the prompt we are processing
                    history_to_pass = st.session_state.messages[:-1][-4:] if len(st.session_state.messages) > 1 else []

                    rag_result = generate_hybrid_rag_response(
                        user_text_query=prompt_to_process,
                        image_input=img_input,
                        category=filters["category"],
                        district=filters["district"],
                        max_budget_lkr=filters["max_budget_lkr"],
                        chat_history=history_to_pass  # Pass memory to the backend
                    )

                    llm_text = rag_result["llm_response"]
                    context_data = rag_result["retrieved_context"]

                    # Extract Candidate Attraction IDs
                    # Extract Candidate Attraction IDs (Preserving Visual -> Semantic Order)
                    candidate_ids = []
                    for key in ["visual", "semantic"]:
                        if key in context_data:
                            for item in context_data[key]:
                                aid = item.get("attraction_id")
                                if aid and aid not in candidate_ids:
                                    candidate_ids.append(aid)
                    
                    print(f"\nCandidate ids : {candidate_ids}\n")
                    
                    # Check our new LLM-driven boolean flag
                    image_is_needed = context_data.get("image_is_needed", True)

                    # Only fetch and display images if the AI determined they are needed
                    images_to_show = []
                    if image_is_needed and candidate_ids:
                        images_to_show = get_images_for_attractions(candidate_ids, ROOT_DIR)

                    # Render Assistant Response
                    render_assistant_response(llm_text, context_data, images_to_show)

                except Exception as e:
                    # 3. Handle Errors Gracefully
                    friendly_error = get_friendly_error_message(e)
                    st.error(friendly_error)
                    
                    # Save error state
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": friendly_error,
                        "is_error": True
                    })
                    
                    # Show immediate retry button
                    if st.button("🔄 Retry Request", key="retry_current_err"):
                        st.session_state.retry_action = True
                        st.rerun()