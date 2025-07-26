from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any
import uuid
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class RAGEngine:
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        logger.debug(f"Using collection: {self.collection_name}")
        logger.debug(f"Using model: {settings.EMBEDDING_MODEL}")
        logger.debug(f"Connecting to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
        self._ensure_collection_exists()
        logger.info("RAG Engine initialized ✅")

    def _ensure_collection_exists(self):
        """Create collection if it doesn't exist"""
        try:
            collections = self.qdrant_client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                self.qdrant_client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,  # all-MiniLM-L6-v2 dimension
                        distance=Distance.COSINE
                    ),
                )
                logger.info(f"Created collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for text"""
        try:
            logger.debug(f"Text for embedding (first 100 chars): {text[:100]}")
            embedding = self.embedding_model.encode(text)
            logger.debug(f"Generated embedding of length {len(embedding)}")
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    def store_event_embedding(self, event: Dict[str, Any]) -> None:
        """Store event embedding in vector database"""
        try:
            # Create searchable text from event
            searchable_text = f"{event.get('message', '')} {event.get('event_type', '')} {event.get('source', '')}"
            embedding = self.generate_embedding(searchable_text)
            
            if not embedding:
                return

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=embedding,
                payload={
                    "event_id": event["id"],
                    "message": event["message"],
                    "event_type": event["event_type"],
                    "source": event["source"],
                    "timestamp": event["timestamp"],
                    "tags": event.get("tags", []),
                    "priority": event.get("priority", "medium")
                }
            )

            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            logger.info(f"Stored embedding for event: {event['id']}")

            # DEBUG print for immediate verification
            results = self.retrieve_similar_events(searchable_text)
            context = self.build_rag_context(event, results)
            print("✅ Similar Events:")
            for r in results:
                print(r)
            print("\n📄 RAG Context:\n", context)
        except Exception as e:
            logger.error(f"Error storing embedding: {e}")

    def retrieve_similar_events(self, query_text: str, limit: int = None) -> List[Dict]:
        """Retrieve similar events from vector database"""
        try:
            if limit is None:
                limit = settings.MAX_SIMILAR_EVENTS

            query_embedding = self.generate_embedding(query_text)
            if not query_embedding:
                return []

            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit,
                score_threshold=0.7  # Only return results with >70% similarity
            )
            logger.debug(f"Raw search results: {search_results}")

            similar_events = []
            for result in search_results:
                similar_events.append({
                    "score": result.score,
                    "event_id": result.payload.get("event_id", ""),
                    "message": result.payload.get("message", ""),
                    "event_type": result.payload.get("event_type", ""),
                    "source": result.payload.get("source", ""),
                    "tags": result.payload.get("tags", []),
                    "priority": result.payload.get("priority", "medium")
                })

            return similar_events
        except Exception as e:
            logger.error(f"Error retrieving similar events: {e}")
            return []

    def build_rag_context(self, current_event: Dict, similar_events: List[Dict]) -> str:
        """Build context for RAG prompt"""
        if not similar_events:
            return "No similar events found in knowledge base."

        context_parts = [
            "Similar events from knowledge base:",
            ""
        ]

        for i, event in enumerate(similar_events[:3], 1):  # Top 3 most similar
            context_parts.append(
                f"{i}. Event: {event['message']}\n"
                f"   Tags: {', '.join(event['tags'])}\n"
                f"   Priority: {event['priority']}\n"
                f"   Similarity: {event['score']:.2f}\n"
            )

        return "\n".join(context_parts)
