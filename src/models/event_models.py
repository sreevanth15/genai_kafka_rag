from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class RawEvent(BaseModel):
    id: str
    timestamp: datetime
    source: str
    event_type: str
    message: str
    metadata: Dict[str, Any] = {}

class TaggedEvent(BaseModel):
    id: str
    timestamp: datetime
    source: str
    event_type: str
    message: str
    metadata: Dict[str, Any] = {}
    tags: List[str]
    priority: str  # high, medium, low
    confidence_score: float
    similar_events: List[str] = []
    rag_context: Optional[str] = None

class FeedbackEvent(BaseModel):
    event_id: str
    original_tags: List[str]
    corrected_tags: List[str]
    feedback_reason: str
    user_id: str
    timestamp: datetime
