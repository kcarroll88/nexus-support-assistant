# Nexus Support Assistant

A RAG (Retrieval-Augmented Generation) support tool that answers questions by searching a knowledge base of PDF documents. Built with LangChain, Chroma, Voyage AI embeddings, and Claude.

## What it does

1. Loads PDF documents from the `docs/` folder into a vector database
2. Accepts natural language questions via a Streamlit web UI
3. Finds the most relevant document chunks using semantic search
4. Generates a concise answer using Claude, with source attribution

## Setup

**Prerequisites:** Python 3.14+, API keys for [Anthropic](https://console.anthropic.com) and [Voyage AI](https://www.voyageai.com)

```bash
# Clone and enter the project
cd langchain-rag

# Activate the virtual environment
source venv/bin/activate

# Add your API keys
cp .env.example .env   # then edit .env with your keys
```

**.env format:**
```
ANTHROPIC_API_KEY=your_anthropic_key
VOYAGE_API_KEY=your_voyage_key
```

## Running

```bash
streamlit run app.py
```

The app opens at `http://localhost:8501`. On first launch it automatically indexes the PDFs in `docs/`. Use the **Rebuild Index** button in the sidebar to re-index after adding or updating documents.

## Project structure

```
langchain-rag/
├── app.py          # Streamlit UI
├── rag.py          # RAG pipeline (load, chunk, embed, search, answer)
├── docs/           # Knowledge base PDFs
├── chroma_db/      # Persistent vector database (auto-generated)
└── .env            # API keys (not committed)
```

## Key dependencies

| Package | Role |
|---|---|
| `streamlit` | Web interface |
| `langchain` + sub-packages | Document loading, chunking, RAG orchestration |
| `chromadb` | Vector database |
| `voyageai` | Embeddings (`voyage-3` model) |
| `anthropic` | LLM for answer generation |
| `pypdf` | PDF parsing |

## Adding documents

Drop PDF files into the `docs/` folder and click **Rebuild Index** in the sidebar to include them in search.
