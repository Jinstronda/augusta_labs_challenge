"""
Company Embedding Pipeline

This script transforms company data from PostgreSQL into semantic vectors stored in Qdrant.
Each company is represented as a dense vector that captures the meaning of its name,
industry classification, and business activities. These vectors enable semantic search:
finding companies by what they do, not just by keyword matching.

The pipeline uses a multilingual sentence transformer model that understands both
Portuguese and English, making it effective for Portuguese company descriptions with
English industry classifications.

Architecture:
    PostgreSQL (source) -> Sentence Transformer -> Qdrant (vector storage)

Usage:
    python embed_companies_qdrant.py          # Test mode: 2 companies
    python embed_companies_qdrant.py --full   # Process all companies
"""
import os
import psycopg2
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import torch
from tqdm import tqdm

# Load environment variables
load_dotenv('config.env')

# Database configuration
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# Check GPU availability
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[GPU] Using device: {device}")
if device == "cpu":
    print("[WARNING] No GPU detected. Embedding will be slower on CPU.")
    print("   Consider using a GPU for faster processing.")


def load_embedding_model():
    """
    Load the sentence transformer model for converting text to vectors.
    
    Tries to load paraphrase-multilingual-MiniLM-L12-v2 first, which handles
    Portuguese and English well. Falls back to English-only model if needed.
    
    The model runs on GPU if available, otherwise CPU. GPU is 10-20x faster
    for batch processing but not required.
    
    Returns:
        SentenceTransformer: Loaded model ready for encoding
    """
    print("\n[MODEL] Loading embedding model...")
    print("   (First run will download the model)")

    try:
        # Try loading multilingual model (better for Portuguese company names)
        print("   Attempting to load multilingual model (paraphrase-multilingual-MiniLM-L12-v2)...")
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)
        print("[OK] Multilingual model loaded successfully! (~420MB, good for Portuguese)")
        return model
    except Exception as e:
        print(f"[WARNING] Could not load multilingual model: {e}")
        print("   Falling back to all-MiniLM-L6-v2 (English-optimized, ~80MB)")
        model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
        print("[OK] Fallback model loaded successfully!")
        return model


def setup_qdrant():
    """
    Initialize Qdrant vector database and prepare collection for company vectors.
    
    Qdrant stores vectors locally in ./qdrant_storage - no server required.
    The collection uses cosine distance for similarity, which works well for
    normalized sentence embeddings.
    
    If a collection already exists, prompts user to delete or reuse it.
    This prevents accidentally overwriting existing embeddings.
    
    Returns:
        tuple: (QdrantClient, collection_name, embedding_model)
    """
    print("\n[QDRANT] Setting up Qdrant...")

    # Use local storage (no server needed)
    client = QdrantClient(path="./qdrant_storage")

    collection_name = "companies"

    # Check if collection exists
    collections = client.get_collections().collections
    collection_exists = any(c.name == collection_name for c in collections)

    # Get model first (needed for vector size)
    model = load_embedding_model()
    
    if collection_exists:
        print(f"[WARNING] Collection '{collection_name}' already exists")
        user_input = input("   Delete and recreate? (y/n): ")
        if user_input.lower() == 'y':
            client.delete_collection(collection_name)
            print("   [OK] Old collection deleted")
        else:
            print("   Using existing collection")
            return client, collection_name, model

    # Get vector size from already loaded model
    vector_size = model.get_sentence_embedding_dimension()

    print(f"   Vector dimension: {vector_size}")

    # Create collection
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=vector_size,
            distance=Distance.COSINE
        )
    )

    print(f"[OK] Collection '{collection_name}' created successfully")

    return client, collection_name, model


def load_companies_from_db():
    """
    Load company data from PostgreSQL database.
    
    Retrieves company_id (for linking), name, CAE classification (industry),
    business activities description, and website. These fields are combined
    to create a rich semantic representation of each company.
    
    Returns:
        list: List of tuples containing company data
    """
    print("\n[DB] Loading companies from PostgreSQL...")

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Load all companies
    cursor.execute("""
        SELECT
            company_id,
            company_name,
            cae_primary_label,
            trade_description_native,
            website
        FROM companies
        ORDER BY company_id
    """)

    companies = cursor.fetchall()

    print(f"[OK] Loaded {len(companies):,} companies")

    cursor.close()
    conn.close()

    return companies


def create_company_text(company):
    """
    Combine company fields into a single text string for embedding.
    
    The order matters: name first (most important), then CAE classification,
    then detailed activities. This creates a text that captures both the
    company's identity and what it does.
    
    Args:
        company: Tuple of (id, name, cae, activities, website)
    
    Returns:
        str: Combined text representation
    """
    company_id, name, cae, activities, website = company
    
    # Combine name + CAE + activities
    text_parts = []
    
    if name:
        text_parts.append(name)
    
    if cae:
        text_parts.append(cae)
    
    if activities:
        text_parts.append(activities)
    
    return " ".join(text_parts)


