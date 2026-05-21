import os
import logging
import chromadb
from app.services.embedder import embed_text, chunk_text
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/chroma")

def get_chroma_client():
    Path(CHROMA_PATH).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_or_create_collection():
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name="regulatory_documents",
        metadata={"description": "Pharma regulatory guidelines and SOPs"}
    )
    return collection

def index_document(doc_name: str, content: str) -> int:
    collection = get_or_create_collection()
    chunks = chunk_text(content)
    logger.info(f"Indexing {doc_name} — {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_name}_chunk_{i}"
        existing = collection.get(ids=[chunk_id])
        if existing["ids"]:
            continue
        embedding = embed_text(chunk)
        collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{"source": doc_name, "chunk_index": i}]
        )
    logger.info(f"Successfully indexed {doc_name}")
    return len(chunks)

def search(query: str, n_results: int = 3) -> list[dict]:
    collection = get_or_create_collection()
    count = collection.count()
    if count == 0:
        logger.warning("Vector store is empty — please index documents first")
        return []
    query_embedding = embed_text(query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, count)
    )
    formatted = []
    for i, doc in enumerate(results["documents"][0]):
        formatted.append({
            "content": doc,
            "source": results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": results["distances"][0][i] if "distances" in results else None
        })
    return formatted
