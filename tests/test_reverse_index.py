"""
Test the reverse index functionality

Verifies that:
1. Companies have eligible_incentives column populated
2. Data structure matches specification
3. Incentives are sorted by company_score
4. Top 5 limit is enforced
"""

import os
import json
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Database configuration
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )


def test_reverse_index_exists():
    """Test that eligible_incentives column exists"""
    print("\n[TEST 1] Checking if eligible_incentives column exists...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'companies' 
            AND column_name = 'eligible_incentives'
        """)
        
        result = cursor.fetchone()
        
        assert result is not None, "eligible_incentives column does not exist"
        assert result[1] == 'jsonb', f"Expected JSONB type, got {result[1]}"
        
        print("✓ eligible_incentives column exists with JSONB type")


def test_data_structure():
    """Test that data structure matches specification"""
    print("\n[TEST 2] Checking data structure...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT company_id, company_name, eligible_incentives
            FROM companies
            WHERE eligible_incentives IS NOT NULL
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        
        assert result is not None, "No companies with eligible_incentives found"
        
        company_id, company_name, incentives_json = result
        incentives = json.loads(incentives_json) if isinstance(incentives_json, str) else incentives_json
        
        assert isinstance(incentives, list), "eligible_incentives should be a list"
        assert len(incentives) > 0, "eligible_incentives should not be empty"
        
        # Check first incentive structure
        incentive = incentives[0]
        required_fields = ['incentive_id', 'title', 'rank', 'company_score']
        
        for field in required_fields:
            assert field in incentive, f"Missing required field: {field}"
        
        print(f"✓ Data structure is correct")
        print(f"  Sample: {company_name} has {len(incentives)} eligible incentives")


def test_sorting_by_score():
    """Test that incentives are sorted by company_score descending"""
    print("\n[TEST 3] Checking if incentives are sorted by score...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT company_id, company_name, eligible_incentives
            FROM companies
            WHERE eligible_incentives IS NOT NULL
            AND jsonb_array_length(eligible_incentives) > 1
            LIMIT 5
        """)
        
        results = cursor.fetchall()
        
        assert len(results) > 0, "No companies with multiple incentives found"
        
        all_sorted = True
        for company_id, company_name, incentives_json in results:
            incentives = json.loads(incentives_json) if isinstance(incentives_json, str) else incentives_json
            
            scores = [inc['company_score'] for inc in incentives]
            
            # Check if sorted descending
            is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
            
            if not is_sorted:
                print(f"✗ Company {company_name} incentives not sorted: {scores}")
                all_sorted = False
            else:
                print(f"  ✓ {company_name}: {len(incentives)} incentives sorted correctly")
        
        assert all_sorted, "Some companies have unsorted incentives"
        print("✓ All incentives are sorted by company_score descending")


def test_top_5_limit():
    """Test that each company has at most 5 incentives"""
    print("\n[TEST 4] Checking top 5 limit...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT company_id, company_name, jsonb_array_length(eligible_incentives) as count
            FROM companies
            WHERE eligible_incentives IS NOT NULL
            ORDER BY count DESC
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        
        max_count = 0
        for company_id, company_name, count in results:
            print(f"  {company_name}: {count} incentives")
            max_count = max(max_count, count)
        
        assert max_count <= 5, f"Found company with {max_count} incentives (max should be 5)"
        print(f"✓ All companies have at most 5 incentives (max found: {max_count})")


def test_coverage():
    """Test coverage statistics"""
    print("\n[TEST 5] Checking coverage statistics...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Total companies
        cursor.execute("SELECT COUNT(*) FROM companies")
        total_companies = cursor.fetchone()[0]
        
        # Companies with eligible_incentives
        cursor.execute("""
            SELECT COUNT(*) 
            FROM companies 
            WHERE eligible_incentives IS NOT NULL
        """)
        with_incentives = cursor.fetchone()[0]
        
        # Total incentives processed
        cursor.execute("""
            SELECT COUNT(*) 
            FROM incentives 
            WHERE top_5_companies_scored IS NOT NULL
        """)
        incentives_processed = cursor.fetchone()[0]
        
        print(f"  Total companies: {total_companies:,}")
        print(f"  Companies with eligible_incentives: {with_incentives:,}")
        print(f"  Coverage: {with_incentives/total_companies*100:.2f}%")
        print(f"  Incentives processed: {incentives_processed:,}")
        
        assert with_incentives > 0, "No companies have eligible_incentives"
        assert incentives_processed > 0, "No incentives have been processed"
        
        print("✓ Coverage statistics look good")


def main():
    """Run all tests"""
    print("=" * 70)
    print("REVERSE INDEX TESTS")
    print("=" * 70)
    
    try:
        test_reverse_index_exists()
        test_data_structure()
        test_sorting_by_score()
        test_top_5_limit()
        test_coverage()
        
        print("\n" + "=" * 70)
        print("✓ ALL TESTS PASSED")
        print("=" * 70)
        
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
