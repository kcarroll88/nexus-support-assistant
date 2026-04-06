import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import voyageai
import anthropic

load_dotenv()

voyage_client = voyageai.Client()
anthropic_client = anthropic.Anthropic()
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")

# ── 1. LOAD ───────────────────────────────────────────────────────────────────
def load_documents(folder_path="docs"):
    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            path = os.path.join(folder_path, filename)
            loader = PyPDFLoader(path)
            pages = loader.load()
            print(f"Loaded: {filename} ({len(pages)} pages)")
            docs.extend(pages)
    return docs

# ── 2. CHUNK ──────────────────────────────────────────────────────────────────
def chunk_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_documents(docs)
    print(f"Created {len(chunks)} chunks")
    return chunks

# ── 3. EMBED + STORE ──────────────────────────────────────────────────────────
def store_chunks(chunks):
    texts = [chunk.page_content for chunk in chunks]
    sources = [chunk.metadata.get("source", "unknown") for chunk in chunks]
    ids = [f"chunk_{i}" for i in range(len(chunks))]

    batch_size = 50
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_sources = sources[i:i+batch_size]
        batch_ids = ids[i:i+batch_size]

        response = voyage_client.embed(batch_texts, model="voyage-3")
        embeddings = response.embeddings

        collection.add(
            documents=batch_texts,
            embeddings=embeddings,
            metadatas=[{"source": s} for s in batch_sources],
            ids=batch_ids
        )
    print(f"Stored {len(chunks)} chunks in ChromaDB")

# ── 4. SEARCH ─────────────────────────────────────────────────────────────────
def search(query, n_results=3):
    query_embedding = voyage_client.embed([query], model="voyage-3").embeddings[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )
    texts = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    return texts, sources

# ── 5. ASK ────────────────────────────────────────────────────────────────────
def ask(query):
    chunks, sources = search(query)
    context = "\n\n".join(chunks)
    unique_sources = set(os.path.basename(s) for s in sources)

    response = anthropic_client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        messages=[{
            "role": "user",
            "content": f"""You are a helpful support assistant for Nexus, a SaaS project management platform.
            Answer the support agent's question using only the context below.
            Be concise and actionable — support agents need fast, clear answers.
            If the answer isn't in the context, say "I don't have that information in the knowledge base. Please escalate to Tier 2."

Context:
{context}

Question: {query}"""
        }]
    )

    return response.content[0].text, unique_sources 

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if collection.count() == 0:
        docs = load_documents()
        chunks = chunk_documents(docs)
        store_chunks(chunks)
    else:
        print(f"Loaded existing database with {collection.count()} chunks")

    questions = [
        "What is NASA?",
        "What are the best pizza toppings?",
    ]

    for question in questions:
        print(f"\nQ: {question}")
        answer, sources = ask(question)
        print(f"A: {answer}")
        print(f"Sources: {sources}")