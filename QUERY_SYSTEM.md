# Query System Architecture

## Overview

The system uses GPT-5-mini to classify user queries into 4 distinct types, then routes them to appropriate handlers for optimal results.

## Query Classification (4 Types)

### 1. SPECIFIC_COMPANY
**User Intent**: Ask for a specific company by name

**Examples**:
- "Show me Microsoft"
- "Find Galp Energia"
- "Information about Tesla"

**System Behavior**:
- Searches RAG (Qdrant) for the best matching company (limit=1)
- Returns ONE company with its top 5 eligible incentives
- Incentives come from the pre-computed `eligible_incentives` JSONB column

**Response**: Single CompanyResult with full details + top 5 incentives

---

### 2. COMPANY_GROUP
**User Intent**: Ask for companies in a market/sector/category

**Examples**:
- "Companies in renewable energy"
- "Tech startups in Lisbon"
- "Manufacturing companies"

**System Behavior**:
- Searches RAG (Qdrant) for top 5 matching companies
- Returns simplified company details (no full incentive lists for performance)
- Shows incentive count only

**Response**: List of 5 CompanyResult with basic info

---

### 3. SPECIFIC_INCENTIVE
**User Intent**: Ask for a specific incentive by name or ID

**Examples**:
- "Show me Digital Innovation Fund"
- "Incentive 1288"
- "PRR funding details"

**System Behavior**:
- Searches PostgreSQL for the best matching incentive (limit=1)
- Returns ONE incentive with its top 5 matched companies
- Companies come from the pre-computed `top_5_companies_scored` JSONB column

**Response**: Single IncentiveResult with full details + top 5 companies with scores

---

### 4. INCENTIVE_GROUP
**User Intent**: Ask for a group/category of incentives

**Examples**:
- "Green energy incentives"
- "R&D funding programs"
- "Startup grants"

**System Behavior**:
- Searches PostgreSQL for top 5 matching incentives
- Returns multiple incentives with their matched companies
- Full details for each incentive

**Response**: List of 5 IncentiveResult with matched companies

---

## Technical Implementation

### Classification Flow

```
User Query
    ↓
GPT-5-mini Classifier (with strict JSON prompting)
    ↓
One of 4 query types
    ↓
Route to appropriate handler
    ↓
Return formatted results
```

### GPT-5-mini Prompt

The classifier uses a clear, structured prompt:

```
Classify this query into ONE of these 4 types:

1. SPECIFIC_COMPANY - User asks for a specific company by name
2. COMPANY_GROUP - User asks for companies in a market/sector/category
3. SPECIFIC_INCENTIVE - User asks for a specific incentive by name or ID
4. INCENTIVE_GROUP - User asks for a group/category of incentives

Query: "{user_query}"

Return JSON only: {"type": "SPECIFIC_COMPANY"} or {"type": "COMPANY_GROUP"} 
                  or {"type": "SPECIFIC_INCENTIVE"} or {"type": "INCENTIVE_GROUP"}
```

### Fallback Classification

If GPT-5-mini fails, the system uses keyword-based classification:
- Detects specific company indicators (LDA, SA, proper names)
- Counts incentive vs company keywords
- Detects group indicators (plural forms, sector words)
- Makes best guess based on patterns

### Data Sources

1. **Company Search**: Qdrant vector DB (250K companies)
   - Uses `paraphrase-multilingual-MiniLM-L12-v2` embeddings
   - Semantic similarity search
   - Fast and accurate

2. **Incentive Search**: PostgreSQL keyword search (~338 incentives)
   - ILIKE pattern matching on title, description, sector, actions
   - Relevance scoring based on field matches
   - Simple but effective for small dataset

3. **Pre-computed Mappings**:
   - `incentives.top_5_companies_scored` - Top 5 companies per incentive
   - `companies.eligible_incentives` - Top 5 incentives per company
   - Built by `scripts/build_company_incentive_index.py`

### API Endpoints

```
POST /api/query
- Main query endpoint
- Accepts: {"query": "user query string"}
- Returns: QueryResponse with results based on classification

GET /api/incentive/:id
- Get specific incentive details
- Returns: IncentiveResult with matched companies

GET /api/company/:id
- Get specific company details
- Returns: CompanyResult with eligible incentives
```

### Performance Optimizations

1. **Singleton Models**: Embedding model and Qdrant client loaded once at startup
2. **Connection Pooling**: PostgreSQL connection pool (1-10 connections)
3. **Simplified Queries**: COMPANY_GROUP returns basic info without full incentive lists
4. **Pre-computed Mappings**: No need to scan all data for detail views
5. **Limit Results**: Always limit to top 5 for fast response times

## Frontend Integration

The frontend (ChatGPT-like interface) handles all 4 query types:

- **SPECIFIC_COMPANY**: Shows single company card with "Click to see incentives"
- **COMPANY_GROUP**: Shows 5 company cards in a grid
- **SPECIFIC_INCENTIVE**: Shows single incentive card with matched companies
- **INCENTIVE_GROUP**: Shows 5 incentive cards in a grid

All cards are clickable and navigate to detail pages.

## Future Enhancements

### Incentive Vector Search (TODO)

Currently incentive search uses keyword matching. To improve:

1. Create incentive embeddings using the same model
2. Store in new Qdrant collection `incentives`
3. Update search service to use vector search
4. Enable better semantic matching for INCENTIVE_GROUP queries

**Script to create**: `scripts/create_incentive_embeddings.py`

### Benefits:
- Better semantic understanding
- Multi-language support
- Fuzzy matching
- Relevance ranking

## Testing

Test all 4 query types:

```bash
# Start backend
cd backend
conda activate turing0.1
uvicorn app.main:app --reload

# Start frontend
cd frontend
npm run dev

# Test queries:
1. "Show me Galp Energia" → SPECIFIC_COMPANY
2. "Tech companies in Lisbon" → COMPANY_GROUP
3. "Digital Innovation Fund" → SPECIFIC_INCENTIVE
4. "Green energy incentives" → INCENTIVE_GROUP
```

## Monitoring

Check logs for classification results:

```
[INFO] Classifying query: Show me Galp Energia
[INFO] GPT classification: SPECIFIC_COMPANY
[INFO] Handling SPECIFIC_COMPANY query
[INFO] Found 1 companies
[INFO] Fetched company 12345 with 5 incentives
[INFO] Query completed in 0.45s with 1 results
```

## Error Handling

- GPT-5-mini failure → Fallback to keyword classification
- No results found → Return empty array with helpful message
- Database errors → HTTP 500 with error details
- Timeout (30s) → Abort request with timeout message
