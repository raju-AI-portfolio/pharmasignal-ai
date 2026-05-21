import os
import logging
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

def get_embedding_client():
    """
    Returns an Azure OpenAI client configured for embeddings.
    """
    return AzureOpenAI(
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION")
    )

def embed_text(text: str) -> list[float]:
    """
    Converts a text string into a vector embedding.
    Returns a list of floats representing the text in vector space.
    """
    client = get_embedding_client()
    
    try:
        response = client.embeddings.create(
            model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        raise

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Splits a large text into smaller overlapping chunks.
    
    Why overlap? So that information at the boundary of chunks
    is not lost — each chunk shares some context with the next.
    
    chunk_size = 500 characters per chunk
    overlap    = 50 characters shared between consecutive chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Only add non-empty chunks
        if chunk.strip():
            chunks.append(chunk.strip())
        
        # Move forward by chunk_size minus overlap
        start += chunk_size - overlap
    
    return chunks