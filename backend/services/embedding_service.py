"""
Embedding service using sentence-transformers and ChromaDB.
Generates embeddings for semantic search.
"""

import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
import uuid

from backend.core.config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings and vector search."""
    
    def __init__(self):
        """Initialize the embedding service."""
        self.model = None
        self.chroma_client = None
        self.collection = None
        self._initialize_service()
    
    def _initialize_service(self) -> None:
        """Initialize embedding model and ChromaDB."""
        try:
            # Initialize sentence-transformers model
            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
            logger.info("Embedding model loaded successfully")
            
            # Initialize ChromaDB
            logger.info(f"Initializing ChromaDB at: {settings.CHROMA_PERSIST_DIR}")
            self.chroma_client = chromadb.Client(ChromaSettings(
                persist_directory=settings.CHROMA_PERSIST_DIR,
                anonymized_telemetry=False
            ))
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name="voice_notes",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("ChromaDB initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing embedding service: {e}")
            raise
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding
        """
        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_tensor=False)
            
            # Convert to list
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    async def store_note_embedding(
        self,
        note_id: str,
        text: str,
        metadata: Dict[str, Any]
    ) -> str:
        """
        Generate and store embedding for a note.
        
        Args:
            note_id: Unique note ID
            text: Text content to embed
            metadata: Note metadata (tags, date, etc.)
            
        Returns:
            Embedding ID
        """
        try:
            logger.info(f"Storing embedding for note: {note_id}")
            
            # Generate embedding
            embedding = await self.generate_embedding(text)
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata],
                ids=[note_id]
            )
            
            logger.info(f"Embedding stored successfully: {note_id}")
            return note_id
            
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")
            raise
    
    async def search_similar_notes(
        self,
        query_text: str,
        n_results: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar notes using semantic search.
        
        Args:
            query_text: Search query
            n_results: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of similar notes with similarity scores
        """
        try:
            logger.info(f"Searching similar notes for: {query_text[:50]}...")
            
            # Generate query embedding
            query_embedding = await self.generate_embedding(query_text)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=filter_metadata if filter_metadata else None
            )
            
            # Format results
            similar_notes = []
            
            if results['ids'] and len(results['ids']) > 0:
                for i in range(len(results['ids'][0])):
                    similar_notes.append({
                        "note_id": results['ids'][0][i],
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if 'distances' in results else None,
                        "similarity": 1 - results['distances'][0][i] if 'distances' in results else None
                    })
            
            logger.info(f"Found {len(similar_notes)} similar notes")
            return similar_notes
            
        except Exception as e:
            logger.error(f"Error searching similar notes: {e}")
            return []
    
    async def update_note_embedding(
        self,
        note_id: str,
        text: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update embedding for an existing note.
        
        Args:
            note_id: Note ID
            text: Updated text
            metadata: Updated metadata
            
        Returns:
            True if successful
        """
        try:
            # Delete old embedding
            self.collection.delete(ids=[note_id])
            
            # Store new embedding
            await self.store_note_embedding(note_id, text, metadata)
            
            logger.info(f"Embedding updated: {note_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating embedding: {e}")
            return False
    
    async def delete_note_embedding(self, note_id: str) -> bool:
        """
        Delete embedding for a note.
        
        Args:
            note_id: Note ID
            
        Returns:
            True if successful
        """
        try:
            self.collection.delete(ids=[note_id])
            logger.info(f"Embedding deleted: {note_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting embedding: {e}")
            return False
    
    def is_available(self) -> bool:
        """
        Check if embedding service is available.
        
        Returns:
            True if service is initialized
        """
        return self.model is not None and self.collection is not None


# Global instance
embedding_service = EmbeddingService()