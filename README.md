
# RuBot — Google Docs RAG Chatbot

*A document-grounded chatbot that answers questions strictly from a Google Doc, engineered for correctness, traceability, and real-world RAG workflows.*

## Problem Statement

RuBot simulates a real-world internal knowledge base chatbot, focusing on reducing hallucinations and ensuring every answer is grounded in a specific document. By combining retrieval with inline citations, RuBot provides traceable, document-backed responses—addressing the core challenge of trustworthy Q&A over proprietary or internal content.


## Architecture Overview

**High-Level Flow:**
1. **Ingestion**: Fetch Google Doc content using the Google Docs API  
   *Why: Enables structured, up-to-date access to collaborative documents, not just plain text.*
2. **Chunking**: Split text into section-aware, token-limited chunks with overlap  
   *Why: Preserves context and boundaries, critical for accurate retrieval and LLM input limits.*
3. **Embedding**: Generate vector embeddings for each chunk  
   *Why: Converts text to vectors for efficient, semantic similarity search.*
4. **Vector Storage**: Store embeddings in ChromaDB  
   *Why: Enables scalable, fast similarity search over document chunks.*
5. **Retrieval**: Rewrite and embed user queries, retrieve top-k relevant chunks  
   *Why: Improves recall and ensures only relevant content is passed to the LLM.*
6. **Generation**: Use an LLM to generate answers, citing relevant sections/pages  
   *Why: Produces natural language answers with traceable references.*
7. **Frontend**: Minimal web UI for chat interaction

```
Google Doc → Ingestion → Chunking → Embedding → Vector DB → Retrieval → Generation → User
```
## Why This Project Is Non-Trivial

- **Google Docs ingestion** is more complex than plain text scraping: it requires API authentication, parsing document structure, and handling collaborative edits.
- **Token-based chunking with overlap** is essential: it preserves context across chunk boundaries and prevents information loss, which is critical for retrieval accuracy.
- **Retrieval quality** directly impacts hallucinations: poor retrieval leads to off-topic or fabricated answers, so robust similarity search is vital.
- **Metadata propagation** (section/page info) is required for reliable citations, enabling users to trace answers back to the source.


## Tech Stack

- **Backend**: Python, FastAPI
- **Vector DB**: ChromaDB
- **Embeddings**: Hugging Face Inference API (BAAI/bge-base-en-v1.5)
- **LLM**: openai/gpt-oss-20b (for answer generation) and llama-3.1-8b-instant (for query re-writting)
- **Frontend**: HTML, CSS, JavaScript (minimal, no framework)
- **Deployment**: Render (or similar PaaS)

## Setup Instructions

### Prerequisites
- Python 3.9+
- Google Cloud service account with Docs API access
- Hugging Face Inference API key
- LLM API key (e.g., OpenAI, Groq)


### Environment Variables
Create a `.env` file in the root directory with the following variables:

```
GOOGLE_CREDENTIALS_PATH=path/to/your/service_account.json
HF_API_TOKEN=your_huggingface_api_key
GROQ_API_KEY=your_groq_api_key
```

> **Note:** Credentials must never be committed—this protects sensitive access and is required for secure deployments. See `.gitignore`.

### Installation

```bash
# Clone the repository
 git clone https://github.com/RudranshJaiswal01/AI-Powered-ChatBot.git
 cd AI-Powered-ChatBot

# Install dependencies
 pip install -r requirements.txt
```

### How to Run Locally

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Open the frontend
# Visit http://localhost:8000/static or open frontend/index.html in your browser
```


## API Endpoints Overview

- `GET /health` — Service health check
- `POST /ingest` — Submit a Google Doc link for ingestion (accepts a public share link)
- `POST /chat` — Query the ingested document (supports optional conversation history)
- `POST /reset-db` — (Optional) Reset or clear the vector database


## Usage Instructions

- Only one document is ingested at a time; all answers are strictly grounded in that document.
- Provide a public Google Doc share link via the UI or `/ingest` endpoint.
- Ask questions in the chat UI or via the API. RuBot will answer only if the information is present in the document, with inline citations.
- Out-of-scope questions (not covered by the document) trigger a fallback response.

## Edge Cases Handled
- Invalid or private Google Doc links
- Empty or malformed documents
- Questions outside the document scope (graceful fallback response)

## Deployment

This app can be deployed on Render or any similar PaaS:

1. Set environment variables in the deployment dashboard
2. Upload your Google service account JSON as a secret file
3. Deploy from GitHub or Docker
4. Set the start command:
   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```
5. (Optional) Serve the frontend via FastAPI static files or a CDN


## Demo

- **Hosted App:** [ https://rubot-wzyz.onrender.com]( https://rubot-wzyz.onrender.com)
- **Demo Video:** [3-minute walkthrough](https://drive.google.com/file/d/1DS6iyxz1dry86xtztVD2oSeIC3DJVR1d/view?usp=drivesdk)

**The demo showcases:**
- Google Doc ingestion and chunking
- Section-aware retrieval and inline citations
- Strictly document-grounded answers
- Fallbacks for out-of-scope queries


## Future Improvements
- User authentication and per-user document storage
- Support for additional document sources (PDF, web pages)
- More advanced retrieval (hybrid search, reranking)
- Richer chat UI (React, Vue, etc.)
- Streaming responses from LLM

---

For questions or contributions, please open an issue or pull request.
