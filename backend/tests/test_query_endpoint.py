"""
Integration tests for the query API endpoint

Tests the full query flow with mocked services.
"""

import sys
import os
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient


def test_query_endpoint_incentive():
    """Test query endpoint with INCENTIVE classification"""
    print("\n[TEST 1] Testing query endpoint for INCENTIVE...")
    
    # Mock app state
    mock_app_state = {
        'embedding_model': Mock(),
        'qdrant_client': Mock()
    }
    
    with patch('app.main.get_app_state', return_value=mock_app_state):
        # Mock classifier
        with patch('app.services.classifier.QueryClassifier') as MockClassifier:
            mock_classifier = Mock()
            mock_classifier.classify.return_value = "INCENTIVE"
            MockClassifier.return_value = mock_classifier
            
            # Mock search service
            with patch('app.services.search.SemanticSearchService') as MockSearch:
                mock_search = Mock()
                mock_search.search_incentives.return_value = [
                    {
                        'incentive_id': 'INC001',
                        'title': 'Test Incentive',
                        'confidence': 'high',
                        'relevance_score': 10
                    }
                ]
                MockSearch.return_value = mock_search
                
                # Mock database service
                with patch('app.services.database.DatabaseService') as MockDB:
                    mock_db = Mock()
                    mock_db.get_incentive_with_companies.return_value = {
                        'incentive_id': 'INC001',
                        'title': 'Test Incentive',
                        'description': 'Test description',
                        'matched_companies': []
                    }
                    MockDB.return_value = mock_db
                    
                    # Import app after mocking
                    from app.main import app
                    client = TestClient(app)
                    
                    # Make request
                    response = client.post("/api/query", json={"query": "test incentive query"})
                    
                    # Verify response
                    assert response.status_code == 200
                    data = response.json()
                    
                    assert data['query_type'] == 'INCENTIVE'
                    assert data['query'] == 'test incentive query'
                    assert data['result_count'] == 1
                    assert 'processing_time' in data
                    
                    print(f"  ✓ Response: {data['result_count']} results")
                    print(f"  ✓ Query type: {data['query_type']}")
                    print(f"  ✓ Processing time: {data['processing_time']:.3f}s")
    
    print("✓ INCENTIVE query endpoint test passed")


def test_query_endpoint_company():
    """Test query endpoint with COMPANY classification"""
    print("\n[TEST 2] Testing query endpoint for COMPANY...")
    
    # Mock app state
    mock_app_state = {
        'embedding_model': Mock(),
        'qdrant_client': Mock()
    }
    
    with patch('app.main.get_app_state', return_value=mock_app_state):
        # Mock classifier
        with patch('app.services.classifier.QueryClassifier') as MockClassifier:
            mock_classifier = Mock()
            mock_classifier.classify.return_value = "COMPANY"
            MockClassifier.return_value = mock_classifier
            
            # Mock search service
            with patch('app.services.search.SemanticSearchService') as MockSearch:
                mock_search = Mock()
                mock_search.search_companies.return_value = [
                    {
                        'id': 123,
                        'name': 'Test Company',
                        'confidence': 'high',
                        'score': 0.85
                    }
                ]
                MockSearch.return_value = mock_search
                
                # Mock database service
                with patch('app.services.database.DatabaseService') as MockDB:
                    mock_db = Mock()
                    mock_db.get_company_with_incentives.return_value = {
                        'company_id': 123,
                        'company_name': 'Test Company',
                        'eligible_incentives': []
                    }
                    MockDB.return_value = mock_db
                    
                    # Import app after mocking
                    from app.main import app
                    client = TestClient(app)
                    
                    # Make request
                    response = client.post("/api/query", json={"query": "test company query"})
                    
                    # Verify response
                    assert response.status_code == 200
                    data = response.json()
                    
                    assert data['query_type'] == 'COMPANY'
                    assert data['query'] == 'test company query'
                    assert data['result_count'] == 1
                    assert 'processing_time' in data
                    
                    print(f"  ✓ Response: {data['result_count']} results")
                    print(f"  ✓ Query type: {data['query_type']}")
                    print(f"  ✓ Processing time: {data['processing_time']:.3f}s")
    
    print("✓ COMPANY query endpoint test passed")


def test_query_endpoint_validation():
    """Test query endpoint input validation"""
    print("\n[TEST 3] Testing query endpoint validation...")
    
    # Mock app state
    mock_app_state = {
        'embedding_model': Mock(),
        'qdrant_client': Mock()
    }
    
    with patch('app.main.get_app_state', return_value=mock_app_state):
        from app.main import app
        client = TestClient(app)
        
        # Test empty query
        response = client.post("/api/query", json={"query": ""})
        assert response.status_code == 422  # Validation error
        print("  ✓ Empty query rejected")
        
        # Test missing query
        response = client.post("/api/query", json={})
        assert response.status_code == 422  # Validation error
        print("  ✓ Missing query rejected")
        
        # Test query too long (>500 chars)
        long_query = "a" * 501
        response = client.post("/api/query", json={"query": long_query})
        assert response.status_code == 422  # Validation error
        print("  ✓ Query too long rejected")
    
    print("✓ Query validation test passed")


def main():
    """Run all tests"""
    print("=" * 70)
    print("QUERY ENDPOINT INTEGRATION TESTS")
    print("=" * 70)
    print("\nNote: These tests use mocks and don't require external services")
    
    try:
        test_query_endpoint_incentive()
        test_query_endpoint_company()
        test_query_endpoint_validation()
        
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
