# RAG-Based Kafka Event Tagging System

A real-time event processing system that uses Retrieval-Augmented Generation (RAG) to intelligently tag Kafka events with AI-powered context awareness.

## 🚀 Quick Start

This system automatically processes raw events from Kafka, uses RAG to find similar historical events, and applies AI-powered tagging with priority levels (high/medium/low) for intelligent event categorization.

## 📋 Prerequisites

- **Docker & Docker Compose**: For running Kafka, Qdrant, and Kafdrop
- **Python 3.8+**: For running the application
- **Git**: For cloning the repository

## 🏗️ System Architecture

```
Raw Events → Kafka Consumer → RAG Enhancement → AI Tagging → Tagged Events → Dashboard
     ↓                              ↑
Event Database ← Vector Database ← Embeddings
```

## 📁 Project Structure

```
kafka-rag-tagging/
├── docker-compose.yml          # Docker services configuration
├── requirements.txt            # Python dependencies
├── .env                       # Environment variables (create this)
├── README.md                  # This file
├── config/
│   ├── __init__.py
│   └── settings.py            # Application configuration
├── src/
│   ├── __init__.py
│   ├── kafka_producer.py      # Sends sample events to Kafka
│   ├── kafka_consumer.py      # RAG-powered event processor
│   ├── rag_engine.py          # Vector similarity search
│   ├── genai_tagger.py        # AI tagging with Gemini
│   └── models/
│       ├── __init__.py
│       └── event_models.py    # Pydantic data models
├── data/
│   └── qdrant_storage/        # Persistent vector database storage
└── scripts/
    └── setup.sh               # Initial setup script
```

## ⚙️ Environment Setup

### 1. Clone the Repository

```bash
git clone 
cd kafka-rag-tagging
```

### 2. Create Virtual Environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create Environment File

Create a `.env` file in the root directory with the following variables:

```env
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_RAW_EVENTS_TOPIC=raw-events
KAFKA_TAGGED_EVENTS_TOPIC=tagged-events
KAFKA_CONSUMER_GROUP=rag-tagger-group

# GenAI Configuration (REQUIRED - Get from Google AI Studio)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=event_embeddings

# PostgreSQL Database (Optional - for future use)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=kafka_events
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password

# Application Settings
LOG_LEVEL=INFO
EMBEDDING_MODEL=all-MiniLM-L6-v2
MAX_SIMILAR_EVENTS=5
```

## 🔑 Required API Keys

### **Google Gemini API Key** (Required)

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and paste it as `GEMINI_API_KEY` in your `.env` file

### **OpenAI API Key** (Optional - Fallback)

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create a new secret key
3. Copy the key and paste it as `OPENAI_API_KEY` in your `.env` file

## 🐳 Docker Services Setup

### 1. Start All Services

```bash
docker-compose up -d
```

This starts:
- **Kafka**: Message streaming platform (port 9092)
- **Kafdrop**: Kafka Web UI (port 9000)
- **Qdrant**: Vector database for RAG (port 6333)

### 2. Verify Services Are Running

```bash
docker ps
```

You should see 3 containers running:
- `kafka-broker`
- `kafdrop-ui`
- `qdrant-vector-db`

### 3. Create Kafka Topics

```bash
# Create raw events topic
docker exec -it kafka-broker /opt/kafka/bin/kafka-topics.sh --create --topic raw-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Create tagged events topic
docker exec -it kafka-broker /opt/kafka/bin/kafka-topics.sh --create --topic tagged-events --bootstrap-server localhost:9092 --partitions 3 --replication-factor 1

# Verify topics were created
docker exec -it kafka-broker /opt/kafka/bin/kafka-topics.sh --list --bootstrap-server localhost:9092
```

## 🎮 Running the Application

### Option 1: Quick Test (Recommended for First Run)

**Terminal 1 - Start the RAG Consumer:**
```bash
python -m src.kafka_consumer
```

**Terminal 2 - Send Sample Events:**
```bash
python -m src.kafka_producer
```

### Option 2: Manual Event Production

You can send custom events using the Kafka console producer:

```bash
docker exec -it kafka-broker /opt/kafka/bin/kafka-console-producer.sh --bootstrap-server localhost:9092 --topic raw-events
```

Then paste JSON events like:
```json
{"id": "001", "timestamp": "2025-01-15T10:00:00Z", "source": "auth_service", "event_type": "login_attempt", "message": "Failed login attempt for user@example.com", "metadata": {"ip": "192.168.1.1"}}
```

