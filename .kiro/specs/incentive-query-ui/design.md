# Design Document

## Overview

The Incentive Query UI is a full-stack web application that provides a ChatGPT-like interface for querying incentives and companies. The system uses modern JavaScript frameworks and Python backend services to deliver fast, intelligent search results.

**Tech Stack:**
- **Frontend**: React 18 + Vite + TailwindCSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (existing)
- **LLM**: OpenAI GPT-4-mini for query classification
- **Embeddings**: Sentence Transformers (existing pipeline)
- **Deployment**: Docker + Static hosting (Vercel/Netlify)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  React App (Vite)                                     │  │
│  │  - Chat Interface Component                           │  │
│  │  - Query Input Component                              │  │
│  │  - Results Display Component                          │  │
│  │  - TailwindCSS Styling                                │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP/REST
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI Server                                       │  │
│  │  - /api/query endpoint                                │  │
│  │  - Query Classifier (GPT-4-mini)                      │  │
│  │  - Semantic Search Service                            │  │
│  │  - Database Service                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ SQL
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    PostgreSQL Database                       │
│  Tables:                                                     │
│  - incentives (incentive_id, title, sector, geo_requirement,│
│                ai_description, eligible_actions,             │
│                funding_rate, investment_eur,                 │
│                top_5_companies, top_5_companies_scored)      │
│  - companies (company_id, company_name, cae_primary_label,  │
│               trade_description_native, website,             │
│               location_lat, location_lon, location_address,  │
│               location_api_status, location_updated_at,      │
│               eligible_incentives JSONB) ← NEW!              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Vector Search
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Qdrant Vector DB                        │
│  Collection: companies                                       │
│  - Embeddings for semantic search                           │
│  - Payload: company metadata                                 │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### Frontend Components

#### 1. ChatInterface Component
```typescript
interface ChatMessage {
  id: string;
  type: 'user' | 'assistant';
  content: string | ResultContent;
  timestamp: Date;
}

interface ResultContent {
  queryType: 'INCENTIVE' | 'COMPANY';
  entity: IncentiveResult | CompanyResult;
  relatedEntities: Company[] | Incentive[];
}
```

**Responsibilities:**
- Manage chat history state
- Handle message rendering
- Auto-scroll to latest message
- Provide "New Chat" functionality

#### 2. QueryInput Component
```typescript
interface QueryInputProps {
  onSubmit: (query: string) => Promise<void>;
  isLoading: boolean;
}
```

**Responsibilities:**
- Text input with auto-resize
- Submit on Enter (Shift+Enter for new line)
- Loading state with spinner
- Input validation

#### 3. ResultsDisplay Component
```typescript
interface ResultsDisplayProps {
  queryType: 'INCENTIVE' | 'COMPANY';
  data: IncentiveResult | CompanyResult;
}
```

**Responsibilities:**
- Render incentive cards with company list
- Render company cards with incentive list
- Display scores, rankings, and metadata
- Provide expandable sections for details

#### 4. IncentiveCard Component
```typescript
interface IncentiveCardProps {
  incentive: {
    id: string;
    title: string;
    description: string;
    sector: string;
    geoRequirement: string;
    eligibleActions: string;
  };
  companies: Array<{
    id: number;
    rank: number;
    name: string;
    score: number;
    cae: string;
    website: string;
    location: string;
  }>;
  onCompanyClick: (companyId: number) => void;
}
```

**Responsibilities:**
- Display incentive metadata
- Show top 5 companies in ranked order as clickable cards
- Provide visual score indicators (progress bars)
- Handle company card clicks to navigate to company detail view
- Link to company websites

#### 5. CompanyCard Component
```typescript
interface CompanyCardProps {
  company: {
    id: number;
    name: string;
    cae: string;
    activities: string;
    website: string;
    location: string;
  };
  incentives: Array<{
    id: string;
    title: string;
    rank: number;
    score: number;
  }>;
  onIncentiveClick: (incentiveId: string) => void;
}
```

