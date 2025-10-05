"""
Test the enhanced matching pipeline with company scoring.
"""
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Get the project root directory (parent of tests/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# Change to project root to ensure relative paths work
os.chdir(PROJECT_ROOT)

# Load environment variables BEFORE importing
load_dotenv('config.env')

from enhanced_incentive_matching import EnhancedMatchingPipeline

# Database configuration
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_test_incentive():
    """Get a test incentive with all required fields."""
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT incentive_id, title, sector, geo_requirement, 
               ai_description, eligible_actions
        FROM incentives
        WHERE sector IS NOT NULL 
        AND eligible_actions IS NOT NULL 
        AND geo_requirement IS NOT NULL
        AND ai_description IS NOT NULL
        ORDER BY RANDOM() LIMIT 1
    """)
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not result:
        print("[ERROR] No incentives found!")
        return None
    
    incentive = {
        'id': result[0],
        'title': result[1],
        'sector': result[2],
        'geo_requirement': result[3],
        'ai_description': result[4],
        'eligible_actions': result[5]
    }
    
    print(f"\n{'='*80}")
    print(f"TEST INCENTIVE")
    print(f"{'='*80}")
    print(f"ID: {incentive['id']}")
    print(f"Title: {incentive['title']}")
    print(f"Sector: {incentive['sector']}")
    print(f"Geographic Requirement: {incentive['geo_requirement']}")
    print(f"{'='*80}\n")
    
    return incentive


def main():
    print("\n" + "="*80)
    print("TESTING ENHANCED MATCHING WITH COMPANY SCORING")
    print("="*80)
    
    # Get test incentive
    incentive = get_test_incentive()
    if not incentive:
        return
    
    # Initialize pipeline
    print("\n[INIT] Initializing enhanced matching pipeline...")
    pipeline = EnhancedMatchingPipeline()
    
    # Run matching
    print("\n[MATCHING] Finding matching companies...")
    result = pipeline.find_matching_companies(incentive, max_candidates=30)
    
    # Display results
    print(f"\n{'='*80}")
    print(f"RESULTS")
    print(f"{'='*80}")
    print(f"Total candidates searched: {result.total_candidates_searched}")
    print(f"Geographic eligible: {result.geographic_eligible_count}")
    print(f"Final companies: {len(result.companies)}")
    print(f"Processing time: {result.processing_time:.2f} seconds")
    
    print(f"\n{'='*80}")
    print(f"TOP COMPANIES (Semantic Ranking)")
    print(f"{'='*80}")
    for i, company in enumerate(result.companies[:5], 1):
        print(f"\n{i}. {company['name']}")
        print(f"   Semantic Score: {company.get('rerank_score', 0):.4f}")
        if 'company_score' in company:
            print(f"   Company Score: {company.get('company_score', 0):.4f}")
    
    print(f"\n{'='*80}")
    print(f"✅ TEST COMPLETED SUCCESSFULLY!")
    print(f"{'='*80}")
    print(f"\nResults saved to:")
    print(f"  - incentives.top_5_companies (semantic ranking)")
    print(f"  - incentives.top_5_companies_scored (company score ranking)")


if __name__ == "__main__":
    main()
