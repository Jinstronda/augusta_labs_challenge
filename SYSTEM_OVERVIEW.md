# Incentive-Company Matching System

## Overview
This system matches Portuguese government incentives with eligible companies using semantic search and AI reranking.

## How It Works

### 1. Data Sources
- **PostgreSQL Database**: Contains 250,000 companies and incentive programs
- **Qdrant Vector Database**: Stores company embeddings for fast semantic search

### 2. Company Embeddings
Companies are embedded using a multilingual model that combines:
- Company name
- CAE classification (industry category in English)
- Business activities (in Portuguese)

### 3. Matching Pipeline

```
Incentive → Search Query → Vector Search → Reranking → Top 5 Matches
```

**Step 1: Query Generation**
- Combines incentive sector + eligible actions
- Example: "Transportes Ferroviários / Serviço Público Aquisição de automotoras..."

**Step 2: Vector Search (Qdrant)**
- Searches 250,000 company embeddings
- Uses Reciprocal Rank Fusion (RRF) for scoring
- Returns top 20 candidates

**Step 3: Reranking (BGE Reranker v2-m3)**
- Deep semantic analysis of query-company pairs
- Scores each candidate (0-1 scale)
- Returns top 5 best matches

### 4. Results
Each match includes:
- Company name
- Rerank score (confidence)
- CAE classification
- Business activities
- Website

## Example Results

**Incentive**: Railway Transport / Public Service - Acquisition of rolling stock
**Top Match**: TRAVIAMA - Urban and suburban passenger land transport (Score: 0.9021)

## Performance

- **Search Speed**: ~2-3 seconds for 250,000 companies
- **Accuracy**: High-quality matches with scores >0.8
- **Multilingual**: Handles Portuguese and English seamlessly

## Technology Stack

- **Embeddings**: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **Vector DB**: Qdrant (local storage)
- **Reranker**: FlagEmbedding BGE Reranker v2-m3
- **Database**: PostgreSQL
- **GPU**: CUDA-accelerated (falls back to CPU)

## Files

- `embed_companies_qdrant.py` - Creates company embeddings
- `test_incentive_matching.py` - Tests matching pipeline
- `requirements.txt` - Python dependencies
- `config.env` - Database configuration

## Usage

```bash
# 1. Embed companies (test mode - 2 companies)
python embed_companies_qdrant.py

# 2. Embed all companies
python embed_companies_qdrant.py --full

# 3. Test matching
python test_incentive_matching.py
```

## Key Features

✅ Semantic search (not keyword matching)
✅ Multilingual support (Portuguese + English)
✅ GPU acceleration
✅ State-of-the-art reranking
✅ Handles 250K+ companies efficiently
✅ High-quality matches (0.8+ scores)
