# Semantic Matching for Government Incentives

## How to Run

```bash
# Setup (first time only - takes 30-60 minutes)
python scripts/setup_postgres.py
python scripts/setup_companies.py
python scripts/fill_llm_fields.py
python scripts/embed_companies_qdrant.py --full
python scripts/setup_enhanced_system.py

# Test with 5 incentives (~5-10 minutes)
python scripts/batch_process_with_scoring.py --limit 5

# View results
python tests/verify_scoring.py

# Process all incentives
python scripts/batch_process_with_scoring.py
```

That's it. The first five commands set up the system. The sixth processes incentives. The seventh shows results.

## What This Does

Given a government incentive program, find companies that should apply for it.

The naive approach is keyword matching. If an incentive mentions "software" and a company has "software" in its description, they match. This fails. A company doing "enterprise resource planning systems" should match an incentive for "digital transformation" even though they share no words.

You need semantic matching - matching by meaning. But semantic similarity alone isn't enough. A company might be semantically perfect but in the wrong region. Or be too small for the incentive. Or lack digital presence.

This system does five things:

1. **Semantic search** - Find relevant companies using embeddings (250K companies in <1 second)
2. **Geographic filtering** - Keep only companies in the right region (GPT-5-mini understands Portuguese geography)
3. **Semantic scoring** - Rank by relevance using a cross-encoder (BGE reranker)
4. **Company scoring** - Rank by comprehensive fit using a weighted formula (GPT-5-mini)
5. **Save both rankings** - Compare semantic vs comprehensive scoring

The interesting part is step 4. We compute a company score using five factors:

```
SCORE = 0.50×Semantic + 0.20×Sector + 0.10×Geography + 0.15×Organization + 0.05×Website
```

Semantic similarity gets 50% weight because it's the core signal. Sector alignment gets 20% because industry matters. Geography gets 10% because it's already filtered (binary). Organization type gets 15% because some incentives want large companies, others want startups. Website presence gets 5% as a proxy for digital maturity.

The formula is applied by GPT-5-mini. This seems odd - why use an LLM for arithmetic? Because the organization factor requires conditional logic. Some incentives prefer large companies (O′ = O). Others prefer small companies (O′ = 1-O). Others prefer nonprofits (O′ = 1 if nonprofit, else 0.5). The LLM handles this cleanly.

## Why Two Rankings

We save two rankings per incentive:

1. **Semantic ranking** - Pure relevance (what they do)
2. **Company score ranking** - Comprehensive fit (what + where + who + digital)

This is an experiment. Which ranking produces better matches? We don't know yet. That's why we save both. After processing all incentives, we can compare them and see which works better.

The semantic ranking is fast and simple. The company score ranking is slower but more nuanced. Maybe semantic is good enough. Maybe the extra factors matter. We'll find out.

## How It Works

### Embeddings

250K Portuguese companies are converted to 384-dimensional vectors. Each company is represented by combining three fields: name, CAE classification, and business activities. These go into a multilingual sentence transformer.

The vectors are stored in Qdrant. Searching 250K vectors takes under a second.

The key decision is what to embed. We embed name + classification + activities because that captures what a company does. Name alone isn't enough. Activities alone are too noisy. The combination works.

### Query Generation

Incentives are converted to queries using three fields: sector, AI-generated description, and eligible actions.

The AI description is key. It's a processed summary of the incentive that captures goals and context, not just keywords. This came from research on semantic matching for government funding (2014-2023). Full descriptions outperform keywords.

The query format mirrors the company format. Both sides have similar information density. This symmetric approach is backed by research.

### Two-Stage Retrieval

First stage: fast approximate search using Qdrant. Convert the query to a vector and find the 20-30 nearest company vectors. This is fast but approximate.

Second stage: precise reranking using BGE reranker v2-m3. This is a 568M parameter cross-encoder that sees query and document together. It's slow but accurate. We only run it on 20-30 items.

This two-stage architecture is standard in modern search. You see it in Google, in recommendation systems, in RAG applications. The reason is fundamental: you can't run expensive models on millions of items, but you can't get good results with cheap models either.

### Geographic Filtering

After semantic search, we enrich companies with locations using Google Maps Places API. Then GPT-5-mini determines geographic eligibility.

The LLM understands Portuguese administrative divisions. It knows that Grândola is in Alentejo. That Lisboa is both a city and a NUTS II region. That "Nacional" means anywhere in Portugal.

