# UI Architecture

## Overview

The Incentive Query UI is a full-stack web application built on top of the existing incentive-company matching system. It provides a ChatGPT-like interface for querying incentives and companies using natural language.

**Key Principle**: The UI is a **thin layer** on top of the existing system. It does not modify the core matching logic, database schema, or scoring algorithms. It only adds a query interface and API endpoints.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  React Frontend (Vite + TypeScript + TailwindCSS)          │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │ ChatInterface│  │ QueryInput   │  │ ResultsDisplay│   │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  │                                                             │ │
│  │  ┌──────────────┐  ┌──────────────┐                       │ │
│  │  │IncentiveCard │  │ CompanyCard  │                       │ │
│  │  └──────────────┘  └──────────────┘                       │ │
│  │                                                             │ │
│  │  Port: 5173 (dev) / 80 (prod)                              │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST (axios)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         BACKEND API                              │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  FastAPI Server (Python)                                   │ │
│  │                                                             │ │
│  │  Endpoints:                                                 │ │
│  │  • POST /api/query          - Natural language query       │ │
│  │  • GET  /api/incentive/:id  - Incentive detail             │ │
│  │  • GET  /api/company/:id    - Company detail               │ │
│  │  • GET  /health             - Health check                 │ │
│  │                                                             │ │
│  │  Services:                                                  │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │  Classifier  │  │    Search    │  │   Database   │    │ │
│  │  │  (GPT-4-mini)│  │  (Semantic)  │  │   Service    │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  │                                                             │ │
│  │  Port: 8000                                                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SQL / Vector Search
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXISTING DATA LAYER                           │
│                                                                   │
│  ┌──────────────────────────┐  ┌──────────────────────────┐    │
│  │  PostgreSQL Database     │  │  Qdrant Vector DB        │    │
│  │                          │  │                          │    │
│  │  Tables:                 │  │  Collection: companies   │    │
│  │  • incentives            │  │  • 250K embeddings       │    │
│  │    - top_5_companies     │  │  • Semantic search       │    │
│  │    - top_5_companies_    │  │                          │    │
│  │      scored              │  │  Port: N/A (local)       │    │
│  │  • companies             │  │  Path: ./qdrant_storage  │    │
│  │    - eligible_incentives │  │                          │    │
│  │                          │  │                          │    │
│  │  Port: 5432              │  │                          │    │
│  └──────────────────────────┘  └──────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Pre-computed by existing system
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  EXISTING MATCHING SYSTEM                        │
│                                                                   │
│  Scripts:                                                         │
│  • batch_process_with_scoring.py  - Process incentives          │
│  • build_company_incentive_index.py - Build reverse index       │
│  • embed_companies_qdrant.py - Create embeddings                │
│                                                                   │
│  Core Engine:                                                     │
│  • enhanced_incentive_matching.py - Matching logic              │
│                                                                   │
│  ⚠️ UI DOES NOT MODIFY THIS LAYER ⚠️                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Breakdown

### Frontend Layer

#### 1. ChatInterface Component
- **Purpose**: Main chat UI container
- **Responsibilities**:
  - Manage chat message history
  - Render user queries and assistant responses
  - Auto-scroll to latest message
  - Provide "New Chat" button
- **State**: Chat messages array
- **Dependencies**: QueryInput, ResultsDisplay

#### 2. QueryInput Component
- **Purpose**: Text input for natural language queries
- **Responsibilities**:
  - Accept user input (1-500 characters)
  - Submit on Enter (Shift+Enter for new line)
  - Show loading state during API call
  - Validate input
- **State**: Query text, loading state
- **Dependencies**: API service

#### 3. ResultsDisplay Component
- **Purpose**: Route and display query results
- **Responsibilities**:
  - Determine result type (INCENTIVE vs COMPANY)
  - Render appropriate card component
  - Handle loading and error states
- **State**: Query results, loading, error
- **Dependencies**: IncentiveCard, CompanyCard

#### 4. IncentiveCard Component
- **Purpose**: Display incentive details with top companies
- **Responsibilities**:
  - Show incentive metadata
  - Render top 5 companies as clickable cards
  - Display scores with progress bars
  - Navigate to company detail on click
