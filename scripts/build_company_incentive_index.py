"""
Build reverse index: company_id → eligible incentives

This script runs after batch processing completes and builds a JSONB column
in the companies table containing each company's top 5 eligible incentives
ranked by score.

The reverse index enables fast company queries without scanning all incentives.

Algorithm:
1. Query all incentives with top_5_companies_scored
2. For each incentive:
   - Parse top_5_companies_scored JSON
   - Extract companies with their ranks and scores
   - Add to company→incentives mapping
3. For each company:
   - Sort incentives by company_score (descending)
   - Keep top 5 incentives
   - Save to companies.eligible_incentives as JSONB

Usage:
    conda activate turing0.1
    python scripts/build_company_incentive_index.py
"""

import os
import json
import psycopg2
from collections import defaultdict
from datetime import datetime
from typing import Dict, List
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


def ensure_schema():
    """
    Add eligible_incentives column to companies table if it doesn't exist.
    
    This column stores a JSONB array of the top 5 incentives for each company.
    """
    print("[SCHEMA] Ensuring eligible_incentives column exists...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Add eligible_incentives column
        cursor.execute("""
            ALTER TABLE companies 
            ADD COLUMN IF NOT EXISTS eligible_incentives JSONB
        """)
        
        # Create GIN index for faster JSONB queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_companies_eligible_incentives 
            ON companies USING GIN (eligible_incentives)
        """)
        
        conn.commit()
        print("[SCHEMA] ✓ eligible_incentives column ready")


def fetch_all_incentives_with_scores() -> List[Dict]:
    """
    Fetch all incentives that have top_5_companies_scored data.
    
    Returns:
        List of dicts with incentive_id, title, and top_5_companies_scored JSON
    """
    print("[FETCH] Querying incentives with scored companies...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT incentive_id, title, top_5_companies_scored
            FROM incentives
            WHERE top_5_companies_scored IS NOT NULL
            ORDER BY incentive_id
        """)
        
        results = cursor.fetchall()
        
        incentives = []
        for row in results:
            incentive_id, title, scored_json = row
            
            # Parse JSON
            try:
                scored_data = json.loads(scored_json) if isinstance(scored_json, str) else scored_json
                incentives.append({
                    'incentive_id': incentive_id,
                    'title': title,
                    'scored_data': scored_data
                })
            except json.JSONDecodeError as e:
                print(f"[FETCH] ✗ Error parsing JSON for incentive {incentive_id}: {e}")
                continue
        
        print(f"[FETCH] ✓ Found {len(incentives)} incentives with scored companies")
        return incentives


def build_reverse_index(incentives: List[Dict]) -> Dict[int, List[Dict]]:
    """
    Build reverse index: company_id → list of incentives.
    
    Args:
        incentives: List of incentives with scored company data
        
    Returns:
        Dict mapping company_id to list of incentive matches
    """
    print("[INDEX] Building reverse index...")
    
    # company_id -> list of {incentive_id, title, rank, company_score}
    company_incentives = defaultdict(list)
    
    for incentive in incentives:
        incentive_id = incentive['incentive_id']
        title = incentive['title']
        scored_data = incentive['scored_data']
        
        # Extract companies from the scored data
        companies = scored_data.get('companies', [])
        
        for company in companies:
            company_id = company.get('id')
            rank = company.get('rank')
            company_score = company.get('company_score', 0)
            
            if company_id is None:
                print(f"[INDEX] ⚠ Skipping company with no ID in incentive {incentive_id}")
                continue
            
            # Add this incentive to the company's list
            company_incentives[company_id].append({
                'incentive_id': incentive_id,
                'title': title,
                'rank': rank,
                'company_score': company_score
            })
    
    print(f"[INDEX] ✓ Built index for {len(company_incentives)} companies")
    
    # Sort and keep top 5 for each company
    print("[INDEX] Sorting and limiting to top 5 per company...")
    
    for company_id in company_incentives:
        # Sort by company_score descending
        company_incentives[company_id].sort(
            key=lambda x: x['company_score'], 
            reverse=True
        )
        
        # Keep only top 5
        company_incentives[company_id] = company_incentives[company_id][:5]
    
    return dict(company_incentives)


