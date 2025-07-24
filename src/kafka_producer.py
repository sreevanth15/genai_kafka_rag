from kafka import KafkaProducer
import json
import time
import uuid
from datetime import datetime
from typing import List, Dict
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EventProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda m: json.dumps(m, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        logger.info("Kafka Producer initialized ✅")

    def send_event(self, event: Dict) -> None:
        """Send a single event to Kafka"""
        try:
            future = self.producer.send(
                settings.KAFKA_RAW_EVENTS_TOPIC,
                key=event.get('id'),
                value=event
            )
            # Wait for acknowledgment
            future.get(timeout=10)
            logger.info(f"Event sent successfully: {event['id']}")
        except Exception as e:
            logger.error(f"Failed to send event: {e}")

    def send_sample_events(self) -> None:
        """Send sample events for testing"""
        sample_events = [
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source": "auth_service",
                "event_type": "login_attempt",
                "message": "Failed login attempt for user john@example.com from IP 192.168.1.100",
                "metadata": {
                    "user_email": "john@example.com",
                    "ip_address": "192.168.1.100",
                    "user_agent": "Mozilla/5.0",
                    "attempt_count": 3
                }
            },
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source": "payment_service",
                "event_type": "transaction",
                "message": "Payment processing timeout for transaction ID 12345",
                "metadata": {
                    "transaction_id": "12345",
                    "amount": 299.99,
                    "currency": "USD",
                    "merchant": "example_store"
                }
            },
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source": "api_gateway",
                "event_type": "error",
                "message": "Database connection timeout on /api/users endpoint",
                "metadata": {
                    "endpoint": "/api/users",
                    "method": "GET",
                    "response_time": 30000,
                    "error_code": "DB_TIMEOUT"
                }
            },
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source": "user_service",
                "event_type": "registration",
                "message": "New user registration from mobile app",
                "metadata": {
                    "platform": "mobile",
                    "app_version": "2.1.0",
                    "device_type": "Android",
                    "location": "New York, US"
                }
            }
        ]

        for event in sample_events:
            self.send_event(event)
            time.sleep(1)  # Small delay between events

    def close(self):
        """Close the producer"""
        self.producer.close()
        logger.info("Producer closed")

if __name__ == "__main__":
    producer = EventProducer()
    try:
        producer.send_sample_events()
    finally:
        producer.close()
