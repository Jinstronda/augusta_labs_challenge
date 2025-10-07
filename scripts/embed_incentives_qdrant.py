"""
Incentive Embedding Pipeline

This script transforms incentive data from PostgreSQL into semantic vectors stored in Qdrant.
Each incentive is represented as a dense vector that captures the meaning of its title,
AI description, sector, and geographic requirements. These vectors enable semantic search:
finding incentives by what they support, not just by keyword matching.

The pipeline uses the same multilingual sentence transformer model as companies,
ensuring consistent semantic space for both entities.

Architecture:
    PostgreSQL (source) -> Sentence Transformer -> Qdrant (vector storage)

Usage:
    python embed_incentives_qdrant.py          # Test mode: 5 incentives
    python embed_incentives_qdrant.py --full   # Process all incentives
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


def load_embedding_model():
    """
    Load the sentence transformer model for converting text to vectors.
    
    Uses the same model as companies for consistent semantic space.
    
    Returns:
        SentenceTransformer: Loaded model ready for encoding
    """
    print("\n[MODEL] Loading embedding model...")
    print("   Using paraphrase-multilingual-MiniLM-L12-v2 (same as companies)")

    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)
    print("[OK] Model loaded successfully!")
    return model


def setup_qdrant():
    """
    Initialize Qdrant vector database and prepare collection for incentive vectors.
    
    Creates a new collection 'incentives' separate from 'companies'.
    Uses cosine distance for similarity matching.
    
    Returns:
        tuple: (QdrantClient, collection_name, embedding_model)
    """
    print("\n[QDRANT] Setting up Qdrant...")

    # Use local storage (same as companies)
    client = QdrantClient(path="./qdrant_storage")

    collection_name = "incentives"

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

    # Get vector size from model
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


def load_incentives_from_db():
    """
    Load incentive data from PostgreSQL database.
    
    Retrieves incentive_id, title, AI description, sector, and geo requirements.
    These fields are combined to create a rich semantic representation.
    
    Returns:
        list: List of tuples containing incentive data
    """
    print("\n[DB] Loading incentives from PostgreSQL...")

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Load all incentives
    cursor.execute("""
        SELECT
            incentive_id,
            title,
            ai_description,
            sector,
            geo_requirement,
            eligible_actions
        FROM incentives
        ORDER BY incentive_id
    """)

    incentives = cursor.fetchall()

    print(f"[OK] Loaded {len(incentives):,} incentives")

    cursor.close()
    conn.close()

    return incentives


def create_incentive_text(incentive):
    """
    Combine incentive fields into a single text string for embedding.
    
    Order: title (most important), AI description, sector, geo, actions.
    This creates a text that captures what the incentive supports and where.
    
    Args:
        incentive: Tuple of (id, title, ai_desc, sector, geo, actions)
    
    Returns:
        str: Combined text representation
    """
    incentive_id, title, ai_desc, sector, geo, actions = incentive
    
    text_parts = []
    
    if title:
        text_parts.append(title)
    
    if ai_desc:
        text_parts.append(ai_desc)
    
    if sector:
        text_parts.append(f"Sector: {sector}")
    
    if geo:
        text_parts.append(f"Location: {geo}")
    
    if actions:
        # Truncate long actions
        actions_text = actions[:200] if len(actions) > 200 else actions
        text_parts.append(f"Actions: {actions_text}")
    
    return " ".join(text_parts)


def embed_and_upload_incentives(client, collection_name, model, incentives):
    """
    Convert incentives to vectors and store in Qdrant.
    
    Processes in batches for efficiency. Uses incentive_id as point ID
    for direct linking with PostgreSQL.
    
    Args:
        client: QdrantClient instance
        collection_name: Name of collection to upload to
        model: Sentence transformer model
        incentives: List of incentive tuples
    """
    print("\n[EMBED] Embedding and uploading incentives to Qdrant...")
    print(f"   Total incentives: {len(incentives):,}")
    print(f"   Device: {device}")

    batch_size = 64 if device == "cuda" else 32
    total_batches = (len(incentives) + batch_size - 1) // batch_size

    print(f"   Batch size: {batch_size}")
    print(f"   Total batches: {total_batches:,}\n")
    
    for i in tqdm(range(0, len(incentives), batch_size), desc="Embedding batches"):
        batch = incentives[i:i+batch_size]
        
        # Create texts for embedding
        texts = [create_incentive_text(incentive) for incentive in batch]
        
        # Generate embeddings
        embeddings = model.encode(
            texts,
            show_progress_bar=False,
            device=device,
            batch_size=batch_size
        )
        
        # Create points for Qdrant
        points = []
        for j, incentive in enumerate(batch):
            incentive_id, title, ai_desc, sector, geo, actions = incentive
            
            # Use incentive_id as string for point ID
            point_id = int(incentive_id) if isinstance(incentive_id, str) and incentive_id.isdigit() else hash(incentive_id) % (2**63)
            
            points.append(PointStruct(
                id=point_id,  # Link to PostgreSQL via incentive_id
                vector=embeddings[j].tolist(),
                payload={
                    "incentive_id": incentive_id,
                    "title": title,
                    "ai_description": ai_desc[:500] if ai_desc else None,  # Truncate
                    "sector": sector,
                    "geo_requirement": geo,
                    "eligible_actions": actions[:300] if actions else None  # Truncate
                }
            ))
        
        # Upload batch to Qdrant
        client.upsert(
            collection_name=collection_name,
            points=points,
            wait=False
        )
    
    # Wait for all uploads to complete
    print("\n[WAIT] Finalizing uploads...")
    client.upsert(
        collection_name=collection_name,
        points=[],
        wait=True
    )

    print(f"[OK] Successfully embedded and uploaded {len(incentives):,} incentives")


def verify_qdrant_data(client, collection_name, model):
    """
    Test that embeddings were stored correctly and search works.
    
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

    # Test search
    print("\n[TEST] Testing search functionality...")
    test_query = "green energy renewable innovation funding"

    # Generate embedding for test query
    test_vector = model.encode(test_query).tolist()

    # Search
    search_results = client.query_points(
        collection_name=collection_name,
        query=test_vector,
        limit=3
    ).points

    print(f"[OK] Search test successful! Found {len(search_results)} results")
    print("\nSample results:")
    for idx, result in enumerate(search_results, 1):
        print(f"  {idx}. {result.payload['title'][:60]}... (score: {result.score:.4f})")
        sector = result.payload.get('sector', 'N/A')
        print(f"     Sector: {sector}")


