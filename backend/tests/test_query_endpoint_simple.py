"""
Simple integration tests for the query API endpoint

Tests basic endpoint functionality without complex mocking.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient


def test_query_endpoint_exists():
    """Test that query endpoint exists and accepts requests"""
    print("\n[TEST 1] Testing query endpoint exists...")
    
    from app.main import app
    client = TestClient(app)
    
    # Test with valid query
    response = client.post("/api/query", json={"query": "test query"})
    
    # Should return 200 or 500 (depending on services), but not 404
    assert response.status_code in [200, 500], f"Unexpected status code: {response.status_code}"
    print(f"  ✓ Endpoint exists (status: {response.status_code})")
    
    print("✓ Query endpoint exists test passed")


def test_query_endpoint_validation():
    """Test query endpoint input validation"""
    print("\n[TEST 2] Testing query endpoint validation...")
    
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


def test_health_endpoint():
    """Test health check endpoint"""
    print("\n[TEST 3] Testing health endpoint...")
    
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert 'status' in data
    assert data['status'] == 'healthy'
    
    print(f"  ✓ Health check: {data['status']}")
    print(f"  ✓ Models loaded: {data.get('models_loaded', False)}")
    
    print("✓ Health endpoint test passed")


def test_root_endpoint():
    """Test root endpoint"""
    print("\n[TEST 4] Testing root endpoint...")
    
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert 'message' in data
    assert 'version' in data
    
    print(f"  ✓ Message: {data['message']}")
    print(f"  ✓ Version: {data['version']}")
    
    print("✓ Root endpoint test passed")


def test_docs_endpoint():
    """Test that API docs are available"""
    print("\n[TEST 5] Testing API docs endpoint...")
    
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/docs")
    assert response.status_code == 200
    print("  ✓ API docs available at /docs")
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    print("  ✓ OpenAPI spec available at /openapi.json")
    
    print("✓ API docs test passed")


def main():
    """Run all tests"""
    print("=" * 70)
    print("QUERY ENDPOINT SIMPLE TESTS")
    print("=" * 70)
    print("\nNote: These tests verify endpoint structure without external services")
    
    try:
        test_root_endpoint()
        test_health_endpoint()
        test_docs_endpoint()
        test_query_endpoint_exists()
        test_query_endpoint_validation()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        print("\nThe query endpoint is properly configured!")
        print("For full integration tests with real services, ensure:")
        print("  - PostgreSQL is running with data")
        print("  - Qdrant is running with company embeddings")
        print("  - OpenAI API key is configured")
        
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