**Responsibilities:**
- Display company metadata
- Show eligible incentives sorted by score as clickable cards
- Provide visual rank indicators
- Handle incentive card clicks to navigate to incentive detail view
- Link to company website

### Backend API

#### 1. Query Endpoint
```python
@app.post("/api/query")
async def query(request: QueryRequest) -> QueryResponse:
    """
    Main query endpoint that classifies and routes queries.
    
    Request:
        {
            "query": "What incentives are available for tech companies?"
        }
    
    Response:
        {
            "query_type": "INCENTIVE",
            "entity": {...},
            "related_entities": [...],
            "processing_time": 0.5
        }
    """

@app.get("/api/incentive/{incentive_id}")
async def get_incentive(incentive_id: str) -> IncentiveResult:
    """
    Get single incentive by ID with top 5 companies.
    
    Response:
        {
            "id": "INC001",
            "title": "Digital Innovation Fund",
            "top_companies": [...]
        }
    """

@app.get("/api/company/{company_id}")
async def get_company(company_id: int) -> CompanyResult:
    """
    Get single company by ID with eligible incentives.
    
    Response:
        {
            "id": 12345,
            "name": "TechCorp",
            "eligible_incentives": [...]
        }
    """
```

#### 2. Query Classifier Service
```python
from openai import OpenAI

class QueryClassifier:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPEN_AI"))
        self.prompt_template = """Classify this query as either "INCENTIVE" or "COMPANY".

Query: {query}

Rules:
- If asking about funding, programs, grants, or incentive names → INCENTIVE
- If asking about businesses, companies, or industries → COMPANY
- If ambiguous → INCENTIVE

Respond with ONLY a JSON object: {{"type": "INCENTIVE"}} or {{"type": "COMPANY"}}
"""
    
    def classify(self, query: str) -> str:
        """
        Use GPT-5-mini to classify query as INCENTIVE or COMPANY.
        
        Returns: "INCENTIVE" or "COMPANY"
        """
        prompt = self.prompt_template.format(query=query)
        
        print(f"[CLASSIFIER] Query: {query[:100]}...")
        print(f"[CLASSIFIER] Prompt length: {len(prompt)} characters")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                # GPT-5 models only support temperature=1 (default)
                max_completion_tokens=100
            )
            
            message = response.choices[0].message
            content = message.content
            
            if not content:
                print(f"[CLASSIFIER] Empty response from API")
                if hasattr(message, 'refusal') and message.refusal:
                    print(f"[CLASSIFIER] Model refused: {message.refusal}")
                return "INCENTIVE"  # Default fallback
            
            content = content.strip()
            print(f"[CLASSIFIER] Response: {content}")
            
            # Parse JSON response
            result = json.loads(content)
            query_type = result.get("type", "INCENTIVE")
            
            print(f"[CLASSIFIER] Classified as: {query_type}")
            return query_type
            
        except json.JSONDecodeError as e:
            print(f"[CLASSIFIER] JSON parse error: {e}")
            # Fallback: check for keywords
            return self.fallback_classify(query)
        except Exception as e:
            print(f"[CLASSIFIER] Error: {e}")
            return self.fallback_classify(query)
    
    def fallback_classify(self, query: str) -> str:
        """Keyword-based fallback classification."""
        query_lower = query.lower()
        
        company_keywords = ['empresa', 'company', 'negócio', 'business']
        incentive_keywords = ['incentivo', 'incentive', 'apoio', 'funding', 
                             'financiamento', 'grant', 'programa', 'program']
        
        if any(kw in query_lower for kw in company_keywords):
            return "COMPANY"
        return "INCENTIVE"  # Default to incentive search
```

