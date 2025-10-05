"""
Incentive-Company Matching System

This script demonstrates semantic matching between government incentives and companies.
The core insight is that matching should be based on what companies do, not just
keywords in their names. A company that "develops software for logistics optimization"
should match an incentive for "digital transformation in supply chain management"
even if they share no exact words.

The system uses a two-stage retrieval approach:
    1. Fast vector search (Qdrant) to find 20 candidates from 250K companies
    2. Precise reranking (BGE) to select the best 5 matches

This architecture balances speed and accuracy. Vector search is fast but approximate.
Reranking is slow but precise. Together they find the right companies efficiently.

Architecture:
    Incentive -> Query -> Vector Search (20) -> Reranking (5) -> Results
"""
import os
import psycopg2
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagReranker

import torch

# Load environment variables
load_dotenv('config.env')

# Database configuration
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")



# Setup device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[GPU] Using device: {device}")


def get_random_incentive():
    """
    Select a random incentive from the database for testing.
    
    Only selects incentives with both sector and eligible_actions populated,
    as these fields are essential for creating meaningful search queries.
    
    Returns:
        dict: Incentive data including id, title, sector, requirements, etc.
        None: If no suitable incentives found
    """
    print("\n[DB] Fetching random incentive...")
    
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT incentive_id, title, sector, geo_requirement, 
               eligible_actions, funding_rate, investment_eur
        FROM incentives
        WHERE sector IS NOT NULL AND eligible_actions IS NOT NULL
        ORDER BY RANDOM() LIMIT 1
    """)
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not result:
        print("[ERROR] No processed incentives found!")
        return None
    
    incentive = {
        'id': result[0], 'title': result[1], 'sector': result[2],
        'geo_requirement': result[3], 'eligible_actions': result[4],
        'funding_rate': result[5], 'investment_eur': result[6]
    }

    print(f"\n[OK] SELECTED INCENTIVE:")
    print(f"=" * 80)
    print(f"ID: {incentive['id']}")
    print(f"Title: {incentive['title']}")
    print(f"Sector: {incentive['sector']}")
    print(f"Geographic Requirement: {incentive['geo_requirement']}")
    print(f"Eligible Actions: {incentive['eligible_actions']}")
    print(f"Funding Rate: {incentive['funding_rate']}")
    print(f"Investment EUR: {incentive['investment_eur']}")
    print(f"=" * 80)
    return incentive


def create_search_query(incentive):
    """
    Generate search query from incentive data.
    
    Combines sector and eligible actions into a single query. This simple
    approach works surprisingly well - better than complex LLM-generated queries.
    The key is that sector + actions already describes what kind of company
    would be eligible.
    
    Example: "Transportes Ferroviários / Serviço Público Aquisição de automotoras..."
    This naturally matches companies in railway transport.
    
    Args:
        incentive: Dict with sector and eligible_actions fields
    
    Returns:
        list: Single-element list containing the query string
    """
    print("\n[QUERY] Generating search query...")
    
    # Combine sector and eligible actions for comprehensive search
    query = f"{incentive['sector']} {incentive['eligible_actions']}"
    
    print(f"\n[SEARCH QUERY]")
    print(f"=" * 80)
    print(f"{query}")
    print(f"=" * 80)
    
    return [query]

def load_embedding_model():
    """
    Load the same embedding model used to create company vectors.
    
    Must be the same model as embed_companies_qdrant.py, otherwise the
    query vectors won't be comparable to company vectors. This is a common
    mistake in vector search systems.
    
    Returns:
        SentenceTransformer: Model for encoding queries
    """
    print("\n[MODEL] Loading embedding model...")
    try:
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)
        print("[OK] Multilingual model loaded")
        return model
    except:
        model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
        print("[OK] Fallback model loaded")
        return model


def load_reranker():
    """
    Load the BGE reranker model for precise scoring.
    
    BGE (BAAI General Embedding) reranker is a cross-encoder that scores
    query-document pairs. Unlike bi-encoders (sentence transformers), it
    sees both texts together and can capture subtle semantic relationships.
    
    This is slower than vector search but much more accurate. That's why
    we use it only on the top 20 candidates, not all 250K companies.
    
    Returns:
        FlagReranker: Reranker model, or None if loading fails
    """
    print("\n[RERANKER] Loading BGE Reranker v2-m3...")
    try:
        reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
        print("[OK] BGE Reranker v2-m3 loaded successfully")
        return reranker
    except Exception as e:
        print(f"[ERROR] Failed to load reranker: {e}")
        return None


def search_companies_qdrant(queries, model, top_k=20):
    """
    Search for companies using vector similarity.
    
    Converts the query to a vector and finds companies with similar vectors.
    Uses Reciprocal Rank Fusion (RRF) to combine results if multiple queries
    are provided, though currently we only use one query.
    
    RRF formula: score = 1 / (rank + 60)
    This gives higher scores to top-ranked results while still considering
    lower ranks. The constant 60 prevents the top result from dominating.
    
    Args:
        queries: List of query strings (usually just one)
        model: Sentence transformer for encoding queries
        top_k: Number of candidates to return
    
    Returns:
        list: Top companies with their RRF scores
    """
    print(f"\n[QDRANT] Searching for top {top_k} companies...")

    client = QdrantClient(path="./qdrant_storage")
    collection_name = "companies"

    try:
        collection_info = client.get_collection(collection_name)
        print(f"[OK] Connected: {collection_info.points_count:,} companies")
    except Exception as e:
        print(f"[ERROR] Qdrant collection not found: {e}")
        return []

    all_results = {}

    for idx, query in enumerate(queries, 1):
        print(f"\n[SEARCHING DATABASE]")
        print(f"Query: {query}")
        print(f"Searching through {collection_info.points_count:,} company embeddings...")

        query_vector = model.encode(query).tolist()

        results = client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=top_k * 2
        ).points

        for rank, result in enumerate(results, 1):
            company_id = result.id
            rrf_score = 1.0 / (rank + 60)

            if company_id in all_results:
                all_results[company_id]['score'] += rrf_score
                all_results[company_id]['queries_matched'] += 1
            else:
                all_results[company_id] = {
                    'id': company_id, 'score': rrf_score,
                    'queries_matched': 1, 'payload': result.payload
                }

    ranked = sorted(
        all_results.values(),
        key=lambda x: (x['queries_matched'], x['score']),
        reverse=True
    )[:top_k]

    print(f"[OK] Found {len(ranked)} companies using RRF")
    return ranked


def enrich_with_postgres(company_ids):
    """
    Fetch complete company data from PostgreSQL.
    
    Qdrant stores only essential fields in the payload. For full details
    (especially long activity descriptions), we query PostgreSQL using the
    company IDs from vector search.
    
    This hybrid approach keeps Qdrant fast while preserving all data in
    the source database.
    
    Args:
        company_ids: List of company IDs to fetch
    
    Returns:
        dict: Company ID -> company data mapping
    """
    print(f"\n[DB] Enriching {len(company_ids)} companies...")

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT company_id, company_name, cae_primary_label,
               trade_description_native, website
        FROM companies WHERE company_id = ANY(%s)
    """, (company_ids,))

    companies = {}
    for row in cursor.fetchall():
        companies[row[0]] = {
            'id': row[0], 'name': row[1], 'cae': row[2],
            'activities': row[3], 'website': row[4]
        }

    cursor.close()
    conn.close()

    print(f"[OK] Enriched {len(companies)} companies")
    return companies