This filtering is 100% accurate in testing. The LLM gets Portuguese geography right.

### Company Scoring

After geographic filtering, we have 5-10 eligible companies. We score them using the weighted formula.

The components are computed in Python:
- S: Normalized semantic scores from reranker
- M: Jaccard similarity between incentive and company keywords
- G: Geographic fit (1 if eligible, 0.5 if unknown, 0 if outside)
- O: Organizational capacity from legal form (S.A. = 1.0, Unipessoal = 0.4, etc.)
- W: Website presence (1 if has website, 0 if not)

Then GPT-5-mini applies the formula with conditional logic for O′. The result is a single score from 0 to 1.

## Results

For a cultural inclusion incentive, the top semantic match scored 0.88. The top company score was 0.79. Both found the same company: a nonprofit focused on "promoting culture and social solidarity."

For a railway transport incentive, semantic found a railway equipment manufacturer (0.10 semantic score). Company score ranked it lower because it lacked a website and had lower organizational capacity.

The rankings are similar but not identical. Company score adds nuance. A company might have high semantic similarity but low organizational capacity. Or high semantic similarity but no website. The score components show why matches are good or bad.

## The Experiment

We're running an experiment. We process all incentives and save both rankings. Then we compare them.

Questions we want to answer:
- Do the rankings differ significantly?
- Which ranking produces better matches?
- Do the extra factors (geography, organization, website) matter?
- Is semantic similarity good enough?

We don't know the answers yet. That's why it's an experiment. After processing all incentives, we'll analyze the results and see what we learn.

## Architecture

The system has five main components:

**DatabaseManager** - Handles PostgreSQL operations. Saves locations, saves results, manages schema.

**LocationService** - Manages Google Maps API. Caches locations in database. Handles rate limits and errors.

**GeographicAnalyzer** - Uses GPT-5-mini to determine geographic eligibility. Understands Portuguese geography.

**CompanyScorer** - Computes company scores using the weighted formula. Calls GPT-5-mini for final calculation.

**EnhancedMatchingPipeline** - Orchestrates everything. Manages the iterative search (10→20→30 candidates if needed). Coordinates all services.

The code is simple. The models are complex. This is how it should be.

## Data Flow

```
Incentive
  ↓
Query (sector + ai_description + eligible_actions)
  ↓
Vector Search (250K companies → top 10-30)
  ↓
Location Enrichment (Google Maps API)
  ↓
Geographic Filtering (GPT-5-mini → 5-10 eligible)
  ↓
Semantic Scoring (BGE reranker → semantic ranking)
  ↓
Company Scoring (GPT-5-mini + formula → company ranking)
  ↓
Save Both Rankings
```

Processing takes 60-120 seconds per incentive. Most time is spent on API calls (Google Maps, GPT-5-mini) and reranking.

## Cost

Processing 100 incentives costs $2-10.

Google Maps API is $17 per 1,000 requests. But caching reduces this by 90%. First run is expensive (no cache). Subsequent runs are cheap.

GPT-5-mini is cheap - about $0.01-0.02 per incentive.

The real cost is time. 60-120 seconds per incentive means 2-3 hours for 100 incentives. This is fine for batch processing but too slow for real-time.

## Project Structure

```
incentive-matching/
├── enhanced_incentive_matching.py    # Core engine
├── scripts/                          # Setup & processing
├── tests/                            # Test scripts
├── data/                             # Data files
└── qdrant_storage/                   # Vector database
```

See `PROJECT_STRUCTURE.md` for details.

## What We Learned

The query generation is simpler than expected. Just concatenating fields works. We tried using GPT to generate better queries. It made things worse. The LLM tried to be clever - expanding terms, adding synonyms. But the embedding model doesn't need this. It already understands semantic relationships.

The two-stage retrieval is essential. Fast search gets you candidates. Precise reranking picks the best. You need both.

Geographic filtering is surprisingly accurate. GPT-5-mini understands Portuguese geography better than we expected. 100% accuracy in testing.

The company scoring adds nuance but we don't know if it matters yet. That's the experiment. We'll find out after processing all incentives.

## Running It

See `GETTING_STARTED.md` for complete setup instructions.

See `EQUATION.md` for scoring formula details.

See `PROJECT_STRUCTURE.md` for file organization.

The system is production-ready. It has error handling, timeout protection, resume capability, and comprehensive logging. It's been tested on real data and produces good results.

The code is simple. The models are complex. The experiment is interesting.