- **Props**: Incentive data
- **Dependencies**: React Router

#### 5. CompanyCard Component
- **Purpose**: Display company details with eligible incentives
- **Responsibilities**:
  - Show company metadata
  - Render eligible incentives as clickable cards
  - Display scores and rankings
  - Navigate to incentive detail on click
- **Props**: Company data
- **Dependencies**: React Router

---

### Backend Layer

#### 1. Query Classifier Service
- **Purpose**: Classify queries as INCENTIVE or COMPANY
- **Technology**: OpenAI GPT-4-mini
- **Input**: Natural language query
- **Output**: "INCENTIVE" or "COMPANY"
- **Fallback**: Keyword-based classification
- **Performance**: ~200-500ms per query

#### 2. Semantic Search Service
- **Purpose**: Find matching companies or incentives
- **Technology**:
  - Companies: Qdrant vector search (existing embeddings)
  - Incentives: PostgreSQL keyword search (small dataset)
- **Input**: Query text
- **Output**: Top matching entities
- **Performance**: <100ms for companies, <50ms for incentives

#### 3. Database Service
- **Purpose**: Retrieve entity details from PostgreSQL
- **Methods**:
  - `get_incentive_with_companies(id)` - Get incentive + top 5 companies
  - `get_company_with_incentives(id)` - Get company + eligible incentives
- **Data Source**: Pre-computed data from existing system
- **Performance**: 50-200ms per query

---

### Data Layer

#### PostgreSQL Database

**incentives table** (existing):
```sql
CREATE TABLE incentives (
  incentive_id VARCHAR PRIMARY KEY,
  title TEXT,
  ai_description TEXT,
  sector TEXT,
  geo_requirement TEXT,
  eligible_actions TEXT,
  funding_rate TEXT,
  investment_eur NUMERIC,
  top_5_companies JSONB,           -- Semantic ranking
  top_5_companies_scored JSONB     -- Multi-factor ranking
);
```

**companies table** (existing + new column):
```sql
CREATE TABLE companies (
  company_id INTEGER PRIMARY KEY,
  company_name TEXT,
  cae_primary_label TEXT,
  trade_description_native TEXT,
  website TEXT,
  location_address TEXT,
  location_lat NUMERIC,
  location_lon NUMERIC,
  eligible_incentives JSONB        -- NEW: Reverse index
);
```

**eligible_incentives structure**:
```json
[
  {
    "incentive_id": "2270",
    "title": "Apoio à Inovação Digital",
    "rank": 1,
    "company_score": 0.92
  }
]
```

#### Qdrant Vector Database

**companies collection** (existing):
- 250,000 company embeddings
- 384-dimensional vectors (paraphrase-multilingual-MiniLM-L12-v2)
- Payload: company_id, company_name, cae, activities
- Used for semantic company search

---

## Data Flow

### Incentive Query Flow

```
1. User types: "incentivos para tecnologia"
   ↓
2. Frontend sends POST /api/query
   ↓
3. Backend: QueryClassifier → "INCENTIVE"
   ↓
4. Backend: SemanticSearch.search_incentives()
   ↓
5. PostgreSQL: Keyword search on title/description
   ↓
6. Backend: DatabaseService.get_incentive_with_companies()
   ↓
7. PostgreSQL: Parse top_5_companies_scored JSON
   ↓
8. Backend: Return IncentiveResult
   ↓
9. Frontend: Display IncentiveCard with top 5 companies
   ↓
10. User clicks company → Navigate to /company/:id
```

### Company Query Flow

```
1. User types: "empresas de software"
   ↓
2. Frontend sends POST /api/query
   ↓
3. Backend: QueryClassifier → "COMPANY"
   ↓
4. Backend: SemanticSearch.search_companies()
   ↓
5. Qdrant: Vector search (cosine similarity)
   ↓
6. Backend: DatabaseService.get_company_with_incentives()
   ↓
7. PostgreSQL: Fetch company + eligible_incentives JSONB
   ↓
8. Backend: Return CompanyResult
   ↓
9. Frontend: Display CompanyCard with eligible incentives
   ↓
10. User clicks incentive → Navigate to /incentive/:id
```

---

## Integration with Existing System