## 📊 Monitoring & Verification

### 1. Kafka Web UI (Kafdrop)
- **URL**: http://localhost:9000
- **Purpose**: View Kafka topics, messages, and consumer groups
- **Usage**: Navigate to topics → `raw-events` or `tagged-events` to see messages

### 2. Qdrant Web UI
- **URL**: http://localhost:6333/dashboard
- **Purpose**: View vector database collections and search results
- **Usage**: Go to Collections → `event_embeddings` to see stored event embeddings

### 3. Check Tagged Events

```bash
# View tagged events in real-time
docker exec -it kafka-broker /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic tagged-events --from-beginning
```

## 🔍 Expected Output

When running successfully, you should see:

### **Consumer Logs:**
```
INFO:src.rag_engine:RAG Engine initialized ✅
INFO:src.genai_tagger:GenAI Tagger initialized ✅
INFO:__main__:RAG Kafka Consumer initialized ✅
INFO:__main__:Processing event: 
INFO:src.genai_tagger:Generated tags for event : ['security', 'authentication', 'failed_login']
INFO:__main__:✅ Tagged event : ['security', 'authentication', 'failed_login'] (high)
```

### **Tagged Event Output:**
```json
{
  "id": "event-123",
  "timestamp": "2025-01-15T10:00:00Z",
  "source": "auth_service",
  "event_type": "login_attempt",
  "message": "Failed login attempt for user@example.com",
  "tags": ["security", "authentication", "failed_login", "suspicious"],
  "priority": "high",
  "confidence_score": 0.92,
  "similar_events": ["event-456", "event-789"],
  "rag_context": "Similar events from knowledge base: ..."
}
```

## 🛠️ Troubleshooting

### **Issue: Consumer fails with Pydantic error**
**Solution**: The code uses `model_dump()` which requires Pydantic v2. Ensure requirements.txt has the correct version.

### **Issue: "No similar events found"**
**Solution**: This is normal for the first few events. The system builds its knowledge base over time.

### **Issue: Gemini API errors**
**Solution**: 
- Verify your `GEMINI_API_KEY` in `.env`
- Check your Google AI Studio quota
- Ensure the API key has proper permissions

### **Issue: Kafka connection errors**
**Solution**:
```bash
# Restart Kafka services
docker-compose down
docker-compose up -d
# Wait 30 seconds for services to start
```

### **Issue: Empty Qdrant dashboard**
**Solution**:
- Ensure consumer is processing events
- Check `./data/qdrant_storage/` directory exists
- Verify Qdrant container logs: `docker logs qdrant-vector-db`

## 🧪 Testing the System

### 1. Basic Functionality Test

```bash
# Terminal 1: Start consumer
python -m src.kafka_consumer

# Terminal 2: Send test events
python -m src.kafka_producer

# Terminal 3: Monitor tagged events
docker exec -it kafka-broker /opt/kafka/bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic tagged-events --from-beginning
```

### 2. Custom Event Test

Send your own events by modifying the `sample_events` list in `src/kafka_producer.py` or using the Kafka console producer.

## 🔧 Development

### **Adding New Event Types**
1. Modify the sample events in `src/kafka_producer.py`
2. Update the tagging prompt in `src/genai_tagger.py` if needed
3. Restart the consumer to process new event patterns

### **Improving RAG Context**
1. Add more historical events to build a better knowledge base
2. Adjust `MAX_SIMILAR_EVENTS` in `.env` to retrieve more/fewer similar events
3. Modify the similarity threshold in `src/rag_engine.py`

### **Customizing AI Tagging**
1. Edit the prompt in `src/genai_tagger.py`
2. Add custom business logic for priority assignment
3. Implement feedback mechanisms for tag corrections

## 📝 Next Steps

1. **Dashboard Development**: Build Streamlit dashboard for real-time visualization
2. **Feedback System**: Implement UI for correcting AI-generated tags
3. **Database Integration**: Add PostgreSQL for persistent event storage
4. **Alert System**: Create alerts based on tagged events and priorities
5. **Model Fine-tuning**: Use feedback data to improve tagging accuracy

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test with the provided sample events
4. Submit a pull request with clear description

## 📄 License

[Add your license information here]

**Need Help?** Check the troubleshooting section above or create an issue in the repository.