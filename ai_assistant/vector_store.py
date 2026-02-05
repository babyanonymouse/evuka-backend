import os
import chromadb
from django.conf import settings
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Service to handle semantic search using ChromaDB and SentenceTransformers.
    """
    _client = None
    _collection = None
    _model = None
    
    COLLECTION_NAME = "evuka_knowledge_base"
    
    @classmethod
    def _get_client(cls):
        if not cls._client:
            # Store the vector DB in the project root under /chroma_db
            persist_path = os.path.join(settings.BASE_DIR, "chroma_db")
            cls._client = chromadb.PersistentClient(path=persist_path)
        return cls._client
    
    @classmethod
    def _get_model(cls):
        if not cls._model:
            # Lightweight, efficient model for embeddings
            cls._model = SentenceTransformer('all-MiniLM-L6-v2')
        return cls._model

    @classmethod
    def _get_collection(cls):
        if not cls._collection:
            client = cls._get_client()
            cls._collection = client.get_or_create_collection(name=cls.COLLECTION_NAME)
        return cls._collection

    @classmethod
    def index_content(cls, content_id, text, metadata):
        """
        Generates an embedding for the text and checks it into Chroma.
        content_id: Unique string ID (e.g., "lesson_10")
        text: The content to embed
        metadata: Dict of metadata (title, type, url)
        """
        try:
            model = cls._get_model()
            embedding = model.encode(text).tolist()
            
            collection = cls._get_collection()
            collection.upsert(
                documents=[text],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[content_id]
            )
            return True
        except Exception as e:
            logger.error(f"Error indexing content {content_id}: {e}")
            return False

    @classmethod
    def search(cls, query, n_results=5):
        """
        Semantically searches the vector DB for the query.
        Returns a formatted string of results.
        """
        try:
            model = cls._get_model()
            query_embedding = model.encode(query).tolist()
            
            collection = cls._get_collection()
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results for the AI
            output_text = ""
            if not results['documents'] or not results['documents'][0]:
                return "No relevant semantic matches found in the vector database."

            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                output_text += f"[{meta.get('type', 'Unknown').upper()}] {meta.get('title', 'Untitled')}\n"
                output_text += f"{doc[:500]}...\n\n"
                
            return output_text
            
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            return f"Error performing semantic search: {e}"

    @classmethod
    def clear_collection(cls):
        """
        Wipes the collection. Useful for re-indexing.
        """
        client = cls._get_client()
        client.delete_collection(cls.COLLECTION_NAME)
        cls._collection = None