def save_reverse_index(company_incentives: Dict[int, List[Dict]]):
    """
    Save reverse index to companies.eligible_incentives column.
    
    Args:
        company_incentives: Dict mapping company_id to list of incentive matches
    """
    print("[SAVE] Saving reverse index to database...")
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Update in batches for better performance
        batch_size = 100
        company_ids = list(company_incentives.keys())
        total = len(company_ids)
        
        for i in range(0, total, batch_size):
            batch_ids = company_ids[i:i+batch_size]
            
            for company_id in batch_ids:
                incentives_json = json.dumps(company_incentives[company_id])
                
                try:
                    cursor.execute("""
                        UPDATE companies 
                        SET eligible_incentives = %s
                        WHERE company_id = %s
                    """, (incentives_json, company_id))
                except Exception as e:
                    print(f"[SAVE] ✗ Error updating company {company_id}: {e}")
                    continue
            
            conn.commit()
            
            processed = min(i + batch_size, total)
            print(f"[SAVE] Progress: {processed}/{total} companies ({processed/total*100:.1f}%)")
        
        print(f"[SAVE] ✓ Saved reverse index for {total} companies")


def verify_results():
    """
    Verify the reverse index was created successfully.
    
    Shows statistics and sample data.
    """
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Count companies with eligible_incentives
        cursor.execute("""
            SELECT COUNT(*) 
            FROM companies 
            WHERE eligible_incentives IS NOT NULL
        """)
        with_incentives = cursor.fetchone()[0]
        
        # Total companies
        cursor.execute("SELECT COUNT(*) FROM companies")
        total_companies = cursor.fetchone()[0]
        
        print(f"\nCompanies with eligible_incentives: {with_incentives:,}/{total_companies:,}")
        print(f"Coverage: {with_incentives/total_companies*100:.1f}%")
        
        # Sample companies with their incentives
        cursor.execute("""
            SELECT company_id, company_name, eligible_incentives
            FROM companies
            WHERE eligible_incentives IS NOT NULL
            ORDER BY RANDOM()
            LIMIT 3
        """)
        
        samples = cursor.fetchall()
        
        print("\nSample Companies with Eligible Incentives:")
        print("-" * 70)
        
        for company_id, company_name, incentives_json in samples:
            incentives = json.loads(incentives_json) if isinstance(incentives_json, str) else incentives_json
            
            print(f"\n[{company_id}] {company_name}")
            print(f"  Eligible Incentives: {len(incentives)}")
            
            for idx, incentive in enumerate(incentives, 1):
                print(f"    {idx}. {incentive['title'][:60]}...")
                print(f"       Score: {incentive['company_score']:.3f} | Rank: {incentive['rank']}")
        
        print("\n" + "=" * 70)


def main():
    """Main execution function"""
    print("=" * 70)
    print("REVERSE INDEX BUILDER")
    print("Company → Eligible Incentives Mapping")
    print("=" * 70)
    
    start_time = datetime.now()
    
    try:
        # Step 1: Ensure schema
        ensure_schema()
        
        # Step 2: Fetch all incentives with scored companies
        incentives = fetch_all_incentives_with_scores()
        
        if not incentives:
            print("\n[ERROR] No incentives found with top_5_companies_scored data!")
            print("Please run batch processing first to generate scored results.")
            return
        
        # Step 3: Build reverse index
        company_incentives = build_reverse_index(incentives)
        
        # Step 4: Save to database
        save_reverse_index(company_incentives)
        
        # Step 5: Verify results
        verify_results()
        
        # Calculate processing time
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 70)
        print("✓ REVERSE INDEX BUILD COMPLETE")
        print("=" * 70)
        print(f"Processing time: {duration:.2f} seconds")
        print(f"Companies indexed: {len(company_incentives):,}")
        print(f"Incentives processed: {len(incentives):,}")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to build reverse index: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
