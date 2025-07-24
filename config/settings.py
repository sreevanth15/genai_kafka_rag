import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Kafka Settings
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_RAW_EVENTS_TOPIC = os.getenv("KAFKA_RAW_EVENTS_TOPIC", "raw-events")
    KAFKA_TAGGED_EVENTS_TOPIC = os.getenv("KAFKA_TAGGED_EVENTS_TOPIC", "tagged-events")
    KAFKA_CONSUMER_GROUP = os.getenv("KAFKA_CONSUMER_GROUP", "rag-tagger-group")
    
    # GenAI Settings
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Vector Database Settings
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "event_embeddings")
    
    # Application Settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    MAX_SIMILAR_EVENTS = int(os.getenv("MAX_SIMILAR_EVENTS", "5"))

settings = Settings()
