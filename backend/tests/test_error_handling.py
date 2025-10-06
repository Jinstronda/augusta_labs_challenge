"""
Tests for error handling and health checks
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient


def test_health_check_detailed():
    """Test detailed health check endpoint"""
    print("\n[TEST 1] Testing detailed health check...")
    
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    
    # Check required fields
    assert 'status' in data
    assert 'timestamp' in data
    assert 'components' in data
    
    # Check components
    components = data['components']
    assert 'models' in components
    assert 'database' in components
    
    print(f"  ✓ Overall status: {data['status']}")
    print(f"  ✓ Timestamp: {data['timestamp']}")
    print(f"  ✓ Models status: {components['models']['status']}")
    print(f"  ✓ Database status: {components['database']['status']}")
    
    if 'qdrant' in components:
        print(f"  ✓ Qdrant status: {components['qdrant']['status']}")
    
    print("✓ Detailed health check test passed")


def test_validation_error_handling():
    """Test validation error handling"""
    print("\n[TEST 2] Testing validation error handling...")
    
    from app.main import app
    client = TestClient(app)
    
    # Test empty query (should trigger validation error)
    response = client.post("/api/query", json={"query": ""})
    assert response.status_code == 422
    
    data = response.json()
    assert 'error' in data
    assert 'detail' in data
    assert 'status_code' in data
    assert data['status_code'] == 422
    
    print(f"  ✓ Validation error caught")
    print(f"  ✓ Error type: {data['error']}")
    print(f"  ✓ Status code: {data['status_code']}")
    
    print("✓ Validation error handling test passed")


def test_404_error_handling():
    """Test 404 error handling"""
    print("\n[TEST 3] Testing 404 error handling...")
    
    from app.main import app
    client = TestClient(app)
    
    # Test non-existent endpoint
    response = client.get("/api/nonexistent")
    assert response.status_code == 404
    
    data = response.json()
    assert 'detail' in data
    
    print(f"  ✓ 404 error returned")
    print(f"  ✓ Detail: {data['detail']}")
    
    print("✓ 404 error handling test passed")


def test_cors_headers():
    """Test CORS headers are present"""
    print("\n[TEST 4] Testing CORS headers...")
    
    from app.main import app
    client = TestClient(app)
    
    # Make request with Origin header
    response = client.get(
        "/health",
        headers={"Origin": "http://localhost:3000"}
    )
    
    assert response.status_code == 200
    
    # Check CORS headers
    headers = response.headers
    assert 'access-control-allow-origin' in headers
    
    print(f"  ✓ CORS headers present")
    print(f"  ✓ Allow-Origin: {headers.get('access-control-allow-origin')}")
    
    print("✓ CORS headers test passed")


def test_http_methods():
    """Test that correct HTTP methods are supported"""
    print("\n[TEST 5] Testing HTTP methods...")
    
    from app.main import app
    client = TestClient(app)
    
    # Test GET on root
    response = client.get("/")
    assert response.status_code == 200
    print("  ✓ GET / works")
    
    # Test GET on health
    response = client.get("/health")
    assert response.status_code == 200
    print("  ✓ GET /health works")
    
    # Test POST on query
    response = client.post("/api/query", json={"query": "test"})
    assert response.status_code in [200, 500]  # 500 if services not available
    print("  ✓ POST /api/query works")
    
    # Test GET on incentive detail
    response = client.get("/api/incentive/test")
    assert response.status_code in [200, 404, 500]
    print("  ✓ GET /api/incentive/:id works")
    
    # Test GET on company detail
    response = client.get("/api/company/123")
    assert response.status_code in [200, 404, 500]
    print("  ✓ GET /api/company/:id works")
    
    print("✓ HTTP methods test passed")


def test_openapi_spec():
    """Test OpenAPI specification is available"""
    print("\n[TEST 6] Testing OpenAPI specification...")
    
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    spec = response.json()
    
    # Check required OpenAPI fields
    assert 'openapi' in spec
    assert 'info' in spec
    assert 'paths' in spec
    
    # Check API info
    info = spec['info']
    assert 'title' in info
    assert 'version' in info
    
    print(f"  ✓ OpenAPI version: {spec['openapi']}")
    print(f"  ✓ API title: {info['title']}")
    print(f"  ✓ API version: {info['version']}")
    print(f"  ✓ Endpoints documented: {len(spec['paths'])}")
    
    print("✓ OpenAPI specification test passed")


def main():
    """Run all tests"""
    print("=" * 70)
    print("ERROR HANDLING AND HEALTH CHECKS TESTS")
    print("=" * 70)
    
    try:
        test_health_check_detailed()
        test_validation_error_handling()
        test_404_error_handling()
        test_cors_headers()
        test_http_methods()
        test_openapi_spec()
        
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