### What the UI Uses (Read-Only)

1. **PostgreSQL Tables**:
   - `incentives.top_5_companies_scored` - Pre-computed by batch processing
   - `companies.eligible_incentives` - Pre-computed by reverse index script

2. **Qdrant Collection**:
   - `companies` - Pre-computed embeddings (250K vectors)

3. **Models**:
   - `paraphrase-multilingual-MiniLM-L12-v2` - For company search
   - `GPT-4-mini` - For query classification

### What the UI Does NOT Touch

1. **Core Matching Logic**:
   - `enhanced_incentive_matching.py` - Not used by UI
   - Scoring formula (EQUATION.md) - Not modified
   - Geographic filtering - Not re-implemented

2. **Batch Processing**:
   - `batch_process_with_scoring.py` - Runs independently
   - `build_company_incentive_index.py` - Runs independently

3. **Database Writes**:
   - UI only reads data, never writes
   - All data is pre-computed by existing scripts

### Reverse Index (New Addition)

The only new component added to the existing system:

**Script**: `scripts/build_company_incentive_index.py`

**Purpose**: Build reverse index (company → incentives)

**Algorithm**:
1. Iterate through all incentives
2. Extract companies from `top_5_companies_scored`
3. Aggregate incentives per company
4. Keep top 5 incentives per company (by score)
5. Save to `companies.eligible_incentives` JSONB column

**When to Run**: After batch processing completes

**Performance**: ~5-10 minutes for 362 incentives

---

## Performance Characteristics

### Frontend Performance

- **Initial Load**: <2 seconds (code splitting)
- **Query Submission**: 300-1000ms (includes backend processing)
- **Navigation**: <100ms (client-side routing)
- **Bundle Size**: ~200KB (minified + gzipped)

### Backend Performance

- **Model Loading**: 5-10 seconds (at startup, singleton)
- **Query Classification**: 200-500ms (GPT-4-mini API)
- **Company Search**: 50-100ms (Qdrant vector search)
- **Incentive Search**: 20-50ms (PostgreSQL keyword search)
- **Database Lookup**: 50-200ms (JSON parsing)

### Optimization Strategies

1. **Singleton Model Loading**: Load once at startup, not per request
2. **Connection Pooling**: Reuse database connections
3. **Code Splitting**: Lazy load React components
4. **Memoization**: Cache expensive component renders
5. **Debouncing**: Limit API calls during typing

---

## Deployment Architecture

### Development Setup

```
Terminal 1: Backend
cd backend
conda activate turing0.1
uvicorn app.main:app --reload --port 8000

Terminal 2: Frontend
cd frontend
npm run dev
# Runs on http://localhost:5173

Terminal 3: Database
# PostgreSQL already running
# Qdrant embedded (./qdrant_storage)
```

### Production Setup (Option 1: Single Server)

```
Docker Compose:
- Backend container (FastAPI)
- Frontend container (Nginx serving static files)
- PostgreSQL container
- Qdrant container

All on one server, internal networking
```

### Production Setup (Option 2: Separate Hosting)

```
Frontend: Vercel/Netlify
- Static build (npm run build)
- CDN distribution
- Environment variable: VITE_API_URL

Backend: Railway/Render/Fly.io
- Docker container
- Environment variables for DB/API keys
- Auto-scaling

Database: Existing PostgreSQL instance
Qdrant: Embedded or separate server
```

---

## Security Considerations

### Frontend
- Input validation (1-500 characters)
- XSS prevention (React escapes by default)
- HTTPS in production
- Environment variables for API URL

### Backend
- CORS configuration (restrict origins)
- Input validation (Pydantic models)
- SQL injection prevention (parameterized queries)
- Rate limiting (recommended for production)
- API key authentication (recommended for production)

### Database
- Read-only access for UI
- Connection pooling with limits
- Prepared statements
- No direct database access from frontend

---

## Monitoring and Observability

### Health Checks
- `/health` endpoint for uptime monitoring
- Database connection status
- Model loading status

### Logging
- Request/response logging
- Error logging with stack traces
- Performance metrics (response times)
- Query classification results

### Metrics to Track
- Query response time (p50, p95, p99)
- Classification accuracy
- Search result quality
- Error rate
- Cache hit rate (future)

