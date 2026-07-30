import streamlit as st

CATEGORIES = ["All Categories", "Beach", "Mountain", "National Park", "Temple", "Historical Site", "Waterfall"]
DISTRICTS = [
    "All Districts", "Ampara", "Anuradhapura", "Badulla", "Colombo", "Galle",
    "Gampaha", "Hambantota", "Kandy", "Kurunegala", "Matale", "Matara",
    "Nuwara Eliya", "Polonnaruwa", "Puttalam", "Ratnapura", "Trincomalee"
]

def render_sidebar():
    """
    Compact dark-themed sidebar. Order: Filters → Action buttons → Visual Search.
    "Clear Filters" uses a flag so widget keys are reset before widgets are drawn,
    avoiding Streamlit's post-instantiation write restriction.
    """
    # --- Consume the reset flag BEFORE widgets are instantiated ---
    if st.session_state.pop("_reset_filters", False):
        st.session_state["sb_category"] = "All Categories"
        st.session_state["sb_district"] = "All Districts"
        st.session_state["sb_budget_enabled"] = False
        st.session_state.pop("sb_budget_value", None)

    with st.sidebar:
        st.markdown(
            "<h3 style='margin:0 0 0.1rem 0; color:#38bdf8; font-size:1.05rem;'>Search Filters</h3>"
            "<p style='color:#64748b; font-size:0.8rem; margin:0 0 0.25rem 0;'>Refine your recommendations.</p>",
            unsafe_allow_html=True,
        )
        st.markdown("---")

        # Category
        selected_cat = st.selectbox("Category", CATEGORIES, index=0, key="sb_category")
        category_param = None if selected_cat == "All Categories" else selected_cat

        # District
        selected_dist = st.selectbox("District", DISTRICTS, index=0, key="sb_district")
        district_param = None if selected_dist == "All Districts" else selected_dist

        # Budget — slider only appears when checked
        enable_budget = st.checkbox("Apply Budget Cap", value=False, key="sb_budget_enabled")
        budget_param = None
        if enable_budget:
            budget_param = st.slider(
                "Max Fee (LKR):", min_value=0, max_value=20000, value=10000, step=500,
                key="sb_budget_value"
            )

        st.markdown("---")

        # Visual Search
        st.markdown(
            "<h3 style='margin:0 0 0.1rem 0; color:#38bdf8; font-size:1.05rem;'>Visual Search</h3>",
            unsafe_allow_html=True,
        )
        uploaded_image = st.file_uploader(
            "Upload a photo:", type=["jpg", "png", "jpeg"]
        )

        if uploaded_image is not None:
            st.image(uploaded_image, caption="Query Image", use_container_width=True)

        st.markdown("---")

        # Action buttons — side by side so sidebar stays compact
        col_clr_filters, col_clr_chat = st.columns(2)

        with col_clr_filters:
            if st.button("Clear Filters", use_container_width=True):
                st.session_state["_reset_filters"] = True
                st.rerun()

        with col_clr_chat:
            if st.button("Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    return {
        "category": category_param,
        "district": district_param,
        "uploaded_image": uploaded_image,
        "max_budget_lkr": budget_param,
    }