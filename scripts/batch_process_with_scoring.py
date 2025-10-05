"""
Batch Process All Incentives with Company Scoring

This script processes all incentives that don't have scored results yet,
finding the top 5 matching companies using both semantic matching and
the Universal Company Match Formula.

Results are saved to:
- incentives.top_5_companies (semantic ranking)
- incentives.top_5_companies_scored (company score ranking)

Usage:
    python batch_process_with_scoring.py
    python batch_process_with_scoring.py --limit 10  # Process only 10 incentives
"""

import os
import sys
import time
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Get the project root directory (parent of scripts/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

# Change to project root to ensure relative paths work
os.chdir(PROJECT_ROOT)

# Load environment variables BEFORE importing (so enhanced_incentive_matching can use them)
load_dotenv('config.env')

# Import our enhanced matching system
from enhanced_incentive_matching import EnhancedMatchingPipeline

# Database configuration
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_unscored_incentives(limit=None):
    """
    Get all incentives that don't have scored results yet.
    
    Args:
        limit: Maximum number of incentives to process
        
    Returns:
        List of incentive dictionaries
    """
    print(f"\n[BATCH] Loading incentives without scored results...")
    
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    
    # Build query
    query = """
        SELECT incentive_id, title, sector, geo_requirement, 
               ai_description, eligible_actions
        FROM incentives
        WHERE sector IS NOT NULL 
        AND eligible_actions IS NOT NULL 
        AND geo_requirement IS NOT NULL
        AND ai_description IS NOT NULL
        AND top_5_companies_scored IS NULL
        ORDER BY incentive_id
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    incentives = []
    for row in results:
        incentive = {
            'id': row[0],
            'title': row[1],
            'sector': row[2],
            'geo_requirement': row[3],
            'ai_description': row[4],
            'eligible_actions': row[5]
        }
        incentives.append(incentive)
    
    cursor.close()
    conn.close()
    
    print(f"[BATCH] Found {len(incentives)} incentives to process")
    return incentives


def process_batch(incentives, max_candidates=50):
    """
    Process a batch of incentives.
    
    Args:
        incentives: List of incentive dictionaries
        max_candidates: Maximum candidates to search per incentive
        
    Returns:
        Tuple of (successful, failed, skipped) counts
    """
    print(f"\n{'='*80}")
    print(f"BATCH PROCESSING WITH COMPANY SCORING")
    print(f"{'='*80}")
    print(f"Total incentives to process: {len(incentives)}")
    print(f"Max candidates per incentive: {max_candidates}")
    print(f"{'='*80}\n")
    
    # Initialize pipeline once
    print("[INIT] Initializing enhanced matching pipeline...")
    pipeline = EnhancedMatchingPipeline()
    
    successful = 0
    failed = 0
    skipped = 0
    
    start_time = time.time()
    
    for i, incentive in enumerate(incentives, 1):
        print(f"\n{'='*80}")
        print(f"PROCESSING INCENTIVE {i}/{len(incentives)}")
        print(f"{'='*80}")
        print(f"ID: {incentive['id']}")
        print(f"Title: {incentive['title'][:70]}...")
        print(f"{'='*80}")
        
        try:
            # Process incentive
            result = pipeline.find_matching_companies(incentive, max_candidates=max_candidates)
            
            if result and len(result.companies) > 0:
                successful += 1
                print(f"\n✅ SUCCESS: Found {len(result.companies)} companies")
                print(f"   Processing time: {result.processing_time:.2f}s")
            else:
                skipped += 1
                print(f"\n⚠️  SKIPPED: No eligible companies found")
                
        except Exception as e:
            failed += 1
            print(f"\n❌ FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Progress update
        elapsed = time.time() - start_time
        avg_time = elapsed / i
        remaining = (len(incentives) - i) * avg_time
        
        print(f"\n[PROGRESS] {i}/{len(incentives)} completed")
        print(f"[PROGRESS] Success: {successful}, Failed: {failed}, Skipped: {skipped}")
        print(f"[PROGRESS] Elapsed: {elapsed/60:.1f}m, Est. remaining: {remaining/60:.1f}m")
    
    total_time = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"BATCH PROCESSING COMPLETE")
    print(f"{'='*80}")
    print(f"Total processed: {len(incentives)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Average time per incentive: {total_time/len(incentives):.1f} seconds")
    print(f"{'='*80}")
    
    if successful > 0:
        print(f"\n✅ {successful} incentives now have scored results!")
        print(f"[INFO] Results saved to:")
        print(f"  - incentives.top_5_companies (semantic ranking)")
        print(f"  - incentives.top_5_companies_scored (company score ranking)")
    
    if failed > 0:
        print(f"\n⚠️  {failed} incentives failed to process")
        print(f"[INFO] Check logs above for error details")
    
    return successful, failed, skipped


def main():
    """Main entry point."""
    # Parse command line arguments
    limit = None
    if len(sys.argv) > 1:
        if sys.argv[1] == '--limit' and len(sys.argv) > 2:
            limit = int(sys.argv[2])
            print(f"[INFO] Processing limit: {limit} incentives")
    
    # Get unscored incentives
    incentives = get_unscored_incentives(limit=limit)
    
    if not incentives:
        print("\n✅ All incentives already have scored results!")
        return
    
    # Process batch
    successful, failed, skipped = process_batch(incentives, max_candidates=50)
    
    # Exit with appropriate code
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
