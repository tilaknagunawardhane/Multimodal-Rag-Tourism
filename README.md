# Multimodal RAG Tourism System - Sri Lanka

## Overview
This is a Multimodal Retrieval-Augmented Generation (RAG) system designed for the Sri Lanka Tourism sector, fulfilling the requirements for SCS 4203 Assignment 2. The system handles structured queries, semantic text queries, and visual image retrieval to provide context-aware, highly relevant recommendations for tourists.

It has been upgraded with **Conversational Memory** for seamless multi-turn chats, **Dynamic Intent Extraction** to control when images should be shown, and **Resilient Error Handling**.

## System Architecture
The application follows a modular, state-of-the-art RAG architecture:

1. **Frontend (`src/frontend/`)**: 
   - `app.py`: Streamlit-based interactive web application featuring graceful error handling and retry mechanisms.
   - `styles.py`: Centralized CSS injection for a deep slate dark theme, modern typography, and glassmorphism UI components.
   - `components/` and `utils/`: Modular helper elements for frontend rendering (including `error_handler.py`).

2. **Ingestion Pipelines (`src/ingestion/`)**:
   - `load_sql.py`: Connects to Neon PostgreSQL to ingest structured data (fees, locations, hours) from `data/tourism_data.csv`.
   - `load_vectors.py`: Processes textual descriptions (`data/text_descriptions.json`) using SentenceTransformers (`all-MiniLM-L6-v2`) and images (`data/images/`) using OpenAI's CLIP model. The generated embeddings are stored in two distinct Qdrant collections.

3. **Retrieval Pipelines (`src/retrieval/`)**:
   - **Intent & Query Reformulation** (`intent.py`): Parses natural language queries into structured JSON parameters using Gemini. Features **Conversational Query Rewriting** to resolve pronouns in multi-turn chats, and determines `image_is_needed` dynamically to prevent showing images during purely informational follow-ups.
   - **Structured** (`structured.py`): Performs SQL lookups in PostgreSQL to enforce budget constraints and factual data.
   - **Semantic Text** (`semantic.py`): Embeds the user query and searches the Qdrant text collection using Cosine Similarity.
   - **Visual Image** (`visual.py`): Embeds a user-uploaded image via CLIP and searches the Qdrant image collection for visually similar attractions.
   - **Hybrid Integrator** (`hybrid.py`): Combines multi-turn chat history, extracted intents, structured facts, semantic text contexts, and visual matches, then passes them to a Large Language Model (Gemini) to generate a cohesive natural language response.

## Database Design
- **Relational Database (Neon PostgreSQL)**:
  - Table: `attractions`
  - Columns: `attraction_id` (PK), `name`, `category`, `district`, `entrance_fee_lkr`, `opening_hours`, `best_season_to_visit`
- **Vector Database (Qdrant)**:
  - Collection `tourism_text`: Vector size 384 (SentenceTransformer `all-MiniLM-L6-v2`).
  - Collection `tourism_images`: Vector size 512 (OpenAI CLIP `clip-vit-base-patch32`).

## Installation Instructions

1. **Clone the repository and set up virtual environment (optional but recommended)**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   Copy the example environment file and fill in your actual API keys and connection strings.
   ```bash
   cp .env.example .env
   ```
   *Note: Ensure `DATABASE_URL`, `QDRANT_URL`, `QDRANT_API_KEY`, and `GEMINI_API_KEY` are valid.*

## Execution & Usage

1. **Validate Data**:
   Ensure all IDs match across CSV, JSON, and Images before ingestion.
   ```bash
   python validate_data.py
   ```

2. **Run Data Ingestion**:
   Load structured data into PostgreSQL:
   ```bash
   python src/ingestion/load_sql.py
   ```
   Load embeddings into Qdrant:
   ```bash
   python src/ingestion/load_vectors.py
   ```

3. **Test the Pipeline**:
   Run the newly updated comprehensive test suite, which evaluates NL intent extraction, explicit filters, semantic similarity, and multimodal searches:
   ```bash
   python test_updated_rag.py
   ```

4. **Launch the Web Interface**:
   Start the interactive Streamlit frontend application:
   ```bash
   streamlit run src/frontend/app.py
   ```