def embed_and_upload_companies(client, collection_name, model, companies):
    """
    Convert companies to vectors and store in Qdrant.
    
    Processes companies in batches for efficiency. GPU can handle larger batches
    (64) than CPU (32). Each batch is embedded in parallel, then uploaded to Qdrant.
    
    The company_id is used as the point ID in Qdrant, creating a direct link
    between the vector database and PostgreSQL. This allows fetching full company
    details after vector search.
    
    Payload includes key fields for quick access without database lookup.
    Activities are truncated to 500 chars to keep payload size reasonable.
    
    Args:
        client: QdrantClient instance
        collection_name: Name of collection to upload to
        model: Sentence transformer model
        companies: List of company tuples
    """
    print("\n[EMBED] Embedding and uploading companies to Qdrant...")
    print(f"   Total companies: {len(companies):,}")
    print(f"   Device: {device}")

    batch_size = 64 if device == "cuda" else 32  # Larger batches on GPU
    total_batches = (len(companies) + batch_size - 1) // batch_size

    print(f"   Batch size: {batch_size}")
    print(f"   Total batches: {total_batches:,}\n")
    
    for i in tqdm(range(0, len(companies), batch_size), desc="Embedding batches"):
        batch = companies[i:i+batch_size]
        
        # Create texts for embedding
        texts = [create_company_text(company) for company in batch]
        
        # Generate embeddings (GPU accelerated if available)
        embeddings = model.encode(
            texts,
            show_progress_bar=False,
            device=device,
            batch_size=batch_size
        )
        
        # Create points for Qdrant
        points = []
        for j, company in enumerate(batch):
            company_id, name, cae, activities, website = company
            
            points.append(PointStruct(
                id=company_id,  # Link to PostgreSQL via company_id
                vector=embeddings[j].tolist(),
                payload={
                    "company_name": name,
                    "cae_primary_label": cae,
                    "trade_description_native": activities[:500] if activities else None,  # Truncate long text
                    "website": website,
                    "has_website": bool(website and website.strip())
                }
            ))
        
        # Upload batch to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points,
            wait=False  # Don't wait for each batch (faster)
        )
    
    # Wait for all uploads to complete
    print("\n[WAIT] Finalizing uploads...")
    client.upsert(
        collection_name=collection_name,
        points=[],  # Empty upsert to flush
        wait=True
    )

    print(f"[OK] Successfully embedded and uploaded {len(companies):,} companies")


def verify_qdrant_data(client, collection_name, model):
    """
    Test that embeddings were stored correctly and search works.
    
    Runs a sample query to verify the vector search pipeline is functional.
    This catches issues like dimension mismatches or corrupted data before
    running the full matching system.
    
    Args:
        client: QdrantClient instance
        collection_name: Name of collection to verify
        model: Sentence transformer model for test query
    """
    print("\n[VERIFY] Verifying Qdrant data...")

    # Get collection info
    collection_info = client.get_collection(collection_name)

    print(f"[OK] Collection: {collection_name}")
    print(f"  Vectors count: {collection_info.points_count:,}")
    print(f"  Vector size: {collection_info.config.params.vectors.size}")

    # Test search with a real query
    print("\n[TEST] Testing search functionality...")
    test_query = "software development empresa tecnologia"

    # Generate embedding for test query
    test_vector = model.encode(test_query).tolist()

    # Use query_points (new API) instead of deprecated search
    from qdrant_client.models import QueryRequest

    search_results = client.query_points(
        collection_name=collection_name,
        query=test_vector,
        limit=3
    ).points

    print(f"[OK] Search test successful! Found {len(search_results)} results")
    print("\nSample results:")
    for idx, result in enumerate(search_results, 1):
        print(f"  {idx}. {result.payload['company_name']} (score: {result.score:.4f})")
        cae_label = result.payload.get('cae_primary_label', 'N/A')
        if cae_label and len(cae_label) > 60:
            print(f"     CAE: {cae_label[:60]}...")
        else:
            print(f"     CAE: {cae_label}")


def main(test_mode=True, test_limit=2):
    """
    Execute the complete embedding pipeline.
    
    Test mode processes only a few companies to verify the pipeline works.
    Full mode processes all companies, which can take 10-30 minutes depending
    on dataset size and hardware.
    
    Pipeline stages:
        1. Setup Qdrant and load embedding model
        2. Load companies from PostgreSQL
        3. Embed and upload in batches
        4. Verify data integrity
    
    Args:
        test_mode: If True, only process test_limit companies
        test_limit: Number of companies to process in test mode
    """
    print("=" * 70)
    if test_mode:
        print(f"Company Embedding Pipeline - TEST MODE ({test_limit} companies)")
    else:
        print("Company Embedding Pipeline - FULL PROCESSING")
    print("Qdrant + Multilingual Embedding Model")
    print("=" * 70)
    
    # Step 1: Setup Qdrant and load model
    client, collection_name, model = setup_qdrant()
    
    # Step 2: Load companies from PostgreSQL
    companies = load_companies_from_db()
    
    # Test mode: only process first N companies
    if test_mode:
        companies = companies[:test_limit]
        print(f"\n[WARNING] TEST MODE: Processing only {len(companies)} companies")

    if not companies:
        print("[ERROR] No companies found in database!")
        print("  Run setup_companies.py first")
        return
    
    # Step 3: Embed and upload to Qdrant
    embed_and_upload_companies(client, collection_name, model, companies)
    
    # Step 4: Verify
    verify_qdrant_data(client, collection_name, model)
    
    print("\n" + "=" * 70)
    print("[OK] Embedding pipeline completed successfully!")
    print("=" * 70)
    print(f"\nQdrant storage location: ./qdrant_storage")
    print(f"Collection name: {collection_name}")
    print(f"Total vectors: {len(companies):,}")

    if test_mode:
        print("\n[SUCCESS] Test successful!")
        print("\nTo process ALL companies, run:")
        print("  python embed_companies_qdrant.py --full")
    else:
        print(f"\n[SUCCESS] Ready for incentive matching!")


if __name__ == "__main__":
    import sys
    
    # Check for --full flag
    test_mode = "--full" not in sys.argv
    
    main(test_mode=test_mode, test_limit=2)