def rerank_companies(query, companies, reranker, top_k=5):
    """
    Rerank candidates using precise semantic scoring.
    
    Vector search is fast but approximate - it might rank a company 5th that
    should be 1st. The reranker fixes this by doing deep semantic analysis
    of each query-company pair.
    
    For each company, we create a text combining name, CAE, and activities.
    The reranker scores how well this matches the query. Scores are normalized
    to 0-1 range, where >0.8 indicates strong match.
    
    Args:
        query: Search query string
        companies: List of candidate companies
        reranker: BGE reranker model
        top_k: Number of final results to return
    
    Returns:
        list: Top companies sorted by rerank score
    """
    print(f"\n[RERANKING] Using BGE Reranker v2-m3 to select top {top_k} companies...")

    if not reranker:
        print("[WARNING] Reranker not available, returning original order")
        return companies[:top_k]

    # Prepare query-document pairs for reranking
    pairs = []
    for company in companies:
        # Create comprehensive company text for reranking
        company_text = f"{company['name']} {company['cae'] or ''} {company['activities'] or ''}"
        pairs.append([query, company_text])

    # Get reranking scores
    print(f"[RERANKING] Computing scores for {len(pairs)} companies...")
    scores = reranker.compute_score(pairs, normalize=True)

    # Add scores to companies and sort
    for i, company in enumerate(companies):
        company['rerank_score'] = scores[i] if isinstance(scores, list) else scores

    # Sort by rerank score and get top_k
    reranked = sorted(companies, key=lambda x: x['rerank_score'], reverse=True)[:top_k]

    print(f"[OK] Reranking complete! Top {len(reranked)} companies selected")
    for i, company in enumerate(reranked, 1):
        print(f"  {i}. {company['name']}: {company['rerank_score']:.4f}")

    return reranked


