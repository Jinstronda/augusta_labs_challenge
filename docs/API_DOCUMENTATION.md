# API Documentation

## Overview

The Incentive Query UI backend provides a REST API for querying incentives and companies. The API uses natural language processing to classify queries and return relevant results with ranked matches.

**Base URL**: `http://localhost:8000`

**API Version**: 1.0

---

## Authentication

Currently, the API does not require authentication. For production deployment, consider adding API key authentication.

---

## Endpoints

### 1. Query Endpoint

**POST** `/api/query`

Main endpoint for natural language queries. Automatically classifies the query as either INCENTIVE or COMPANY search and returns appropriate results.

#### Request

```json
{
  "query": "What incentives are available for tech companies?"
}
```

**Parameters:**
- `query` (string, required): Natural language query (1-500 characters)

#### Response - Incentive Query

```json
{
  "query_type": "INCENTIVE",
  "entity": {
    "id": "2270",
    "title": "Apoio à Inovação Digital",
    "ai_description": "Incentivo para empresas tecnológicas...",
    "sector": "Tecnologia",
    "geo_requirement": "Portugal Continental",
    "eligible_actions": "Desenvolvimento de software, I&D",
    "funding_rate": "50%",
    "investment_eur": 500000.0,
    "top_companies": [
      {
        "id": 12345,
        "rank": 1,
        "name": "TechCorp SA",
        "company_score": 0.92,
        "semantic_score": 0.88,
        "cae": "62010 - Atividades de programação informática",
        "website": "https://techcorp.pt",
        "location": "Lisboa, Portugal"
      },
      {
        "id": 67890,
        "rank": 2,
        "name": "InnoSoft Lda",
        "company_score": 0.87,
        "semantic_score": 0.85,
        "cae": "62020 - Atividades de consultoria em informática",
        "website": "https://innosoft.pt",
        "location": "Porto, Portugal"
      }
      // ... 3 more companies
    ]
  },
  "processing_time": 0.45
}
```

#### Response - Company Query

```json
{
  "query_type": "COMPANY",
  "entity": {
    "id": 12345,
    "name": "TechCorp SA",
    "cae": "62010 - Atividades de programação informática",
    "activities": "Desenvolvimento de software empresarial",
    "website": "https://techcorp.pt",
    "location": "Rua da Tecnologia 123, Lisboa",
    "eligible_incentives": [
      {
        "id": "2270",
        "title": "Apoio à Inovação Digital",
        "rank": 1,
        "company_score": 0.92
      },
      {
        "id": "2228",
        "title": "Programa de Digitalização",
        "rank": 3,
        "company_score": 0.87
      }
      // ... up to 5 incentives
    ]
  },
  "processing_time": 0.32
}
```

#### Error Responses

**400 Bad Request** - Invalid query
```json
{
  "detail": "Query must be between 1 and 500 characters"
}
```

**404 Not Found** - No results
```json
{
  "detail": "No matching incentive found for query"
}
```

**500 Internal Server Error** - Server error
```json
{
  "detail": "An internal error occurred"
}
```

---

### 2. Get Incentive Detail

**GET** `/api/incentive/{incentive_id}`

Retrieve detailed information about a specific incentive including its top 5 matching companies.

#### Request

```
GET /api/incentive/2270
```

**Parameters:**
- `incentive_id` (string, path): Unique incentive identifier

#### Response

```json
{
  "id": "2270",
  "title": "Apoio à Inovação Digital",
  "ai_description": "Incentivo para empresas tecnológicas que desenvolvem soluções digitais inovadoras...",
  "sector": "Tecnologia",
  "geo_requirement": "Portugal Continental",
  "eligible_actions": "Desenvolvimento de software, I&D, Transformação digital",
  "funding_rate": "50%",
  "investment_eur": 500000.0,
  "top_companies": [
    {
      "id": 12345,
      "rank": 1,
      "name": "TechCorp SA",
      "company_score": 0.92,
      "semantic_score": 0.88,
      "cae": "62010 - Atividades de programação informática",
      "website": "https://techcorp.pt",
      "location": "Lisboa, Portugal"
    }
    // ... 4 more companies
  ]
}
```

#### Error Responses

**404 Not Found**
```json
{
  "detail": "Incentive not found"
}
```

---

### 3. Get Company Detail

**GET** `/api/company/{company_id}`

Retrieve detailed information about a specific company including its eligible incentives.

#### Request

```
GET /api/company/12345
```

**Parameters:**
- `company_id` (integer, path): Unique company identifier

#### Response

```json
{
  "id": 12345,
  "name": "TechCorp SA",
  "cae": "62010 - Atividades de programação informática",
  "activities": "Desenvolvimento de software empresarial, consultoria em TI, soluções cloud",
  "website": "https://techcorp.pt",
  "location": "Rua da Tecnologia 123, 1000-001 Lisboa",
  "eligible_incentives": [
    {
      "id": "2270",
      "title": "Apoio à Inovação Digital",
      "rank": 1,
      "company_score": 0.92
    },
    {
      "id": "2228",
      "title": "Programa de Digitalização",
      "rank": 3,
      "company_score": 0.87
    },
    {
      "id": "1288",
      "title": "Fundo de Inovação Tecnológica",
      "rank": 2,
      "company_score": 0.85
    }
    // ... up to 5 incentives
  ]
}
```

#### Error Responses

