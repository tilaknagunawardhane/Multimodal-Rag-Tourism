import streamlit as st


def render_chat_history():
    """
    Renders existing chat conversation history from st.session_state.
    The metadata expander has been removed — only LLM text and images are shown.
    """
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

            # Display matching attraction images inline
            if msg.get("images"):
                st.markdown(
                    "<p style='color:#475569; font-size:0.82rem; font-weight:500; "
                    "margin-top:6px; margin-bottom:2px;'>Related Images:</p>",
                    unsafe_allow_html=True,
                )
                cols = st.columns(len(msg["images"]))
                for col, img_path in zip(cols, msg["images"]):
                    with col:
                        st.image(img_path, use_container_width=True)


def render_assistant_response(llm_text: str, context_data: dict, images_to_show: list):
    """
    Renders the newly generated assistant response and saves it to session state.
    The metadata expander has been removed — only LLM text and images are shown.
    """
    st.markdown(llm_text)

    if images_to_show:
        st.markdown(
            "<p style='color:#475569; font-size:0.82rem; font-weight:500; "
            "margin-top:6px; margin-bottom:2px;'>Related Images:</p>",
            unsafe_allow_html=True,
        )
        cols = st.columns(len(images_to_show))
        for col, img_path in zip(cols, images_to_show):
            with col:
                st.image(img_path, use_container_width=True)

    # Persist message in session state (context kept for potential backend use, not displayed)
    st.session_state.messages.append({
        "role": "assistant",
        "content": llm_text,
        "context": context_data,
        "images": images_to_show,
    })