#### 3. Semantic Search Service
```python
class SemanticSearchService:
    # Singleton pattern - load model once at app startup
    _instance = None
    _model = None
    _qdrant_client = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Load model once
            cls._model = SentenceTransformer(
                'paraphrase-multilingual-MiniLM-L12-v2',
                device='cuda' if torch.cuda.is_available() else 'cpu'
            )
            cls._qdrant_client = QdrantClient(path="./qdrant_storage")
            print("[SEARCH] Model loaded successfully (singleton)")
        return cls._instance
    
    def __init__(self):
        self.model = self._model
        self.qdrant_client = self._qdrant_client
        self.db_conn_params = {...}
    
    def search_incentives(self, query: str, top_k: int = 1) -> List[Dict]:
        """
        Search incentives using PostgreSQL keyword search.
        
        Since the incentive dataset is small (~300 records), we use
        simple keyword matching instead of vector embeddings.
        
        Query:
        SELECT incentive_id, title, sector, ai_description,
               geo_requirement, eligible_actions
        FROM incentives
        WHERE LOWER(title) LIKE LOWER(%s)
           OR LOWER(ai_description) LIKE LOWER(%s)
           OR LOWER(sector) LIKE LOWER(%s)
        LIMIT %s
        
        For better results, can upgrade to full-text search:
        WHERE to_tsvector('portuguese', title || ' ' || 
              COALESCE(ai_description, '') || ' ' || 
              COALESCE(sector, '')) @@ 
              plainto_tsquery('portuguese', %s)
        """
    
    def search_companies(self, query: str, top_k: int = 1) -> List[Dict]:
        """
        Search companies using Qdrant vector search.
        
        Uses existing Qdrant collection 'companies' with pre-computed
        embeddings. Returns companies with cosine similarity scores.
        """
        query_vector = self.model.encode(query).tolist()
        
        results = self.qdrant_client.query_points(
            collection_name="companies",
            query=query_vector,
            limit=top_k
        ).points
        
        # Enrich with PostgreSQL data
        company_ids = [r.id for r in results]
        return self.enrich_companies_from_postgres(company_ids)
```

**Search Strategy:**
- **Companies**: Use existing Qdrant vector DB with pre-computed embeddings (250k records)
- **Incentives**: Use PostgreSQL keyword search (small dataset ~300 records, no embeddings needed for MVP)
- Return single best match for specific queries
- Future: Add incentive embeddings for multi-result queries

#### 4. Database Service
```python
class DatabaseService:
    def __init__(self):
        self.conn_params = {
            'dbname': os.getenv('DB_NAME', 'incentives_db'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432')
        }
    
    def get_incentive_with_companies(self, incentive_id: str) -> Dict:
        """
        Retrieve incentive and parse top_5_companies_scored JSON.
        
        Query:
        SELECT incentive_id, title, sector, geo_requirement,
               ai_description, eligible_actions, funding_rate,
               investment_eur, top_5_companies_scored
        FROM incentives
        WHERE incentive_id = %s
        """
    
    def get_company_with_incentives(self, company_id: int) -> Dict:
        """
        Retrieve company with pre-computed eligible incentives.
        
        Query:
        SELECT company_id, company_name, cae_primary_label,
               trade_description_native, website,
               location_address, eligible_incentives
        FROM companies
        WHERE company_id = %s
        
        The eligible_incentives JSONB column contains:
        [
            {
                "incentive_id": "INC001",
                "title": "Digital Innovation Fund",
                "rank": 1,
                "company_score": 0.92
            },
            ...
        ]
        
        This is pre-computed by a batch script that runs after
        incentive processing completes.
        """
```

## Data Models

### Frontend Models

