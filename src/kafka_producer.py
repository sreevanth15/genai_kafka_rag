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
                "source": "security_scanner",
                "event_type": "vulnerability_detected",
                "message": "Critical security vulnerability found in user upload module - SQL injection risk",
                "metadata": {
                    "severity": "critical",
                    "cve_id": "CVE-2024-1234",
                    "affected_module": "file_upload",
                    "scan_tool": "SecurityBot v2.1"
                }
            },
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source": "backup_service",
                "event_type": "backup_failure",
                "message": "Daily database backup failed - insufficient storage space on backup server",
                "metadata": {
                    "backup_type": "full_database",
                    "storage_used": "95%",
                    "required_space": "50GB",
                    "server": "backup-srv-01"
                }
            },
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source": "cdn_service",
                "event_type": "cache_miss",
                "message": "High cache miss ratio detected - 78% of requests bypassing CDN cache",
                "metadata": {
                    "cache_hit_ratio": "22%",
                    "region": "eu-west-1",
                    "total_requests": 15000,
                    "bandwidth_cost": "$240/hour"
                }
            },
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source": "kubernetes_cluster",
                "event_type": "pod_restart",
                "message": "Pod 'payment-processor-7b8c9d' restarted due to memory limit exceeded",
                "metadata": {
                    "pod_name": "payment-processor-7b8c9d",
                    "namespace": "production",
                    "memory_limit": "512Mi",
                    "restart_count": 3
                }
            },
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source": "fraud_detection",
                "event_type": "suspicious_transaction",
                "message": "Potential fraud detected - multiple high-value transactions from new user account",
                "metadata": {
                    "user_id": "user_789012",
                    "transaction_count": 5,
                    "total_amount": 12500.00,
                    "account_age_hours": 2,
                    "risk_score": 0.92
                }
            },
            {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "source": "load_balancer",
                "event_type": "health_check_failure",
                "message": "Backend server health check failed - server marked as unhealthy",
                "metadata": {
                    "server_ip": "10.0.2.45",
                    "response_time": 5000,
                    "status_code": 503,
                    "consecutive_failures": 3
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