def main(test_mode=True, test_limit=5):
    """
    Execute the complete embedding pipeline for incentives.
    
    Args:
        test_mode: If True, only process test_limit incentives
        test_limit: Number of incentives to process in test mode
    """
    print("=" * 70)
    if test_mode:
        print(f"Incentive Embedding Pipeline - TEST MODE ({test_limit} incentives)")
    else:
        print("Incentive Embedding Pipeline - FULL PROCESSING")
    print("Qdrant + Multilingual Embedding Model")
    print("=" * 70)
    
    # Step 1: Setup Qdrant and load model
    client, collection_name, model = setup_qdrant()
    
    # Step 2: Load incentives from PostgreSQL
    incentives = load_incentives_from_db()
    
    # Test mode: only process first N incentives
    if test_mode:
        incentives = incentives[:test_limit]
        print(f"\n[WARNING] TEST MODE: Processing only {len(incentives)} incentives")

    if not incentives:
        print("[ERROR] No incentives found in database!")
        return
    
    # Step 3: Embed and upload to Qdrant
    embed_and_upload_incentives(client, collection_name, model, incentives)
    
    # Step 4: Verify
    verify_qdrant_data(client, collection_name, model)
    
    print("\n" + "=" * 70)
    print("[OK] Embedding pipeline completed successfully!")
    print("=" * 70)
    print(f"\nQdrant storage location: ./qdrant_storage")
    print(f"Collection name: {collection_name}")
    print(f"Total vectors: {len(incentives):,}")

    if test_mode:
        print("\n[SUCCESS] Test successful!")
        print("\nTo process ALL incentives, run:")
        print("  python scripts/embed_incentives_qdrant.py --full")
    else:
        print(f"\n[SUCCESS] Incentive vectors ready for semantic search!")


if __name__ == "__main__":
    import sys
    
    # Check for --full flag
    test_mode = "--full" not in sys.argv
    
    main(test_mode=test_mode, test_limit=5)
