import streamlit as st

def render_chat_history():
    """
    Renders existing chat conversation history from st.session_state.
    Includes special handling for error states and retry buttons.
    """
    for i, msg in enumerate(st.session_state.messages):
        with st.chat_message(msg["role"]):
            
            # 1. Handle Error Messages with Retry Button
            if msg.get("is_error"):
                st.error(msg["content"])
                if st.button("🔄 Retry Request", key=f"retry_btn_{i}"):
                    st.session_state.retry_action = True
                    st.rerun()
            
            # 2. Handle Standard Assistant/User Messages
            else:
                st.markdown(msg["content"])
                
                # Display matching database images if present
                if msg.get("images"):
                    st.markdown("<p style='color: #475569; font-size: 0.85rem; font-weight: 500; margin-top: 8px;'>Related Destination Images:</p>", unsafe_allow_html=True)
                    cols = st.columns(len(msg["images"]))
                    for col, img_path in zip(cols, msg["images"]):
                        with col:
                            st.image(img_path, use_container_width=True)

def render_assistant_response(llm_text: str, context_data: dict, images_to_show: list):
    """
    Renders the newly generated assistant response and saves it to session state.
    """
    st.markdown(llm_text)

    if images_to_show:
        st.markdown("<p style='color: #475569; font-size: 0.85rem; font-weight: 500; margin-top: 8px;'>Related Destination Images:</p>", unsafe_allow_html=True)
        cols = st.columns(len(images_to_show))
        for col, img_path in zip(cols, images_to_show):
            with col:
                st.image(img_path, use_container_width=True)

    # Persist message in session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": llm_text,
        "context": context_data,
        "images": images_to_show
    })