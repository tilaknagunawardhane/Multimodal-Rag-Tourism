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

# --- Page Configuration ---
st.set_page_config(
    page_title="LankaGuideAI",
    page_icon="🌴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Apply Light Theme Styling
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
if st.session_state.messages:
    chat_container = st.container(border=False)
    with chat_container:
        render_chat_history()
else:
    chat_container = None
    # st.markdown(
    #     "<p style='color:#94a3b8; text-align:center; font-size:0.95rem;'>"
    #     "Start a conversation — ask about any Sri Lankan destination!</p>",
    #     unsafe_allow_html=True,
    # )

# --- Handle User Input ---
if prompt := st.chat_input("E.g., 'Tell me about free historical temples in Kandy'"):

    # 1. Append User Message
    st.session_state.messages.append({"role": "user", "content": prompt})

    # If container wasn't created yet, create it now
    if chat_container is None:
        chat_container = st.container(border=False)

    with chat_container:
        with st.chat_message("user"):
            st.markdown(prompt)

    # 2. Process via Hybrid RAG Pipeline
    with chat_container:
        with st.chat_message("assistant"):
            with st.spinner("Searching databases..."):
                img_input = (
                    Image.open(filters["uploaded_image"])
                    if filters["uploaded_image"]
                    else None
                )

                try:
                    rag_result = generate_hybrid_rag_response(
                        user_text_query=prompt,
                        image_input=img_input,
                        category=filters["category"],
                        district=filters["district"],
                        max_budget_lkr=filters["max_budget_lkr"],
                    )

                    llm_text = rag_result["llm_response"]
                    context_data = rag_result["retrieved_context"]

                    # Extract Candidate Attraction IDs
                    candidate_ids = set()
                    for key in ["semantic", "visual"]:
                        if key in context_data:
                            for item in context_data[key]:
                                if "attraction_id" in item:
                                    candidate_ids.add(item["attraction_id"])

                    images_to_show = (
                        get_images_for_attractions(candidate_ids, ROOT_DIR)
                        if candidate_ids
                        else []
                    )

                    # Render Assistant Response
                    render_assistant_response(llm_text, context_data, images_to_show)

                except Exception as e:
                    error_msg = f"An error occurred during retrieval: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append(
                        {"role": "assistant", "content": error_msg}
                    )