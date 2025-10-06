"""
Simple standalone test for DatabaseService (no pytest required)

Tests database operations with a real database connection.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.database import DatabaseService


def test_database_connection():
    """Test that database connection pool is initialized"""
    print("\n[TEST 1] Testing database connection...")
    
    service = DatabaseService()
    assert service.connection_pool is not None, "Connection pool not initialized"
    
    # Test getting and returning a connection
    conn = service.get_connection()
    assert conn is not None, "Failed to get connection"
    service.return_connection(conn)
    
    service.close()
    print("✓ Database connection test passed")


def test_get_incentive_with_companies():
    """Test fetching an incentive with its matched companies"""
    print("\n[TEST 2] Testing get_incentive_with_companies...")
    
    service = DatabaseService()
    
    # First, find an incentive that has scored companies
    conn = service.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT incentive_id 
        FROM incentives 
        WHERE top_5_companies_scored IS NOT NULL 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    cursor.close()
    service.return_connection(conn)
    
    if not result:
        print("⚠ No incentives with scored companies found - skipping test")
        service.close()
        return
    
    incentive_id = result[0]
    
    # Fetch the incentive
    incentive_data = service.get_incentive_with_companies(incentive_id)
    
    # Verify structure
    assert incentive_data is not None, "Incentive data is None"
    assert 'incentive_id' in incentive_data, "Missing incentive_id"
    assert 'title' in incentive_data, "Missing title"
    assert 'matched_companies' in incentive_data, "Missing matched_companies"
    assert isinstance(incentive_data['matched_companies'], list), "matched_companies is not a list"
    
    # If there are companies, verify their structure
    if incentive_data['matched_companies']:
        company = incentive_data['matched_companies'][0]
        assert 'id' in company, "Company missing id"
        assert 'name' in company, "Company missing name"
        assert 'rank' in company, "Company missing rank"
        assert 'company_score' in company, "Company missing company_score"
        
        print(f"✓ Fetched incentive: {incentive_data['title']}")
        print(f"  Companies: {len(incentive_data['matched_companies'])}")
    
    service.close()
    print("✓ get_incentive_with_companies test passed")


def test_get_incentive_not_found():
    """Test fetching a non-existent incentive"""
    print("\n[TEST 3] Testing get_incentive_with_companies with invalid ID...")
    
    service = DatabaseService()
    result = service.get_incentive_with_companies("NONEXISTENT_ID_12345")
    
    assert result is None, "Expected None for non-existent incentive"
    
    service.close()
    print("✓ Non-existent incentive test passed")


def test_get_company_with_incentives():
    """Test fetching a company with its eligible incentives"""
    print("\n[TEST 4] Testing get_company_with_incentives...")
    
    service = DatabaseService()
    
    # First, find a company that has eligible incentives
    conn = service.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT company_id 
        FROM companies 
        WHERE eligible_incentives IS NOT NULL 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    cursor.close()
    service.return_connection(conn)
    
    if not result:
        print("⚠ No companies with eligible incentives found - skipping test")
        service.close()
        return
    
    company_id = result[0]
    
    # Fetch the company
    company_data = service.get_company_with_incentives(company_id)
    
    # Verify structure
    assert company_data is not None, "Company data is None"
    assert 'company_id' in company_data, "Missing company_id"
    assert 'company_name' in company_data, "Missing company_name"
    assert 'eligible_incentives' in company_data, "Missing eligible_incentives"
    assert isinstance(company_data['eligible_incentives'], list), "eligible_incentives is not a list"
    
    # If there are incentives, verify their structure
    if company_data['eligible_incentives']:
        incentive = company_data['eligible_incentives'][0]
        assert 'incentive_id' in incentive, "Incentive missing incentive_id"
        assert 'title' in incentive, "Incentive missing title"
        assert 'rank' in incentive, "Incentive missing rank"
        assert 'company_score' in incentive, "Incentive missing company_score"
        
        print(f"✓ Fetched company: {company_data['company_name']}")
        print(f"  Incentives: {len(company_data['eligible_incentives'])}")
    
    service.close()
    print("✓ get_company_with_incentives test passed")


def test_get_company_not_found():
    """Test fetching a non-existent company"""
    print("\n[TEST 5] Testing get_company_with_incentives with invalid ID...")
    
    service = DatabaseService()
    result = service.get_company_with_incentives(999999999)
    
    assert result is None, "Expected None for non-existent company"
    
    service.close()
    print("✓ Non-existent company test passed")


def main():
    """Run all tests"""
    print("=" * 70)
    print("DATABASE SERVICE TESTS")
    print("=" * 70)
    
    try:
        test_database_connection()
        test_get_incentive_with_companies()
        test_get_incentive_not_found()
        test_get_company_with_incentives()
        test_get_company_not_found()
        
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