def display_results(incentive, results):
    """
    Print final matching results in readable format.
    
    Shows company name, rerank score, CAE classification, activities, and website.
    The rerank score indicates match quality: >0.8 is excellent, >0.5 is good,
    <0.3 suggests weak match.
    
    Args:
        incentive: The incentive being matched (for context)
        results: List of matched companies with scores
    """
    print("\n" + "=" * 80)
    print(f"FINAL RESULTS: TOP {len(results)} COMPANIES")
    print("=" * 80)

    for idx, result in enumerate(results, 1):
        print(f"\n{'='*80}")
        print(f"COMPANY #{idx}")
        print(f"{'='*80}")
        print(f"Name: {result['name']}")
        print(f"Rerank Score: {result['rerank_score']:.4f}")
        print(f"\nCAE Classification:")
        print(f"  {result['cae'] if result['cae'] else 'N/A'}")
        print(f"\nBusiness Activities:")
        if result['activities']:
            print(f"  {result['activities']}")
        else:
            print(f"  N/A")
        print(f"\nWebsite: {result['website'] if result['website'] else 'N/A'}")
        print(f"{'='*80}")


def main():
    """
    Execute the complete matching pipeline.
    
    Pipeline stages:
        1. Select random incentive from database
        2. Generate search query from incentive data
        3. Load embedding model and reranker
        4. Vector search for 20 candidates
        5. Enrich candidates with full data
        6. Rerank to select top 5
        7. Display results
    
    This demonstrates the full system on a single incentive. In production,
    you would batch process all incentives or run on-demand for specific ones.
    """
    print("=" * 80)
    print("SEMANTIC INCENTIVE-COMPANY MATCHING TEST")
    print("Qdrant Vector Search + BGE Reranker v2-m3")
    print("=" * 80)

    # Step 1: Get random incentive
    incentive = get_random_incentive()
    if not incentive:
        return

    # Step 2: Generate semantic query
    queries = create_search_query(incentive)
    query = queries[0]  # Extract the single query string

    # Step 3: Load models
    model = load_embedding_model()
    reranker = load_reranker()

    # Step 4: Search Qdrant for initial candidates
    search_results = search_companies_qdrant(queries, model, top_k=20)

    if not search_results:
        print("[ERROR] No results found")
        return

    # Step 5: Enrich with PostgreSQL data
    company_ids = [r['id'] for r in search_results]
    company_details = enrich_with_postgres(company_ids)

    initial_results = []
    for result in search_results:
        if result['id'] in company_details:
            company = company_details[result['id']]
            company['fusion_score'] = result['score']
            initial_results.append(company)

    # Step 6: Rerank with BGE Reranker v2-m3 and get top 5
    final_results = rerank_companies(query, initial_results, reranker, top_k=5)

    # Step 7: Display final top 5 results
    display_results(incentive, final_results)

    print("\n" + "=" * 80)
    print("[SUCCESS] Matching completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
