"""
Qdrant vector store management.
"""
import logging
import uuid
from typing import List, Dict, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
)
from app.core.config import settings
from app.core.embeddings import embeddings_generator

logger = logging.getLogger(__name__)


class VectorStore:
    """Qdrant vector store wrapper."""
    
    def __init__(self):
        """Initialize Qdrant client and collection."""
        try:
            # Initialize Qdrant client
            self.client = QdrantClient(
                url=settings.QDRANT_URL,
                api_key=settings.QDRANT_API_KEY,
            )
            
            self.collection_name = settings.QDRANT_COLLECTION_NAME
            
            # Get embedding dimension
            embedding_dim = embeddings_generator.dimension
            
            # Check if collection exists, create if not
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=embedding_dim,
                        distance=Distance.COSINE
                    )
                )
            else:
                logger.info(f"Using existing collection: {self.collection_name}")
            
            logger.info(f"Vector store initialized: {self.collection_name}")
            
        except Exception as e:
            logger.error(f"Error initializing vector store: {str(e)}", exc_info=True)
            raise
    
    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict]] = None,
        doc_id: Optional[str] = None,
    ) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            texts: List of text chunks to add
            metadatas: Optional list of metadata dicts
            doc_id: Optional document ID for grouping chunks
            
        Returns:
            List of chunk IDs
        """
        try:
            # Generate embeddings
            embeddings = embeddings_generator.embed_documents(texts)
            
            # Generate IDs - Qdrant requires UUIDs or integers, not strings with underscores
            chunk_ids = [
                uuid.uuid4() for _ in range(len(texts))
            ]
            
            # Prepare metadatas
            if metadatas is None:
                metadatas = [{} for _ in texts]
            
            # Add document ID to metadata if provided
            if doc_id:
                for meta in metadatas:
                    meta["doc_id"] = doc_id
            
            # Prepare points for Qdrant
            points = []
            for i, (chunk_id, embedding, text, metadata) in enumerate(zip(chunk_ids, embeddings, texts, metadatas)):
                points.append(
                    PointStruct(
                        id=chunk_id,
                        vector=embedding,
                        payload={
                            "text": text,
                            **metadata
                        }
                    )
                )
            
            # Upsert points to Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"Added {len(texts)} documents to vector store")
            # Return string IDs for consistency
            return [str(chunk_id) for chunk_id in chunk_ids]
            
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}", exc_info=True)
            raise
    
    def search(
        self,
        query: str,
        top_k: int = None,
        min_score: float = None,
        filter_metadata: Optional[Dict] = None,
    ) -> List[Dict]:
        """
        Search for similar documents.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            min_score: Minimum similarity score
            filter_metadata: Optional metadata filter
            
        Returns:
            List of search results with text, metadata, and score
        """
        try:
            top_k = top_k or settings.RAG_TOP_K
            min_score = min_score or settings.RAG_MIN_SCORE
            
            # Generate query embedding
            query_embedding = embeddings_generator.embed_query(query)
            
            # Build filter if provided
            query_filter = None
            if filter_metadata:
                conditions = []
                for key, value in filter_metadata.items():
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )
                if conditions:
                    query_filter = Filter(must=conditions)
            
            # Search in Qdrant using query_points (correct API for qdrant-client 1.7.0)
            # query_points accepts the vector directly as the 'query' parameter
            try:
                query_result = self.client.query_points(
                    collection_name=self.collection_name,
                    query=query_embedding,  # Pass vector directly
                    limit=top_k,
                    score_threshold=min_score,
                    query_filter=query_filter,
                    with_payload=True,
                    with_vectors=False,
                )
                
                # Extract results from query response
                results_list = query_result.points if hasattr(query_result, 'points') else []
                
            except Exception as e:
                logger.error(f"Qdrant query_points failed: {str(e)}", exc_info=True)
                raise Exception(f"Qdrant query failed: {str(e)}")
            
            # Format results
            formatted_results = []
            for point in results_list:
                # Qdrant returns score as similarity (higher is better)
                # For cosine distance, score is already similarity
                score = point.score if hasattr(point, 'score') else 0.0
                
                if score >= min_score:
                    payload = point.payload if hasattr(point, 'payload') else {}
                    point_id = str(point.id) if hasattr(point, 'id') else ''
                    
                    formatted_results.append({
                        "text": payload.get("text", "") if payload else "",
                        "metadata": {k: v for k, v in (payload.items() if payload else []) if k != "text"},
                        "id": point_id,
                        "score": float(score),
                    })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}", exc_info=True)
            raise
    
    def delete_document(self, doc_id: str) -> None:
        """
        Delete all chunks for a document.
        
        Args:
            doc_id: Document ID to delete
        """
        try:
            # Search for all points with this doc_id
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="doc_id",
                        match=MatchValue(value=doc_id)
                    )
                ]
            )
            
            # Get all points with this doc_id
            scroll_result = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=filter_condition,
                limit=10000,  # Adjust if you have more chunks per document
                with_payload=False,
                with_vectors=False,
            )
            
            if scroll_result[0]:  # Points found
                point_ids = [point.id for point in scroll_result[0]]
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=point_ids
                )
                logger.info(f"Deleted {len(point_ids)} chunks for doc_id: {doc_id}")
            else:
                logger.info(f"No chunks found for doc_id: {doc_id}")
            
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}", exc_info=True)
            raise
    
    def get_collection_stats(self) -> Dict:
        """Get statistics about the collection."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return {
                "total_chunks": collection_info.points_count,
                "collection_name": self.collection_name,
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}", exc_info=True)
            return {"error": str(e)}


# Global instance
vector_store = VectorStore()