```typescript
// Incentive Result
interface IncentiveResult {
  id: string;  // incentive_id
  title: string;
  aiDescription: string;  // ai_description
  sector: string;
  geoRequirement: string;  // geo_requirement
  eligibleActions: string;  // eligible_actions
  fundingRate: string | null;  // funding_rate
  investmentEur: number | null;  // investment_eur
  topCompanies: CompanyMatch[];  // from top_5_companies_scored JSON
}

interface CompanyMatch {
  id: number;  // company_id
  rank: number;  // from JSON
  name: string;  // company_name
  companyScore: number;  // company_score from JSON
  semanticScore: number;  // semantic_score from JSON
  cae: string;  // cae_primary_label
  website: string | null;
  location: string | null;  // location_address
}

// Company Result
interface CompanyResult {
  id: number;  // company_id
  name: string;  // company_name
  cae: string;  // cae_primary_label
  activities: string;  // trade_description_native
  website: string | null;
  location: string | null;  // location_address
  eligibleIncentives: IncentiveMatch[];  // parsed from top_5_companies_scored
}

interface IncentiveMatch {
  id: string;
  title: string;
  rank: number;
  companyScore: number;
}
```

### Backend Models

```python
from pydantic import BaseModel
from typing import List, Optional

class QueryRequest(BaseModel):
    query: str

class CompanyMatch(BaseModel):
    id: int
    rank: int
    name: str
    company_score: float
    semantic_score: float
    cae: Optional[str]
    website: Optional[str]
    location: Optional[str]

class IncentiveResult(BaseModel):
    id: str  # incentive_id
    title: str
    ai_description: str
    sector: str
    geo_requirement: str
    eligible_actions: str
    funding_rate: Optional[str]
    investment_eur: Optional[float]
    top_companies: List[CompanyMatch]  # from top_5_companies_scored JSON

class IncentiveMatch(BaseModel):
    id: str
    title: str
    rank: int
    company_score: float

class CompanyResult(BaseModel):
    id: int  # company_id
    name: str  # company_name
    cae: Optional[str]  # cae_primary_label
    activities: Optional[str]  # trade_description_native
    website: Optional[str]
    location: Optional[str]  # location_address
    eligible_incentives: List[IncentiveMatch]  # from top_5_companies_scored JSON

class QueryResponse(BaseModel):
    query_type: str  # "INCENTIVE" or "COMPANY"
    entity: IncentiveResult | CompanyResult
    processing_time: float
```

## Error Handling

### Frontend Error Handling
```typescript
try {
  const response = await fetch('/api/query', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
  
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  
  const data = await response.json();
  // Handle success
} catch (error) {
  if (error.message.includes('Failed to fetch')) {
    showError('Service unavailable. Please try again later.');
  } else if (error.message.includes('timeout')) {
    showError('Request timed out. Please try a simpler query.');
  } else {
    showError('An error occurred. Please try again.');
  }
}
```

### Backend Error Handling
```python
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "An internal error occurred"}
    )

@app.post("/api/query")
async def query(request: QueryRequest):
    try:
        # Classification
        query_type = classifier.classify(request.query)
    except OpenAIError:
        # Fallback to keyword-based classification
        query_type = fallback_classify(request.query)
    
    try:
        # Search and retrieve
        if query_type == "INCENTIVE":
            result = search_service.search_incentives(request.query)
        else:
            result = search_service.search_companies(request.query)
        
        if not result:
            raise HTTPException(404, "No results found")
        
        return QueryResponse(...)
    except DatabaseError as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(500, "Database error occurred")
```

## Testing Strategy

### Frontend Testing
- **Unit Tests**: Jest + React Testing Library
  - Test individual components (QueryInput, ResultsDisplay)
  - Test state management and hooks
  - Test utility functions

- **Integration Tests**: Playwright
  - Test full query flow (input → API → results)
  - Test error scenarios
  - Test responsive design

### Backend Testing
- **Unit Tests**: pytest
  - Test query classifier with various inputs
  - Test semantic search service
  - Test database service queries
  - Mock external dependencies (OpenAI, database)

- **Integration Tests**: pytest + TestClient
  - Test `/api/query` endpoint end-to-end
  - Test with real database (test fixtures)
  - Test error handling and edge cases

