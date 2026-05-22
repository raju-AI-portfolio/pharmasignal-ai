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
    """
    Returns a ChromaDB client.
    Data is persisted to disk at CHROMA_PATH.
    """
    Path(CHROMA_PATH).mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=CHROMA_PATH)

def get_or_create_collection():
    """
    Gets or creates the regulatory documents collection in ChromaDB.
    A collection is like a table in a database — it holds all our vectors.
    """
    client = get_chroma_client()
    collection = client.get_or_create_collection(
        name="regulatory_documents",
        metadata={"description": "Pharma regulatory guidelines and SOPs"}
    )
    return collection

def index_document(doc_name: str, content: str) -> int:
    """
    Chunks a document, embeds each chunk and stores in ChromaDB.
    Returns the number of chunks indexed.
    """
    collection = get_or_create_collection()
    
    # Split document into chunks
    chunks = chunk_text(content)
    logger.info(f"Indexing {doc_name} — {len(chunks)} chunks")
    
    # Embed and store each chunk
    for i, chunk in enumerate(chunks):
        chunk_id = f"{doc_name}_chunk_{i}"
        
        # Check if already indexed
        existing = collection.get(ids=[chunk_id])
        if existing["ids"]:
            continue
        
        # Get embedding for this chunk
        embedding = embed_text(chunk)
        
        # Store in ChromaDB
        collection.add(
            ids=[chunk_id],
            embeddings=[embedding],
            documents=[chunk],
            metadatas=[{
                "source": doc_name,
                "chunk_index": i
            }]
        )
    
    logger.info(f"Successfully indexed {doc_name}")
    return len(chunks)

def search(query: str, n_results: int = 3) -> list[dict]:
    """
    Searches the vector store for chunks relevant to the query.
    
    How it works:
    1. Convert query to embedding vector
    2. Find the n_results most similar vectors in ChromaDB
    3. Return the matching document chunks
    """
    collection = get_or_create_collection()
    
    # Check if collection has any documents
    count = collection.count()
    if count == 0:
        logger.warning("Vector store is empty — please index documents first")
        return []
    
    # Embed the query
    query_embedding = embed_text(query)
    
    # Search for similar chunks
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(n_results, count)
    )
    
    # Format results
    formatted = []
    for i, doc in enumerate(results["documents"][0]):
        formatted.append({
            "content": doc,
            "source": results["metadatas"][0][i]["source"],
            "chunk_index": results["metadatas"][0][i]["chunk_index"],
            "distance": results["distances"][0][i] if "distances" in results else None
        })
    
    return formatted