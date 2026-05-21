from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.document_loader import download_documents
from app.services.vector_store import index_document, search
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    n_results: int = 3

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "rag"}

@router.post("/index")
async def index_documents():
    """
    Downloads regulatory documents and indexes them into ChromaDB.
    Call this once to populate the vector store.
    """
    try:
        # Step 1 - download/create documents
        logger.info("Starting document indexing...")
        created_docs = await download_documents()

        # Step 2 - index each document
        total_chunks = 0
        indexed = []

        docs_dir = Path("./data/documents")
        for doc_name in created_docs:
            file_path = docs_dir / f"{doc_name}.txt"
            if file_path.exists():
                content = file_path.read_text()
                chunks = index_document(doc_name, content)
                total_chunks += chunks
                indexed.append(doc_name)

        return {
            "status": "success",
            "documents_indexed": len(indexed),
            "total_chunks": total_chunks,
            "documents": indexed
        }

    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search")
async def search_documents(request: SearchRequest):
    """
    Searches indexed documents for content relevant to the query.
    This is what agents call when they need regulatory context.
    """
    try:
        results = search(
            query=request.query,
            n_results=request.n_results
        )

        return {
            "query": request.query,
            "results": results,
            "total_found": len(results)
        }

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))