**404 Not Found**
```json
{
  "detail": "Company not found"
}
```

---

### 4. Health Check

**GET** `/health`

Check if the API is running and healthy.

#### Request

```
GET /health
```

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2025-01-07T10:30:00Z",
  "version": "1.0.0"
}
```

---

## Query Classification

The system uses GPT-4-mini to classify queries into two types:

### INCENTIVE Queries
Queries asking about funding programs, grants, or incentive details.

**Examples:**
- "What incentives are available for tech companies?"
- "Show me funding for renewable energy"
- "Apoios para exportação"
- "Programa de inovação digital"

### COMPANY Queries
Queries asking about specific companies or businesses.

**Examples:**
- "What incentives is TechCorp eligible for?"
- "Show me companies in software development"
- "Empresas de energia renovável"
- "TechCorp SA incentivos"

### Fallback Classification
If LLM classification fails, the system uses keyword-based fallback:
- Keywords like "empresa", "company", "negócio" → COMPANY
- Default → INCENTIVE

---

## Data Models

### IncentiveResult

```typescript
{
  id: string;                    // Unique incentive ID
  title: string;                 // Incentive title
  ai_description: string;        // Processed description
  sector: string;                // Industry sector
  geo_requirement: string;       // Geographic scope
  eligible_actions: string;      // Eligible activities
  funding_rate: string | null;   // Funding percentage
  investment_eur: number | null; // Max investment amount
  top_companies: CompanyMatch[]; // Top 5 companies
}
```

### CompanyMatch

```typescript
{
  id: number;              // Company ID
  rank: number;            // Rank (1-5)
  name: string;            // Company name
  company_score: number;   // Multi-factor score (0-1)
  semantic_score: number;  // Semantic similarity (0-1)
  cae: string | null;      // CAE classification
  website: string | null;  // Company website
  location: string | null; // Address
}
```

### CompanyResult

```typescript
{
  id: number;                        // Company ID
  name: string;                      // Company name
  cae: string | null;                // CAE classification
  activities: string | null;         // Business activities
  website: string | null;            // Company website
  location: string | null;           // Address
  eligible_incentives: IncentiveMatch[]; // Eligible incentives
}
```

### IncentiveMatch

```typescript
{
  id: string;          // Incentive ID
  title: string;       // Incentive title
  rank: number;        // Company's rank for this incentive
  company_score: number; // Company's score (0-1)
}
```

---

## Rate Limits

Currently, no rate limits are enforced. For production:
- Recommended: 100 requests per minute per IP
- Implement using middleware (e.g., slowapi)

---

## CORS Configuration

The API allows cross-origin requests from:
- Development: `http://localhost:5173` (Vite dev server)
- Production: Configure via `CORS_ORIGINS` environment variable

---

## Performance

### Expected Response Times
- `/api/query`: 300-1000ms (includes LLM classification)
- `/api/incentive/{id}`: 50-200ms (database lookup)
- `/api/company/{id}`: 50-200ms (database lookup)
- `/health`: <10ms

### Optimization
- Models loaded as singletons at startup (critical for performance)
- Database connection pooling
- Qdrant vector search for companies (fast)
- PostgreSQL keyword search for incentives (small dataset)

---

## Error Handling

### HTTP Status Codes
- `200 OK`: Successful request
- `400 Bad Request`: Invalid input
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable

### Error Response Format
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Example Usage

### cURL Examples

**Query for incentives:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "incentivos para tecnologia"}'
```

**Query for companies:**
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "empresas de software"}'
```

**Get incentive detail:**
```bash
curl http://localhost:8000/api/incentive/2270
```

**Get company detail:**
```bash
curl http://localhost:8000/api/company/12345
```

**Health check:**
```bash
curl http://localhost:8000/health
```

### JavaScript/TypeScript Examples

```typescript
// Query API
const response = await fetch('http://localhost:8000/api/query', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ query: 'incentivos para tecnologia' })
});
const data = await response.json();

// Get incentive detail
const incentive = await fetch('http://localhost:8000/api/incentive/2270')
  .then(res => res.json());

// Get company detail
const company = await fetch('http://localhost:8000/api/company/12345')
  .then(res => res.json());
```

### Python Examples

```python
import requests

# Query API
response = requests.post(
    'http://localhost:8000/api/query',
    json={'query': 'incentivos para tecnologia'}
)
data = response.json()

# Get incentive detail
incentive = requests.get('http://localhost:8000/api/incentive/2270').json()

# Get company detail
company = requests.get('http://localhost:8000/api/company/12345').json()
```

---

## Testing

### Manual Testing
Use the provided test scripts:
```bash
# Test query endpoint
python backend/tests/test_query_endpoint.py

# Test detail endpoints
python backend/tests/test_detail_endpoints.py

# Test error handling
python backend/tests/test_error_handling.py
```

### Automated Testing
```bash
cd backend
pytest tests/
```

---

## Deployment

### Development
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Production
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker
```bash
cd backend
docker build -t incentive-api .
docker run -p 8000:8000 --env-file ../.env incentive-api
```

---

## Support

- **Backend Code**: `backend/app/`
- **Tests**: `backend/tests/`
- **Configuration**: `backend/app/config.py`
- **Models**: `backend/app/models.py`

For issues or questions, refer to the troubleshooting guide in `docs/TROUBLESHOOTING_UI.md`.
