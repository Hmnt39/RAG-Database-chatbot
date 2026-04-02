"""Embedding management for document and query embeddings."""

from datetime import datetime, timedelta, timezone
from typing import List
import logging
from sentence_transformers import SentenceTransformer
import openai
from app.state import db_client, settings
import numpy as np

openai.api_key = settings.openai_api_key

logger = logging.getLogger(__name__)


class EmbeddingManager:
    """Manages document and query embeddings using SentenceTransformers or OpenAI."""

    def __init__(self, embedding_mode: str = None, model_name: str = None):
        """
        Initialize embedding manager.

        Args:
            embedding_mode: "local" for SentenceTransformers or "openai" for OpenAI API
            model_name: Model name/identifier for embeddings
        """
        self.embedding_mode = embedding_mode or settings.embedding_mode
        self.model_name = model_name or settings.embedding_model
        self.model = None
        
        if self.embedding_mode.lower() == "local":
            try:
                self.model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded local embedding model: {self.model_name}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        elif self.embedding_mode.lower() == "openai":
            logger.info(f"Using OpenAI embeddings with model: {self.model_name}")
        else:
            raise ValueError(f"Unknown embedding mode: {self.embedding_mode}. Choose 'local' or 'openai'")

    def get_dimension(self) -> int:
        """
        Get embedding dimension.

        Returns:
            Embedding vector dimension
        """
        if self.embedding_mode.lower() == "local":
            return self.model.get_sentence_embedding_dimension()
        elif self.embedding_mode.lower() == "openai":
            return 1536  # Default for OpenAI embeddings
        return 0

    def create_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text using configured embedding mode.

        Args:
            text: Input text to embed

        Returns:
            List of embedding values
        """
        try:
            if self.embedding_mode.lower() == "local":
                embedding = self.model.encode(text, convert_to_tensor=False)
                return embedding.tolist()
            elif self.embedding_mode.lower() == "openai":
                response = openai.Embedding.create(
                    input=text,
                    model=self.model_name
                )
                return response['data'][0]['embedding']
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            raise
    
    @staticmethod
    def row_to_text(row: dict) -> str:
        """Convert opportunity row to text representation."""
        return (
            f"Opportunity {row['opportunityCode']} ({row['opportunityName']}) "
            f"belongs to {row['accountName']} ({row['accountCode']}). "
            f"It is currently in the {row['stage']} stage, sourced from {row['source']}, "
            f"owned by {row['owner']}. The expected deal amount is {row['amount']} {row['currency']} "
            f"with a probability of {row['probability']}%. The opportunity is {row['status']} "
            f"and {'active' if row['isActive'] else 'inactive'}, expected to close on {row['expectedCloseDate']}. "
            f"Description: {row['description']}."
        )

    def add_embeddings_to_collection(self, collection_name: str, latest_data: bool = True):
        """Add embeddings to MongoDB collection."""
        docs_collection = db_client.db[collection_name]
        embeddings_collection = db_client.db["embeddings"]

        query = {}
        if latest_data:
            query["updatedAt"] = {"$gte": datetime.now(timezone.utc) - timedelta(days=0)}

        docs = list(docs_collection.find(query))
        logger.info(f"Found {len(docs)} documents to embed in collection '{collection_name}'")

        for doc in docs:
            text = self.row_to_text(doc)
            embedding = self.create_embedding(text)
            embeddings_collection.insert_one({
                "doc_id": doc["_id"],
                "text": text,
                "embedding": embedding
            })
            logger.info(f"Embedded opportunity {doc['opportunityCode']}")

    
    def cosine_similarity(self, vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))


    def fetch_embeddings(self, top_k: int, query_embedding: List[float], max_candidates: int = 1000) -> List[str]:
        """
        Fetch and score embeddings efficiently.
        
        Args:
            top_k: Number of top results to return
            query_embedding: Query embedding vector
            max_candidates: Maximum number of candidates to fetch from DB (for performance)
        
        Returns:
            List of top-k matching texts
        """
        embeddings_collection = db_client.db["embeddings"]

        # Fetch limited number of embeddings from DB for performance
        # In production, consider using MongoDB Atlas Vector Search or a dedicated vector DB
        docs = list(embeddings_collection.find(
            {"embedding": {"$exists": True}},
            projection={"embedding": 1, "text": 1}
        ).limit(max_candidates))
        
        if not docs:
            logger.warning("No embeddings found in database")
            return []
        
        scored = []
        for doc in docs:
            if "embedding" in doc and doc["embedding"]:
                try:
                    score = self.cosine_similarity(query_embedding, doc["embedding"])
                    scored.append((score, doc["text"]))
                except Exception as e:
                    logger.warning(f"Error scoring embedding: {e}")
                    continue

        # Sort by similarity
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [text for _, text in scored[:top_k]]
        return results