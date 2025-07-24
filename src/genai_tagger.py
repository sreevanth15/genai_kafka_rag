import google.generativeai as genai
from typing import List, Dict, Tuple
import json
import logging
from config.settings import settings

logger = logging.getLogger(__name__)

class GenAITagger:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("GenAI Tagger initialized ✅")

    def generate_tags_with_rag(self, event: Dict, rag_context: str) -> Tuple[List[str], str, float]:
        """Generate tags using RAG context"""
        prompt = self._build_rag_prompt(event, rag_context)
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_response(response.text)
            
            tags = result.get("tags", [])
            priority = result.get("priority", "medium")
            confidence = result.get("confidence", 0.7)
            
            logger.info(f"Generated tags for event {event['id']}: {tags}")
            return tags, priority, confidence
            
        except Exception as e:
            logger.error(f"Error generating tags: {e}")
            return ["error", "unclassified"], "low", 0.5

    def _build_rag_prompt(self, event: Dict, rag_context: str) -> str:
        """Build prompt with RAG context"""
        return f"""
You are an intelligent event tagging system. Your task is to analyze system events and assign appropriate tags and priority levels.

Current Event to Tag:
- Message: {event['message']}
- Source: {event['source']}
- Event Type: {event['event_type']}
- Metadata: {json.dumps(event.get('metadata', {}), indent=2)}

{rag_context}

Based on the current event and similar events from the knowledge base, provide:

1. **Tags**: 2-4 relevant tags (e.g., security, authentication, error, performance, business)
2. **Priority**: high/medium/low based on severity and business impact
3. **Confidence**: Your confidence level (0.0-1.0) in the tagging decision

Guidelines:
- Security events (failed logins, suspicious activity): high priority, tags like 'security', 'authentication', 'suspicious'
- Performance issues (timeouts, slow responses): medium-high priority, tags like 'performance', 'timeout', 'latency'
- Business events (payments, transactions): priority based on impact, tags like 'business', 'payment', 'transaction'
- System errors: medium priority, tags like 'error', 'system', 'monitoring'
- User activities: low-medium priority, tags like 'user', 'activity', 'engagement'

Respond in JSON format:
{{
    "tags": ["tag1", "tag2", "tag3"],
    "priority": "high|medium|low",
    "confidence": 0.95,
    "reasoning": "Brief explanation of your decision"
}}
"""

    def _parse_response(self, response_text: str) -> Dict:
        """Parse GenAI response"""
        try:
            # Clean response text
            response_text = response_text.strip()
            if response_text.startswith("```"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            result = json.loads(response_text)
            return result

        except json.JSONDecodeError:
            # Fallback parsing
            logger.warning("Failed to parse JSON response, using fallback")
            return {
                "tags": ["unclassified"],
                "priority": "medium",
                "confidence": 0.5,
                "reasoning": "Failed to parse response"
            }