### Performance Testing
- **Load Testing**: k6 or Locust
  - Test API response times under load
  - Test concurrent query handling
  - Identify bottlenecks

## Deployment Architecture

### Development Environment
```
frontend/          # React app
  ├── src/
  ├── public/
  ├── package.json
  └── vite.config.ts

backend/           # FastAPI app
  ├── app/
  │   ├── main.py
  │   ├── services/
  │   └── models/
  ├── requirements.txt
  └── Dockerfile

docker-compose.yml # Local development setup
```

### Production Deployment

**Option 1: Docker Compose (Simple)**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://...
      - OPENAI_API_KEY=...
  
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

**Option 2: Separate Hosting (Scalable)**
- Frontend: Vercel/Netlify (static build)
- Backend: Railway/Render/Fly.io (containerized)
- Database: Existing PostgreSQL instance

### Environment Variables
```bash
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/dbname
OPENAI_API_KEY=sk-...
CORS_ORIGINS=https://your-frontend.com
LOG_LEVEL=INFO

# Frontend
VITE_API_URL=https://your-backend.com
```

## Performance Optimizations

### Frontend Optimizations
1. **Code Splitting**: Lazy load components
   ```typescript
   const ResultsDisplay = lazy(() => import('./ResultsDisplay'));
   ```

2. **Memoization**: Prevent unnecessary re-renders
   ```typescript
   const MemoizedCard = memo(IncentiveCard);
   ```

3. **Debouncing**: Limit API calls
   ```typescript
   const debouncedSearch = useDebouncedCallback(
     (query) => fetchResults(query),
     500
   );
   ```

4. **Bundle Optimization**: Vite tree-shaking and minification

### Backend Optimizations
1. **Singleton Model Loading**: Load once at startup (CRITICAL)
   ```python
   # In main.py startup event
   @app.on_event("startup")
   async def startup_event():
       # Initialize singleton services
       search_service = SemanticSearchService()  # Loads model once
       print("[STARTUP] Models loaded successfully")
   ```

2. **Connection Pooling**: Reuse database connections
   ```python
   engine = create_engine(DATABASE_URL, pool_size=10, max_overflow=20)
   ```

3. **Async Operations**: Use FastAPI async for I/O
   ```python
   async def search_incentives(query: str):
       async with db.connection() as conn:
           ...
   ```

4. **Batch Database Queries**: Minimize round trips
   ```python
   # Get all company IDs from JSON, then batch fetch
   company_ids = extract_company_ids(top_5_companies_scored)
   companies = await db.fetch_companies_batch(company_ids)
   ```

## Security Considerations

1. **Input Validation**: Sanitize user queries
   ```python
   class QueryRequest(BaseModel):
       query: str = Field(..., min_length=1, max_length=500)
   ```

2. **CORS Configuration**: Restrict origins
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://your-frontend.com"],
       allow_methods=["POST"],
   )
   ```

3. **Environment Variables**: Never commit secrets
   - Use `.env` files locally
   - Use platform secrets in production

## UI/UX Design

### Color Scheme (TailwindCSS)
- Primary: `blue-600` (links, buttons)
- Success: `green-500` (high scores)
- Warning: `yellow-500` (medium scores)
- Background: `gray-50` (light mode), `gray-900` (dark mode)
- Cards: `white` with `shadow-lg`

### Typography
- Headings: `font-bold text-2xl`
- Body: `font-normal text-base`
- Metadata: `text-sm text-gray-600`

### Layout
```
┌─────────────────────────────────────────┐
│  [Logo]  Incentive Query System    [New]│
├─────────────────────────────────────────┤
│                                         │
│  User: What incentives for tech?       │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ Assistant:                        │ │
│  │                                   │ │
│  │ [Incentive Card]                  │ │
│  │   Title: Digital Innovation Fund  │ │
│  │   Sector: Technology              │ │
│  │   Top Companies:                  │ │
│  │   1. TechCorp (Score: 0.92) ████  │ │
│  │   2. InnoSoft (Score: 0.87) ███   │ │
│  │   ...                             │ │
│  └───────────────────────────────────┘ │
│                                         │
├─────────────────────────────────────────┤
│  [Type your query here...]        [→]  │
└─────────────────────────────────────────┘
```

### Responsive Design
- Desktop: Full width with max-width 1200px
- Tablet: Stacked cards, full width
- Mobile: Single column, touch-optimized

## Reverse Index Generation

### Purpose
Pre-compute which incentives each company is eligible for, enabling fast company queries without scanning all incentives.

### Script: `build_company_incentive_index.py`

```python
"""
Build reverse index: company_id → eligible incentives

This script runs after batch processing completes and builds
a JSONB column in the companies table containing each company's
top 5 eligible incentives ranked by score.

Usage:
    python scripts/build_company_incentive_index.py
"""

