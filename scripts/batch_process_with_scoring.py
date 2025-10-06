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
import json
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

# Skipped incentives tracking file
SKIPPED_FILE = os.path.join(PROJECT_ROOT, 'data', 'skipped_incentives.json')


def load_skipped_ids():
    """Load the set of previously skipped incentive IDs."""
    if os.path.exists(SKIPPED_FILE):
        try:
            with open(SKIPPED_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('skipped_ids', []))
        except Exception as e:
            print(f"[WARNING] Could not load skipped IDs: {e}")
    return set()


def save_skipped_ids(skipped_ids):
    """Save the set of skipped incentive IDs."""
    try:
        os.makedirs(os.path.dirname(SKIPPED_FILE), exist_ok=True)
        with open(SKIPPED_FILE, 'w') as f:
            json.dump({
                'skipped_ids': list(skipped_ids),
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
    except Exception as e:
        print(f"[WARNING] Could not save skipped IDs: {e}")


def remove_from_skipped(incentive_id):
    """Remove an incentive ID from the skipped list (when it succeeds)."""
    skipped_ids = load_skipped_ids()
    if incentive_id in skipped_ids:
        skipped_ids.remove(incentive_id)
        save_skipped_ids(skipped_ids)
        return True
    return False


def get_unscored_incentives(limit=None, include_skipped=False):
    """
    Get all incentives that don't have scored results yet.
    Previously skipped incentives are moved to the end or excluded entirely.
    
    Args:
        limit: Maximum number of incentives to process
        include_skipped: If False, exclude previously skipped incentives entirely
        
    Returns:
        List of incentive dictionaries
    """
    print(f"\n[BATCH] Loading incentives without scored results...")
    
    # Load previously skipped IDs
    skipped_ids = load_skipped_ids()
    if skipped_ids:
        if include_skipped:
            print(f"[BATCH] Found {len(skipped_ids)} previously skipped incentives (will process last)")
        else:
            print(f"[BATCH] Found {len(skipped_ids)} previously skipped incentives (will be excluded)")
    
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
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    # Separate into priority (not skipped) and low-priority (previously skipped)
    priority_incentives = []
    skipped_incentives = []
    
    for row in results:
        incentive = {
            'id': row[0],
            'title': row[1],
            'sector': row[2],
            'geo_requirement': row[3],
            'ai_description': row[4],
            'eligible_actions': row[5]
        }
        
        if row[0] in skipped_ids:
            skipped_incentives.append(incentive)
        else:
            priority_incentives.append(incentive)
    
    cursor.close()
    conn.close()
    
    # Combine based on include_skipped flag
    if include_skipped:
        # Priority first, then previously skipped
        incentives = priority_incentives + skipped_incentives
        print(f"[BATCH] Found {len(incentives)} incentives to process")
        print(f"[BATCH]   - {len(priority_incentives)} new/priority")
        print(f"[BATCH]   - {len(skipped_incentives)} previously skipped")
    else:
        # Only priority incentives
        incentives = priority_incentives
        print(f"[BATCH] Found {len(incentives)} incentives to process (excluding {len(skipped_incentives)} skipped)")
    
    # Apply limit if specified
    if limit:
        incentives = incentives[:limit]
    
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
    
    # Load persistent skipped IDs
    persistent_skipped = load_skipped_ids()
    
    successful = 0
    failed = 0
    skipped = 0
    
    # Track skipped incentives to retry at the end
    skipped_queue = []
    
    start_time = time.time()
    
    # Process main queue
    total_to_process = len(incentives)
    processed_count = 0
    
    for i, incentive in enumerate(incentives, 1):
        processed_count += 1
        print(f"\n{'='*80}")
        print(f"PROCESSING INCENTIVE {processed_count}/{total_to_process}")
        print(f"{'='*80}")
        print(f"ID: {incentive['id']}")
        print(f"Title: {incentive['title'][:70]}...")
        print(f"{'='*80}")
        
        try:
            # Process incentive
            result = pipeline.find_matching_companies(incentive, max_candidates=max_candidates)
            
            if result and len(result.companies) > 0:
                successful += 1
                # Remove from persistent skipped list if it was there
                if incentive['id'] in persistent_skipped:
                    remove_from_skipped(incentive['id'])
                    print(f"\n✅ SUCCESS: Found {len(result.companies)} companies (removed from skip list)")
                else:
                    print(f"\n✅ SUCCESS: Found {len(result.companies)} companies")
                print(f"   Processing time: {result.processing_time:.2f}s")
            else:
                skipped += 1
                skipped_queue.append(incentive)
                # Add to persistent skipped list
                persistent_skipped.add(incentive['id'])
                save_skipped_ids(persistent_skipped)
                print(f"\n⚠️  SKIPPED: No eligible companies found (saved to skip list)")
                
        except Exception as e:
            failed += 1
            print(f"\n❌ FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
        
        # Progress update
        elapsed = time.time() - start_time
        avg_time = elapsed / processed_count
        remaining = (total_to_process - processed_count) * avg_time
        
        print(f"\n[PROGRESS] {processed_count}/{total_to_process} completed")
        print(f"[PROGRESS] Success: {successful}, Failed: {failed}, Skipped: {skipped}")
        print(f"[PROGRESS] Elapsed: {elapsed/60:.1f}m, Est. remaining: {remaining/60:.1f}m")
    
    # Process skipped queue if there are any
    if skipped_queue:
        print(f"\n{'='*80}")
        print(f"PROCESSING SKIPPED QUEUE ({len(skipped_queue)} incentives)")
        print(f"{'='*80}")
        
        for i, incentive in enumerate(skipped_queue, 1):
            processed_count += 1
            print(f"\n{'='*80}")
            print(f"RETRY SKIPPED INCENTIVE {i}/{len(skipped_queue)}")
            print(f"{'='*80}")
            print(f"ID: {incentive['id']}")
            print(f"Title: {incentive['title'][:70]}...")
            print(f"{'='*80}")
            
            try:
                # Process incentive
                result = pipeline.find_matching_companies(incentive, max_candidates=max_candidates)
                
                if result and len(result.companies) > 0:
                    successful += 1
                    skipped -= 1  # Remove from skipped count
                    # Remove from persistent skipped list
                    remove_from_skipped(incentive['id'])
                    print(f"\n✅ SUCCESS: Found {len(result.companies)} companies (removed from skip list)")
                    print(f"   Processing time: {result.processing_time:.2f}s")
                else:
                    print(f"\n⚠️  STILL SKIPPED: No eligible companies found (remains in skip list)")
                    
            except Exception as e:
                failed += 1
                skipped -= 1  # Remove from skipped, add to failed
                print(f"\n❌ FAILED: {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Progress update
            elapsed = time.time() - start_time
            avg_time = elapsed / processed_count
            
            print(f"\n[PROGRESS] Retry {i}/{len(skipped_queue)} completed")
            print(f"[PROGRESS] Success: {successful}, Failed: {failed}, Skipped: {skipped}")
            print(f"[PROGRESS] Total elapsed: {elapsed/60:.1f}m")
    
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
    include_skipped = False
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--limit' and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
            print(f"[INFO] Processing limit: {limit} incentives")
            i += 2
        elif sys.argv[i] == '--retry-skipped':
            include_skipped = True
            print(f"[INFO] Will retry previously skipped incentives")
            i += 1
        else:
            i += 1
    
    # Get unscored incentives
    incentives = get_unscored_incentives(limit=limit, include_skipped=include_skipped)
    
    if not incentives:
        print("\n✅ All incentives already have scored results!")
        skipped_ids = load_skipped_ids()
        if skipped_ids:
            print(f"\n[INFO] There are {len(skipped_ids)} skipped incentives.")
            print(f"[INFO] Run with --retry-skipped to process them.")
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
