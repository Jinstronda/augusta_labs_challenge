"""
Unit tests for SemanticSearchService

Tests search functionality with real database and Qdrant connections.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.search import SemanticSearchService
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from app.config import settings


def test_search_service_initialization():
    """Test that search service initializes correctly"""
    print("\n[TEST 1] Testing search service initialization...")
    
    # Load models
    embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    
    # Create service
    service = SemanticSearchService(embedding_model, qdrant_client)
    
    assert service.embedding_model is not None
    assert service.qdrant_client is not None
    assert service.collection_name == settings.QDRANT_COLLECTION
    
    print("✓ Search service initialized successfully")


def test_search_companies():
    """Test company search with vector similarity"""
    print("\n[TEST 2] Testing company search...")
    
    # Load models
    print("  Loading embedding model...")
    embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    
    service = SemanticSearchService(embedding_model, qdrant_client)
    
    # Test queries
    test_queries = [
        "empresas de construção",
        "tecnologia e software",
        "restaurantes"
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        results = service.search_companies(query, limit=3)
        
        assert isinstance(results, list), "Results should be a list"
        assert len(results) <= 3, "Should return at most 3 results"
        
        if results:
            company = results[0]
            assert 'id' in company
            assert 'name' in company
            assert 'score' in company
            assert 'confidence' in company
            
            print(f"    Top result: {company['name']}")
            print(f"    Score: {company['score']:.3f}")
            print(f"    Confidence: {company['confidence']}")
    
    print("\n✓ Company search test passed")


def test_search_incentives():
    """Test incentive search with keyword matching"""
    print("\n[TEST 3] Testing incentive search...")
    
    # Load models (needed for initialization)
    embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    
    service = SemanticSearchService(embedding_model, qdrant_client)
    
    # Test queries
    test_queries = [
        "inovação",
        "digitalização",
        "exportação"
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        results = service.search_incentives(query, limit=3)
        
        assert isinstance(results, list), "Results should be a list"
        assert len(results) <= 3, "Should return at most 3 results"
        
        if results:
            incentive = results[0]
            assert 'incentive_id' in incentive
            assert 'title' in incentive
            assert 'relevance_score' in incentive
            assert 'confidence' in incentive
            
            print(f"    Top result: {incentive['title'][:60]}...")
            print(f"    Relevance: {incentive['relevance_score']}")
            print(f"    Confidence: {incentive['confidence']}")
    
    print("\n✓ Incentive search test passed")


def test_confidence_calculation():
    """Test confidence level calculation"""
    print("\n[TEST 4] Testing confidence calculation...")
    
    # Load models
    embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    
    service = SemanticSearchService(embedding_model, qdrant_client)
    
    # Test different score ranges
    test_cases = [
        (0.9, "high"),
        (0.7, "high"),
        (0.6, "medium"),
        (0.4, "medium"),
        (0.3, "low"),
        (0.1, "low")
    ]
    
    for score, expected_confidence in test_cases:
        confidence = service._calculate_confidence(score)
        assert confidence == expected_confidence, f"Score {score} should give {expected_confidence}, got {confidence}"
        print(f"  ✓ Score {score:.1f} → {confidence}")
    
    print("✓ Confidence calculation test passed")


def test_empty_query():
    """Test handling of empty queries"""
    print("\n[TEST 5] Testing empty query handling...")
    
    # Load models
    embedding_model = SentenceTransformer(settings.EMBEDDING_MODEL)
    qdrant_client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    
    service = SemanticSearchService(embedding_model, qdrant_client)
    
    # Empty query should still work (return some results)
    results = service.search_companies("", limit=3)
    assert isinstance(results, list)
    print(f"  ✓ Empty query returned {len(results)} results")
    
    results = service.search_incentives("", limit=3)
    assert isinstance(results, list)
    print(f"  ✓ Empty incentive query returned {len(results)} results")
    
    print("✓ Empty query handling test passed")


def main():
    """Run all tests"""
    print("=" * 70)
    print("SEMANTIC SEARCH SERVICE TESTS")
    print("=" * 70)
    print("\nNote: These tests require:")
    print("  - Qdrant running with companies collection")
    print("  - PostgreSQL with incentives data")
    print("  - Internet connection (first run downloads model)")
    
    try:
        test_search_service_initialization()
        test_search_companies()
        test_search_incentives()
        test_confidence_calculation()
        test_empty_query()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