def build_reverse_index():
    """
    Algorithm:
    1. Query all incentives with top_5_companies_scored
    2. For each incentive:
       - Parse top_5_companies_scored JSON
       - Extract companies with their ranks and scores
       - Add to company→incentives mapping
    3. For each company:
       - Sort incentives by company_score (descending)
       - Keep top 5 incentives
       - Save to companies.eligible_incentives as JSONB
    
    Data structure:
    company_incentives = {
        company_id: [
            {
                "incentive_id": "INC001",
                "title": "Digital Innovation",
                "rank": 1,
                "company_score": 0.92
            },
            ...
        ]
    }
    """
```

### Database Schema Update

```sql
-- Add eligible_incentives column to companies table
ALTER TABLE companies 
ADD COLUMN IF NOT EXISTS eligible_incentives JSONB;

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_companies_eligible_incentives 
ON companies USING GIN (eligible_incentives);
```

### Example Data

**companies.eligible_incentives:**
```json
[
  {
    "incentive_id": "INC001",
    "title": "Digital Innovation Fund",
    "rank": 1,
    "company_score": 0.92
  },
  {
    "incentive_id": "INC045",
    "title": "Green Energy Transition",
    "rank": 3,
    "company_score": 0.87
  },
  {
    "incentive_id": "INC023",
    "title": "Export Support Program",
    "rank": 2,
    "company_score": 0.85
  }
]
```

### Performance Impact

**Before (scanning all incentives):**
- Query time: ~500ms for 300 incentives
- Requires parsing all top_5_companies_scored JSON

**After (pre-computed index):**
- Query time: ~5ms (single row lookup)
- Direct JSONB column access

## Navigation and Interactivity

### Clickable UI Flow

```
User Query → Result Display
     ↓
[Incentive Card]
  - Click company → Navigate to Company Detail View
  - Shows: Company info + eligible incentives
     ↓
[Company Card]
  - Click incentive → Navigate to Incentive Detail View
  - Shows: Incentive info + top 5 companies
```

### Implementation
- Use React Router for navigation
- URL structure: `/incentive/:id` and `/company/:id`
- Maintain chat history while navigating
- Back button returns to previous view

## Future Enhancements

1. **Incentive Vector Embeddings**: Create embeddings for incentives to enable multi-result queries
2. **Multi-result Display**: Show top 3-5 results for general queries like "show me tech incentives"
3. **Query Expansion**: Use LLM to expand vague queries
4. **Multi-language Support**: Portuguese + English
5. **Export Results**: PDF/CSV download
6. **Advanced Filters**: Sector, region, score range
7. **Query History**: Save and revisit past queries
8. **Comparison Mode**: Compare multiple incentives side-by-side
9. **Real-time Updates**: WebSocket for live data
10. **Analytics Dashboard**: Query trends and popular searches
11. **Incremental Index Updates**: Update reverse index when new incentives are processed
12. **Rate Limiting**: Add when scaling to production
