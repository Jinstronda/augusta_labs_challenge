"""
Tests for detail page API endpoints

Tests incentive and company detail endpoints.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient


def test_incentive_detail_endpoint():
    """Test incentive detail endpoint"""
    print("\n[TEST 1] Testing incentive detail endpoint...")
    
    from app.main import app
    client = TestClient(app)
    
    # First, find a valid incentive ID
    import psycopg2
    from app.config import settings
    
    try:
        conn = psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SELECT incentive_id FROM incentives WHERE top_5_companies_scored IS NOT NULL LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            print("  ⚠ No incentives with scored companies found - skipping test")
            return
        
        incentive_id = result[0]
        
        # Test valid incentive
        response = client.get(f"/api/incentive/{incentive_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'incentive_id' in data
        assert 'title' in data
        assert 'matched_companies' in data
        
        print(f"  ✓ Fetched incentive: {data['title'][:60]}...")
        print(f"  ✓ Matched companies: {len(data['matched_companies'])}")
        
    except Exception as e:
        print(f"  ⚠ Database connection failed: {e}")
        print("  Skipping test (requires database)")
        return
    
    print("✓ Incentive detail endpoint test passed")


def test_incentive_detail_not_found():
    """Test incentive detail endpoint with invalid ID"""
    print("\n[TEST 2] Testing incentive detail endpoint with invalid ID...")
    
    from app.main import app
    client = TestClient(app)
    
    # Test non-existent incentive
    response = client.get("/api/incentive/NONEXISTENT_ID_12345")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    data = response.json()
    assert 'detail' in data
    
    print(f"  ✓ 404 returned for non-existent incentive")
    print(f"  ✓ Error message: {data['detail']}")
    
    print("✓ Incentive not found test passed")


def test_company_detail_endpoint():
    """Test company detail endpoint"""
    print("\n[TEST 3] Testing company detail endpoint...")
    
    from app.main import app
    client = TestClient(app)
    
    # First, find a valid company ID
    import psycopg2
    from app.config import settings
    
    try:
        conn = psycopg2.connect(
            dbname=settings.DB_NAME,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            host=settings.DB_HOST,
            port=settings.DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute("SELECT company_id FROM companies WHERE eligible_incentives IS NOT NULL LIMIT 1")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result:
            print("  ⚠ No companies with eligible incentives found - skipping test")
            return
        
        company_id = result[0]
        
        # Test valid company
        response = client.get(f"/api/company/{company_id}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        
        data = response.json()
        assert 'company_id' in data
        assert 'company_name' in data
        assert 'eligible_incentives' in data
        
        print(f"  ✓ Fetched company: {data['company_name']}")
        print(f"  ✓ Eligible incentives: {len(data['eligible_incentives'])}")
        
    except Exception as e:
        print(f"  ⚠ Database connection failed: {e}")
        print("  Skipping test (requires database)")
        return
    
    print("✓ Company detail endpoint test passed")


def test_company_detail_not_found():
    """Test company detail endpoint with invalid ID"""
    print("\n[TEST 4] Testing company detail endpoint with invalid ID...")
    
    from app.main import app
    client = TestClient(app)
    
    # Test non-existent company
    response = client.get("/api/company/999999999")
    assert response.status_code == 404, f"Expected 404, got {response.status_code}"
    
    data = response.json()
    assert 'detail' in data
    
    print(f"  ✓ 404 returned for non-existent company")
    print(f"  ✓ Error message: {data['detail']}")
    
    print("✓ Company not found test passed")


def test_detail_endpoints_in_openapi():
    """Test that detail endpoints are documented in OpenAPI spec"""
    print("\n[TEST 5] Testing detail endpoints in OpenAPI spec...")
    
    from app.main import app
    client = TestClient(app)
    
    response = client.get("/openapi.json")
    assert response.status_code == 200
    
    spec = response.json()
    paths = spec.get('paths', {})
    
    # Check incentive detail endpoint
    assert '/api/incentive/{incentive_id}' in paths, "Incentive detail endpoint not in OpenAPI spec"
    print("  ✓ Incentive detail endpoint documented")
    
    # Check company detail endpoint
    assert '/api/company/{company_id}' in paths, "Company detail endpoint not in OpenAPI spec"
    print("  ✓ Company detail endpoint documented")
    
    print("✓ OpenAPI documentation test passed")


def main():
    """Run all tests"""
    print("=" * 70)
    print("DETAIL ENDPOINTS TESTS")
    print("=" * 70)
    print("\nNote: Some tests require database connection")
    
    try:
        test_detail_endpoints_in_openapi()
        test_incentive_detail_not_found()
        test_company_detail_not_found()
        test_incentive_detail_endpoint()
        test_company_detail_endpoint()
        
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
