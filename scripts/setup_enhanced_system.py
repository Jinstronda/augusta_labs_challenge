"""
Setup Script for Enhanced Incentive-Company Matching System

This script prepares the database and validates the system configuration
for the enhanced matching system with geographic filtering.

Run this before using the enhanced matching system for the first time.
"""

import os
import sys
from dotenv import load_dotenv

# Get the project root directory (parent of scripts/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# Change to project root to ensure relative paths work
os.chdir(PROJECT_ROOT)

# Load environment variables BEFORE importing
load_dotenv('config.env')

def check_environment():
    """Check that all required environment variables are set."""
    print("Checking environment configuration...")
    
    required_vars = [
        'DB_NAME', 'DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT',
        'OPEN_AI'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("Please set these in your config.env file")
        return False
    
    # Check Google Maps API key
    google_key = "AIzaSyAKWaDFzEYZKxhuwumj1fmv-IHmz_pAGw8"
    if not google_key:
        print("❌ Google Maps API key not configured")
        print("Please set GOOGLE_MAPS_API_KEY in the script")
        return False
    
    print("✅ Environment configuration looks good")
    return True

def setup_database():
    """Set up the database schema for the enhanced system."""
    print("\nSetting up database schema...")
    
    try:
        from enhanced_incentive_matching import DatabaseManager
        
        db_manager = DatabaseManager()
        db_manager.ensure_schema()
        
        print("✅ Database schema setup completed")
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("Please check your database connection and permissions")
        return False

def test_api_connections():
    """Test connections to external APIs."""
    print("\nTesting API connections...")
    
    # Test OpenAI connection
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPEN_AI"))
        
        # Simple test call
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_completion_tokens=5
        )
        print("✅ OpenAI API connection successful")
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        print("Please check your OPEN_AI API key")
        return False
    
    # Test Google Maps API
    try:
        import requests
        
        google_key = "AIzaSyAKWaDFzEYZKxhuwumj1fmv-IHmz_pAGw8"
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': 'test',
            'key': google_key
        }
        
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if 'error_message' in data:
            print(f"❌ Google Maps API error: {data['error_message']}")
            return False
        
        print("✅ Google Maps API connection successful")
        
    except Exception as e:
        print(f"❌ Google Maps API test failed: {e}")
        return False
    
    return True

def check_models():
    """Check that required models can be loaded."""
    print("\nChecking model availability...")
    
    try:
        # Test embedding model
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ Embedding model loaded successfully")
        
        # Test reranker
        from FlagEmbedding import FlagReranker
        reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
        print("✅ Reranker model loaded successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Model loading failed: {e}")
        print("Models will be downloaded on first use")
        return False

def check_qdrant():
    """Check that Qdrant collection exists."""
    print("\nChecking Qdrant collection...")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(path="./qdrant_storage")
        collection_info = client.get_collection("companies")
        
        print(f"✅ Qdrant collection found: {collection_info.points_count:,} companies")
        return True
        
    except Exception as e:
        print(f"❌ Qdrant collection not found: {e}")
        print("Please run embed_companies_qdrant.py first to create company embeddings")
        return False

def main():
    """Run all setup and validation checks."""
    print("=" * 60)
    print("ENHANCED INCENTIVE MATCHING SYSTEM SETUP")
    print("=" * 60)
    
    checks = [
        ("Environment Variables", check_environment),
        ("Database Schema", setup_database),
        ("API Connections", test_api_connections),
        ("Qdrant Collection", check_qdrant),
        ("Model Loading", check_models),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{'-' * 40}")
        print(f"CHECKING: {name}")
        print(f"{'-' * 40}")
        
        try:
            success = check_func()
            results.append((name, success))
        except Exception as e:
            print(f"❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print(f"\n{'=' * 60}")
    print("SETUP SUMMARY")
    print(f"{'=' * 60}")
    
    all_passed = True
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name:<25} {status}")
        if not success:
            all_passed = False
    
    print(f"\n{'=' * 60}")
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("The enhanced matching system is ready to use.")
        print("\nTo test the system, run:")
        print("  python enhanced_incentive_matching.py")
    else:
        print("⚠️  SOME CHECKS FAILED")
        print("Please fix the issues above before using the enhanced system.")
        print("\nYou can still run the basic system with:")
        print("  python test_incentive_matching.py")
    
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()