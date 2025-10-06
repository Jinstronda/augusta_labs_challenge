# Incentive Query API - Backend

FastAPI backend for the Incentive Query UI application.

## Features

- **Query Classification**: Uses GPT-5-mini to classify queries as INCENTIVE or COMPANY
- **Semantic Search**: Vector search for companies using Qdrant and sentence transformers
- **Database Integration**: PostgreSQL for incentives and companies data
- **Singleton Model Loading**: ML models loaded once at startup for optimal performance
- **Health Checks**: Built-in health check endpoint for monitoring

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Configuration management
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py        # API endpoints
│   └── services/
│       ├── __init__.py
│       ├── database.py      # Database operations
│       ├── classifier.py    # Query classification
│       └── search.py        # Semantic search
├── requirements.txt         # Python dependencies
├── Dockerfile              # Docker configuration
└── README.md               # This file
```

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database with incentives and companies data
- Qdrant vector database with company embeddings
- OpenAI API key

### Installation

1. **Create virtual environment** (or use conda):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:

Create a `config.env` file in the project root (or use existing one):
```env
# Database
DB_NAME=incentives_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=companies

# OpenAI
OPEN_AI=your_openai_api_key
```

### Running the Server

**Development mode** (with auto-reload):
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode**:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Docker

### Build image:
```bash
docker build -t incentive-query-api .
```

### Run container:
```bash
docker run -p 8000:8000 --env-file config.env incentive-query-api
```

## API Endpoints

### Health Check
```
GET /health
```

Returns server health status and model loading status.

### Query (Coming in Task 6)
```
POST /api/query
```

Main query endpoint for searching incentives or companies.

### Incentive Detail (Coming in Task 6.5)
```
GET /api/incentive/:id
```

Get detailed information about a specific incentive.

### Company Detail (Coming in Task 6.5)
```
GET /api/company/:id
```

Get detailed information about a specific company.

## Development

### Running Tests
```bash
pytest
```

### Code Style
```bash
# Format code
black app/

# Lint code
flake8 app/
```

## Performance Notes

### Model Loading
Models are loaded **once at startup** as singletons in the `lifespan` context manager. This is critical for performance:

- ❌ **Bad**: Loading model on every request (~2-3 seconds per request)
- ✅ **Good**: Loading model once at startup (~2-3 seconds total)

### Caching
- Database connections use connection pooling
- Qdrant client is reused across requests
- Embedding model is shared across all requests

## Troubleshooting

### Models not loading
Check the startup logs for errors. Common issues:
- Missing dependencies (install with `pip install -r requirements.txt`)
- Insufficient memory (sentence transformers need ~500MB RAM)
- Network issues downloading models (first run downloads from HuggingFace)

### Database connection errors
- Verify PostgreSQL is running
- Check `config.env` has correct credentials
- Ensure database has required tables (incentives, companies)

### Qdrant connection errors
- Verify Qdrant is running (`docker ps` if using Docker)
- Check `QDRANT_HOST` and `QDRANT_PORT` in config
- Ensure collection exists (check with Qdrant dashboard)

## License

MIT
