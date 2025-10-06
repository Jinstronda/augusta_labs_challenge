"""
Unit tests for SemanticSearchService (without external dependencies)

Tests the service logic without requiring Qdrant or database connections.
"""

import sys
import os
from unittest.mock import Mock, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.search import SemanticSearchService


def test_confidence_calculation():
    """Test confidence level calculation"""
    print("\n[TEST 1] Testing confidence calculation...")
    
    # Create mock models
    mock_model = Mock()
    mock_qdrant = Mock()
    
    service = SemanticSearchService(mock_model, mock_qdrant)
    
    # Test different score ranges
    test_cases = [
        (0.9, "high"),
        (0.7, "high"),
        (0.6, "medium"),
        (0.4, "medium"),
        (0.3, "low"),
        (0.1, "low"),
        # Test normalization of scores > 1
        (10.0, "high"),
        (5.0, "medium"),
        (2.0, "low")
    ]
    
    for score, expected_confidence in test_cases:
        confidence = service._calculate_confidence(score)
        assert confidence == expected_confidence, f"Score {score} should give {expected_confidence}, got {confidence}"
        print(f"  ✓ Score {score:.1f} → {confidence}")
    
    print("✓ Confidence calculation test passed")


def test_search_companies_with_mock():
    """Test company search with mocked Qdrant"""
    print("\n[TEST 2] Testing company search with mock...")
    
    # Create mock models
    mock_model = Mock()
    mock_model.encode = Mock(return_value=[0.1, 0.2, 0.3])  # Mock embedding
    
    mock_qdrant = Mock()
    
    # Mock search results
    mock_result = Mock()
    mock_result.score = 0.85
    mock_result.payload = {
        'company_id': 123,
        'company_name': 'Test Company',
        'cae_primary_label': 'Construction',
        'trade_description_native': 'Building construction',
        'website': 'www.test.com'
    }
    
    mock_qdrant.search = Mock(return_value=[mock_result])
    
    service = SemanticSearchService(mock_model, mock_qdrant)
    
    # Test search
    results = service.search_companies("test query", limit=5)
    
    # Verify
    assert len(results) == 1
    assert results[0]['id'] == 123
    assert results[0]['name'] == 'Test Company'
    assert results[0]['score'] == 0.85
    assert results[0]['confidence'] == 'high'
    
    # Verify model was called
    mock_model.encode.assert_called_once()
    mock_qdrant.search.assert_called_once()
    
    print("  ✓ Company search with mock passed")
    print(f"    Result: {results[0]['name']} (score: {results[0]['score']})")
    
    print("✓ Company search mock test passed")


def test_service_initialization():
    """Test service initialization"""
    print("\n[TEST 3] Testing service initialization...")
    
    mock_model = Mock()
    mock_qdrant = Mock()
    
    service = SemanticSearchService(mock_model, mock_qdrant)
    
    assert service.embedding_model is mock_model
    assert service.qdrant_client is mock_qdrant
    assert service.collection_name is not None
    
    print("✓ Service initialization test passed")


def main():
    """Run all tests"""
    print("=" * 70)
    print("SEMANTIC SEARCH SERVICE UNIT TESTS")
    print("=" * 70)
    print("\nNote: These tests use mocks and don't require external services")
    
    try:
        test_service_initialization()
        test_confidence_calculation()
        test_search_companies_with_mock()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print("\nNote: For integration tests with real Qdrant/DB, run:")
        print("  python backend/tests/test_search.py")
        
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
