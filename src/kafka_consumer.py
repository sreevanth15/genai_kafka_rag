from kafka import KafkaConsumer, KafkaProducer
import json
import logging
from typing import Dict
from datetime import datetime
from config.settings import settings
from src.rag_engine import RAGEngine
from src.genai_tagger import GenAITagger
from src.models.event_models import RawEvent, TaggedEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGKafkaConsumer:
    def __init__(self):
        self.consumer = KafkaConsumer(
            settings.KAFKA_RAW_EVENTS_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset='earliest',
            enable_auto_commit=True,
            group_id=settings.KAFKA_CONSUMER_GROUP,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )
        
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda m: json.dumps(m, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        self.rag_engine = RAGEngine()
        self.genai_tagger = GenAITagger()
        logger.info("RAG Kafka Consumer initialized ✅")

    def process_event(self, raw_event: Dict) -> TaggedEvent:
        """Process a single event with RAG enhancement"""
        try:
            # Create searchable text for RAG
            searchable_text = f"{raw_event['message']} {raw_event['event_type']}"
            
            # Retrieve similar events
            similar_events = self.rag_engine.retrieve_similar_events(searchable_text)
            
            # Build RAG context
            rag_context = self.rag_engine.build_rag_context(raw_event, similar_events)
            
            # Generate tags using RAG context
            tags, priority, confidence = self.genai_tagger.generate_tags_with_rag(
                raw_event, rag_context
            )
            
            # Create tagged event
            tagged_event = TaggedEvent(
                id=raw_event['id'],
                timestamp=datetime.fromisoformat(raw_event['timestamp']),
                source=raw_event['source'],
                event_type=raw_event['event_type'],
                message=raw_event['message'],
                metadata=raw_event.get('metadata', {}),
                tags=tags,
                priority=priority,
                confidence_score=confidence,
                similar_events=[e['event_id'] for e in similar_events[:3]],
                rag_context=rag_context[:500] if rag_context else None  # Truncate for storage
            )
            
            return tagged_event
            
        except Exception as e:
            logger.error(f"Error processing event {raw_event.get('id', 'unknown')}: {e}")
            # Return a fallback tagged event
            return TaggedEvent(
                id=raw_event.get('id', 'unknown'),
                timestamp=datetime.now(),
                source=raw_event.get('source', 'unknown'),
                event_type=raw_event.get('event_type', 'unknown'),
                message=raw_event.get('message', ''),
                metadata=raw_event.get('metadata', {}),
                tags=['error', 'processing_failed'],
                priority='low',
                confidence_score=0.3,
                similar_events=[],
                rag_context=None
            )

    def run(self):
        """Main consumer loop"""
        logger.info("Starting RAG consumer loop...")
        
        try:
            for message in self.consumer:
                raw_event = message.value
                logger.info(f"Processing event: {raw_event.get('id', 'unknown')}")
                
                try:
                    # Process event with RAG
                    tagged_event = self.process_event(raw_event)
                    
                    # Send to tagged events topic - FIXED: use model_dump()
                    try:
                        future = self.producer.send(
                            settings.KAFKA_TAGGED_EVENTS_TOPIC,
                            key=tagged_event.id,
                            value=tagged_event.model_dump()  # ✅ Fixed deprecation
                        )
                        future.get(timeout=10)  # Wait for acknowledgment
                        logger.debug(f"Successfully sent tagged event to Kafka: {tagged_event.id}")
                    except Exception as kafka_error:
                        logger.error(f"Failed to send tagged event to Kafka: {str(kafka_error)}")
                        raise kafka_error
                    
                    # Store embedding for future RAG queries - FIXED: use model_dump()
                    try:
                        self.rag_engine.store_event_embedding(tagged_event.model_dump())  # ✅ Fixed deprecation
                        logger.debug(f"Successfully stored embedding: {tagged_event.id}")
                    except Exception as rag_error:
                        logger.error(f"Failed to store embedding: {str(rag_error)}")
                        raise rag_error
                    
                    logger.info(f"✅ Tagged event {tagged_event.id}: {tagged_event.tags} ({tagged_event.priority})")
                    
                except Exception as processing_error:
                    logger.error(f"Error processing individual event {raw_event.get('id', 'unknown')}: {str(processing_error)}")
                    import traceback
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    continue  # Continue with next event instead of crashing
                    
        except KeyboardInterrupt:
            logger.info("Consumer stopped by user")
        except Exception as e:
            logger.error(f"Consumer error: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
        finally:
            self.consumer.close()
            self.producer.close()



if __name__ == "__main__":
    consumer = RAGKafkaConsumer()
    consumer.run()
