# RAG PDF Ingestion & Query System

This project implements a **RAG (Retrieval-Augmented Generation)** system for uploading PDF documents, indexing them in a vector database, and answering questions based on their content.

The system utilizes:
*   **FastAPI** for the backend.
*   **Streamlit** for the frontend (file upload and chat interface).
*   **Inngest** for orchestrating asynchronous tasks (ingestion and answer generation).
*   **Qdrant** as the vector database.
*   **Groq API** (Llama 3 model) for LLM response generation.
*   **SentenceTransformers** for creating embeddings.

## 🏗 Architecture

The project consists of the following main modules:

1.  **`data_load.py`**: Handles reading PDF files, splitting text into chunks using `SentenceSplitter`, and creating vector representations (embeddings) using the `all-MiniLM-L6-v2` model.
2.  **`vec_db.py`**: A wrapper around the Qdrant client. Manages collection creation, vector uploading (`upsert`), and similar vector search (`search`).
3.  **`custom_types.py`**: Contains data type definitions (Pydantic models) for structuring data between pipeline steps (chunks, search results, answers).
4.  **`main.py`**: The core FastAPI application.
    *   Defines two Inngest functions:
        *   `rag_ingest_pdf`: Triggered by the `rag/ingest_pdf` event. Loads the PDF, chunks it, creates embeddings, and saves to Qdrant.
        *   `rag_query_pdf_ai`: Triggered by the `rag/query_pdf_ai` event. Searches for relevant chunks based on the user's question and generates an answer via the Groq API.
5.  **`frontend_app.py`**: The Streamlit interface.
    *   Allows uploading PDF files.
    *   Sends events to Inngest for processing.
    *   Displays task execution status by polling the local Inngest API.
    *   Provides a form for asking questions and displays the answer with sources.

## 🚀 Requirements

To run the project, you need:
*   Python 3.9+
*   Installed dependencies (see below)
*   A running instance of **Qdrant** (local or cloud).
*   A running **Inngest Dev Server** (for local development).
*   API keys for **Groq**.

## ⚙️ Installation and Setup

### 1. Clone the repository and install dependencies

```bash
pip install fastapi uvicorn streamlit inngest qdrant-client sentence-transformers llama-index python-dotenv pydantic requests
```

### 2. Configure environment variables

Create a ".env" file in the project root with the following content:

```env
# Groq API Key (for LLM)
GROQ_API_KEY=your_groq_api_key_here

# Qdrant Configuration
QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=your_qdrant_api_key_if_needed

# Inngest Configuration (for local development)
INNGEST_API_BASE=http://127.0.0.1:8288/v1
```

### 3. Launch components

#### Step A: Start Inngest Dev Server
In a separate terminal, start the Inngest development server so it can receive events from the application:

```bash
inngest dev --url http://localhost:8000
```
*(Ensure the port matches the port used to launch FastAPI)*

#### Step B: Start Qdrant
If you are using Docker:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

#### Step C: Start Backend (FastAPI)
```bash
uvicorn main:app --reload --port 8000
```
This will register the Inngest functions and open the API documentation at `http://localhost:8000/docs`.

#### Step D: Start Frontend (Streamlit)
In a new terminal:
```bash
streamlit run frontend_app.py
```
The interface will be available at http://localhost:8501.

## 📖 How to Use

1.  Open the Streamlit web interface.
2.  **Upload a Document:**
    *   Go to the "Upload a PDF to Ingest" section.
    *   Select a PDF file and click the upload button.
    *    The system will send an event to Inngest, which will start the parsing, chunking, and saving process to the vector database. You will see a success status upon completion.
3.  **Ask a Question:**
    *   Go to the "Ask a question about your PDFs" section.
    *   Enter your question.
    *   Specify the number of contextual chunks (top_k) to consider (default is 5).
    *   Click "Ask".
4.  **Get an Answer:**
    *   The application will wait for the Inngest task to complete.
    *   Once finished, the generated answer and the list of sources (file names/chunks) it is based on will be displayed.

## 🔧 Technical Details

*   **Embedding Model:** `all-MiniLM-L6-v2` (vector dimension 384).
*   **Distance Metric:** Cosine Similarity.
*   **LLM Model:** `llama-3.3-70b-versatile` via Groq provider.
*   **Chunk Size:** 1000 characters with an overlap of 200 characters.
*   **Limitations:**
    *   Ingestion is throttled: 2 events per minute.
    *   Source rate limit: 1 event per 4 hours for the same file (to avoid duplication when re-uploading the same file).
    *   Maximum context length before sending to LLM is truncated to 10,000 characters.

## 🛠 Troubleshooting

*   **Timeout while waiting for response:** If processing a large PDF takes a long time, increase the timeout_s parameter in the wait_for_run_output function in frontend_app.py.
*   **Connection error to Inngest:** Ensure that inngest dev is running and that the URL in .env (INNGEST_API_BASE) is correct.
*   **JSON key spaces:** Potential errors with extra spaces in dictionary keys (e.g., "question " -> "question") have been fixed in the code; ensure you are using the latest versions of the files.

---
*Project developed to demonstrate RAG capabilities using modern orchestration tools and vector search.*
