"""
Unit tests for DatabaseService

Tests database operations with a real database connection.
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.database import DatabaseService


@pytest.fixture
def db_service():
    """Create DatabaseService instance for testing"""
    service = DatabaseService()
    yield service
    service.close()


def test_database_connection(db_service):
    """Test that database connection pool is initialized"""
    assert db_service.connection_pool is not None
    
    # Test getting and returning a connection
    conn = db_service.get_connection()
    assert conn is not None
    db_service.return_connection(conn)


def test_get_incentive_with_companies(db_service):
    """Test fetching an incentive with its matched companies"""
    # First, find an incentive that has scored companies
    conn = db_service.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT incentive_id 
        FROM incentives 
        WHERE top_5_companies_scored IS NOT NULL 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    cursor.close()
    db_service.return_connection(conn)
    
    if not result:
        pytest.skip("No incentives with scored companies found in database")
    
    incentive_id = result[0]
    
    # Fetch the incentive
    incentive_data = db_service.get_incentive_with_companies(incentive_id)
    
    # Verify structure
    assert incentive_data is not None
    assert 'incentive_id' in incentive_data
    assert 'title' in incentive_data
    assert 'matched_companies' in incentive_data
    assert isinstance(incentive_data['matched_companies'], list)
    
    # If there are companies, verify their structure
    if incentive_data['matched_companies']:
        company = incentive_data['matched_companies'][0]
        assert 'id' in company
        assert 'name' in company
        assert 'rank' in company
        assert 'company_score' in company
        
        print(f"\n✓ Fetched incentive: {incentive_data['title']}")
        print(f"  Companies: {len(incentive_data['matched_companies'])}")


def test_get_incentive_not_found(db_service):
    """Test fetching a non-existent incentive"""
    result = db_service.get_incentive_with_companies("NONEXISTENT_ID_12345")
    assert result is None


def test_get_company_with_incentives(db_service):
    """Test fetching a company with its eligible incentives"""
    # First, find a company that has eligible incentives
    conn = db_service.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT company_id 
        FROM companies 
        WHERE eligible_incentives IS NOT NULL 
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    cursor.close()
    db_service.return_connection(conn)
    
    if not result:
        pytest.skip("No companies with eligible incentives found in database")
    
    company_id = result[0]
    
    # Fetch the company
    company_data = db_service.get_company_with_incentives(company_id)
    
    # Verify structure
    assert company_data is not None
    assert 'company_id' in company_data
    assert 'company_name' in company_data
    assert 'eligible_incentives' in company_data
    assert isinstance(company_data['eligible_incentives'], list)
    
    # If there are incentives, verify their structure
    if company_data['eligible_incentives']:
        incentive = company_data['eligible_incentives'][0]
        assert 'incentive_id' in incentive
        assert 'title' in incentive
        assert 'rank' in incentive
        assert 'company_score' in incentive
        
        print(f"\n✓ Fetched company: {company_data['company_name']}")
        print(f"  Incentives: {len(company_data['eligible_incentives'])}")


def test_get_company_not_found(db_service):
    """Test fetching a non-existent company"""
    result = db_service.get_company_with_incentives(999999999)
    assert result is None


def test_connection_pool_reuse(db_service):
    """Test that connections are properly reused from the pool"""
    # Get multiple connections
    conn1 = db_service.get_connection()
    db_service.return_connection(conn1)
    
    conn2 = db_service.get_connection()
    db_service.return_connection(conn2)
    
    # Connections should be reused (same object)
    assert conn1 is conn2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