---

## Scalability

### Current Capacity
- **Concurrent Users**: 10-50 (single server)
- **Queries per Second**: 5-10
- **Database Size**: 250K companies, 362 incentives

### Scaling Strategies

**Horizontal Scaling**:
- Add more backend instances (stateless)
- Load balancer in front
- Shared PostgreSQL + Qdrant

**Vertical Scaling**:
- Larger server for Qdrant (more RAM)
- GPU for faster embeddings (if needed)

**Caching**:
- Redis for query results
- CDN for frontend assets
- Database query caching

**Database Optimization**:
- Indexes on frequently queried columns
- Materialized views for complex queries
- Read replicas for scaling reads

---

## Future Enhancements

1. **Multi-Result Queries**: Show top 3-5 incentives instead of just 1
2. **Incentive Embeddings**: Create embeddings for better incentive search
3. **Query History**: Save and revisit past queries
4. **Filters**: Add sector, region, score filters
5. **Comparison Mode**: Compare multiple incentives side-by-side
6. **Real-time Updates**: WebSocket for live data
7. **Analytics Dashboard**: Query trends and popular searches
8. **Multi-language**: Portuguese + English support
9. **Export**: PDF/CSV download of results
10. **Rate Limiting**: Protect against abuse

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend Framework | React 18 | UI components |
| Build Tool | Vite | Fast dev server + build |
| Styling | TailwindCSS | Utility-first CSS |
| Type Safety | TypeScript | Static typing |
| Routing | React Router | Client-side navigation |
| HTTP Client | Axios | API requests |
| Backend Framework | FastAPI | REST API |
| Language | Python 3.11+ | Backend logic |
| Database | PostgreSQL | Structured data |
| Vector DB | Qdrant | Semantic search |
| LLM | GPT-4-mini | Query classification |
| Embeddings | Sentence Transformers | Company embeddings |
| Deployment | Docker | Containerization |

---

## File Structure

```
incentive-matching/
├── frontend/                    # NEW: React frontend
│   ├── src/
│   │   ├── components/         # UI components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API client
│   │   ├── types/              # TypeScript types
│   │   └── utils/              # Utilities
│   ├── package.json
│   └── vite.config.ts
│
├── backend/                     # NEW: FastAPI backend
│   ├── app/
│   │   ├── api/                # API routes
│   │   ├── services/           # Business logic
│   │   ├── models.py           # Pydantic models
│   │   ├── config.py           # Configuration
│   │   └── main.py             # App entry point
│   ├── tests/                  # Backend tests
│   ├── requirements.txt
│   └── Dockerfile
│
├── scripts/                     # EXISTING: Setup scripts
│   ├── build_company_incentive_index.py  # NEW: Reverse index
│   └── ...                     # Other existing scripts
│
├── enhanced_incentive_matching.py  # EXISTING: Core engine
├── data/                        # EXISTING: Data files
├── qdrant_storage/              # EXISTING: Vector DB
└── docs/                        # EXISTING + NEW: Documentation
    ├── API_DOCUMENTATION.md     # NEW
    ├── UI_ARCHITECTURE.md       # NEW (this file)
    ├── ENVIRONMENT_VARIABLES.md # NEW
    └── TROUBLESHOOTING_UI.md    # NEW
```

---

## Summary

The UI layer is a **thin, read-only interface** on top of the existing incentive-company matching system. It:

1. **Does not modify** the core matching logic or scoring algorithms
2. **Only reads** pre-computed data from the database
3. **Adds** a natural language query interface
4. **Provides** a ChatGPT-like user experience
5. **Integrates** seamlessly with the existing system

The architecture is designed to be:
- **Simple**: Minimal components, clear responsibilities
- **Fast**: Optimized for performance (singleton models, connection pooling)
- **Scalable**: Stateless backend, horizontal scaling ready
- **Maintainable**: Clean separation of concerns, well-documented

For more details, see:
- API Documentation: `docs/API_DOCUMENTATION.md`
- Environment Variables: `docs/ENVIRONMENT_VARIABLES.md`
- Troubleshooting: `docs/TROUBLESHOOTING_UI.md`
