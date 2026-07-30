import streamlit as st

def apply_dark_theme():
    """
    Deep slate dark theme with teal accents.
    Sidebar allows a thin auto-scrollbar when content overflows (e.g. budget slider active).
    Chat input text is explicitly forced to a light colour.
    """
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

        /* ===== VIEWPORT — allow natural vertical scroll, no horizontal bar ===== */
        html, body {
            overflow-x: hidden !important;
        }
        [data-testid="stAppViewContainer"] {
            overflow-x: hidden !important;
        }
        [data-testid="stHeader"] {
            overflow: hidden !important;
        }

        /* ===== MAIN CONTENT — pull up, remove default top gap ===== */
        .main .block-container {
            padding-top: 1rem !important;
            margin-top: 0 !important;
        }

        /* ===== BASE ===== */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif !important;
            color: #e2e8f0 !important;
        }

        .stApp {
            background-color: #0f172a !important;
        }

        /* Hide Streamlit chrome */
        #MainMenu { visibility: hidden; }
        footer     { visibility: hidden; }
        header     { background-color: transparent !important; }

        /* ===== SIDEBAR — thin auto-scrollbar so Clear button is always reachable ===== */
        [data-testid="stSidebar"] {
            background-color: #1e293b !important;
            border-right: 1px solid #334155 !important;
            overflow-y: auto !important;    /* allows scroll when slider appears */
            overflow-x: hidden !important;  /* no horizontal scrollbar */
            padding-bottom: 1rem !important;
        }

        /* Thin, subtle scrollbar for sidebar */
        [data-testid="stSidebar"]::-webkit-scrollbar { width: 4px; }
        [data-testid="stSidebar"]::-webkit-scrollbar-track { background: transparent; }
        [data-testid="stSidebar"]::-webkit-scrollbar-thumb {
            background: #475569;
            border-radius: 4px;
        }
        [data-testid="stSidebar"]::-webkit-scrollbar-thumb:hover { background: #64748b; }

        /* Compact sidebar widget spacing */
        [data-testid="stSidebar"] .stElementContainer { margin-bottom: 0.15rem !important; }
        [data-testid="stSidebar"] .stMarkdown p        { margin-bottom: 0.1rem  !important; }
        [data-testid="stSidebar"] hr {
            margin-top: 0.35rem !important;
            margin-bottom: 0.35rem !important;
            border-color: #334155 !important;
        }

        /* ===== HEADINGS ===== */
        h1 {
            color: #38bdf8 !important;
            font-weight: 700;
            letter-spacing: -0.3px;
            font-size: 1.6rem !important;
            margin-bottom: 0.1rem !important;
        }

        h2, h3 {
            color: #cbd5e1 !important;
            font-weight: 600;
        }

        /* ===== TEXT & LABELS ===== */
        label, p, span, li {
            color: #e2e8f0 !important;
        }

        .stSelectbox label,
        .stSlider label,
        .stCheckbox label span,
        .stFileUploader label {
            color: #cbd5e1 !important;
            font-weight: 500 !important;
        }

        /* Selectbox value and options text */
        div[data-baseweb="select"],
        div[data-baseweb="select"] * {
            color: #e2e8f0 !important;
            background-color: #1e293b !important;
        }

        div[data-baseweb="select"] [data-testid="stSelectboxVirtualDropdown"],
        ul[data-baseweb="menu"],
        ul[role="listbox"] {
            background-color: #1e293b !important;
        }

        ul[role="listbox"] li,
        li[data-baseweb="menu-item"] {
            background-color: #1e293b !important;
            color: #e2e8f0 !important;
        }

        ul[role="listbox"] li:hover,
        li[data-baseweb="menu-item"]:hover {
            background-color: #334155 !important;
        }

        /* Slider value & ticks */
        .stSlider div[data-testid="stTickBarMin"],
        .stSlider div[data-testid="stTickBarMax"],
        .stSlider div[data-testid="stThumbValue"] {
            color: #94a3b8 !important;
        }

        /* Slider filled track */
        [data-testid="stSlider"] [role="slider"] {
            background-color: #14b8a6 !important;
        }

        /* Input & textarea base */
        input, textarea, select {
            color: #e2e8f0 !important;
            background-color: #1e293b !important;
        }

        /* ===== CHAT MESSAGES ===== */
        .stChatMessage {
            background-color: #1e293b !important;
            border: 1px solid #334155 !important;
            border-radius: 10px !important;
            padding: 1rem 1.15rem !important;
            margin-bottom: 0.5rem !important;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
        }

        .stChatMessage p,
        .stChatMessage span,
        .stChatMessage li,
        .stChatMessage h1,
        .stChatMessage h2,
        .stChatMessage h3,
        .stChatMessage strong {
            color: #e2e8f0 !important;
        }

        /* ===== AVATARS ===== */
        [data-testid="chatAvatarIcon-user"]      { background-color: #14b8a6 !important; }
        [data-testid="chatAvatarIcon-assistant"] { background-color: #6366f1 !important; }

        /* ===== BUTTONS ===== */
        .stButton > button {
            background-color: #14b8a6 !important;
            color: #0f172a !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 0.45rem 1.2rem !important;
            font-weight: 600 !important;
            transition: background-color 0.2s ease, box-shadow 0.2s ease !important;
            box-shadow: 0 1px 4px rgba(20, 184, 166, 0.25) !important;
        }

        .stButton > button:hover {
            background-color: #0d9488 !important;
            box-shadow: 0 3px 10px rgba(20, 184, 166, 0.4) !important;
        }

        /* ===== FILE UPLOADER ===== */
        [data-testid="stFileUploadDropzone"] {
            background-color: #1e293b !important;
            border: 2px dashed #475569 !important;
            border-radius: 8px !important;
        }

        [data-testid="stFileUploadDropzone"]:hover {
            border-color: #14b8a6 !important;
            background-color: #0f2d29 !important;
        }

        /* ===== CHAT INPUT — force light text so it's always visible ===== */
        [data-testid="stChatInput"] {
            border: 1px solid #334155 !important;
            background-color: #1e293b !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
        }

        /* The actual textarea inside the chat input widget */
        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] textarea::placeholder {
            color: #e2e8f0 !important;
            background-color: transparent !important;
            caret-color: #38bdf8 !important;
        }

        [data-testid="stChatInput"] textarea::placeholder {
            color: #64748b !important;
        }

        /* Send button icon inside chat input */
        [data-testid="stChatInput"] button svg { fill: #14b8a6 !important; }

        /* ===== HIDE scrollable chat container border ===== */
        [data-testid="stVerticalBlockBorderWrapper"] {
            border: none !important;
        }

        /* ===== MISC STREAMLIT ELEMENTS ===== */
        /* Checkbox */
        [data-testid="stCheckbox"] span {
            color: #cbd5e1 !important;
        }

        /* Spinner */
        [data-testid="stSpinner"] p { color: #94a3b8 !important; }

        /* Info / error boxes */
        [data-testid="stAlert"] {
            background-color: #1e293b !important;
            border-color: #334155 !important;
            color: #e2e8f0 !important;
        }
    </style>
    """, unsafe_allow_html=True)