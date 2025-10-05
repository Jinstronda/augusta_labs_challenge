"""
Batch Process All Incentives

This script processes all incentives in the database sequentially, finding the top 5 
matching companies for each one using the enhanced matching system with geographic filtering.

Results are saved directly to the incentives.top_5_companies column as JSON.

Usage:
    python batch_process_all_incentives.py
    python batch_process_all_incentives.py --start-from 100  # Resume from incentive 100
    python batch_process_all_incentives.py --limit 50       # Process only 50 incentives
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

# Load environment variables BEFORE importing
load_dotenv('config.env')

# Import our enhanced matching system
from enhanced_incentive_matching import EnhancedMatchingPipeline, DatabaseManager

# Database configuration
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def get_all_processable_incentives(start_from=None, limit=None):
    """
    Get all incentives that can be processed (have required fields).
    
    Args:
        start_from: Skip incentives before this ID (for resuming)
        limit: Maximum number of incentives to process
        
    Returns:
        List of incentive dictionaries
    """
    print(f"\n[BATCH] Loading processable incentives from database...")
    
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    
    # Build query with optional filters
    query = """
        SELECT incentive_id, title, sector, geo_requirement, 
               ai_description, eligible_actions, funding_rate, investment_eur,
               top_5_companies
        FROM incentives
        WHERE sector IS NOT NULL 
        AND eligible_actions IS NOT NULL 
        AND geo_requirement IS NOT NULL
        AND ai_description IS NOT NULL
    """
    
    params = []
    
    if start_from:
        query += " AND incentive_id >= %s"
        params.append(start_from)
    
    query += " ORDER BY incentive_id"
    
    if limit:
        query += " LIMIT %s"
        params.append(limit)
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    incentives = []
    already_processed = 0
    
    for row in results:
        incentive = {
            'id': row[0], 'title': row[1], 'sector': row[2],
            'geo_requirement': row[3], 'ai_description': row[4],
            'eligible_actions': row[5], 'funding_rate': row[6], 
            'investment_eur': row[7],
            'already_processed': row[8] is not None  # Has top_5_companies data
        }
        
        if incentive['already_processed']:
            already_processed += 1
        
        incentives.append(incentive)
    
    cursor.close()
    conn.close()
    
    print(f"[BATCH] Found {len(incentives)} processable incentives")
    print(f"[BATCH] Already processed: {already_processed}")
    print(f"[BATCH] Remaining to process: {len(incentives) - already_processed}")
    
    return incentives


def process_single_incentive(pipeline, incentive, current_num, total_num):
    """
    Process a single incentive and return success status.
    
    Args:
        pipeline: EnhancedMatchingPipeline instance
        incentive: Incentive dictionary
        current_num: Current incentive number (for progress)
        total_num: Total number of incentives
        
    Returns:
        bool: True if successful, False if failed
    """
    print(f"\n{'='*80}")
    print(f"PROCESSING INCENTIVE {current_num}/{total_num}")
    print(f"ID: {incentive['id']}")
    print(f"Title: {incentive['title'][:60]}...")
    print(f"Geographic Requirement: {incentive['geo_requirement']}")
    print(f"{'='*80}")
    
    try:
        start_time = time.time()
        
        # Process the incentive
        result = pipeline.find_matching_companies(incentive)
        
        processing_time = time.time() - start_time
        
        print(f"\n[SUCCESS] Incentive {incentive['id']} processed successfully!")
        print(f"[RESULT] Found {len(result.companies)} matching companies")
        print(f"[TIMING] Processing time: {processing_time:.1f} seconds")
        
        if result.companies:
            print(f"[TOP MATCH] {result.companies[0]['name']} (score: {result.companies[0].get('rerank_score', 0):.4f})")
        
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Failed to process incentive {incentive['id']}: {str(e)}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        return False


def main():
    """
    Main batch processing function.
    
    Processes all incentives sequentially with progress tracking,
    error handling, and resume capability.
    """
    print("="*80)
    print("BATCH PROCESSING ALL INCENTIVES")
    print("Enhanced Matching System with Geographic Filtering")
    print("="*80)
    
    # Parse command line arguments
    start_from = None
    limit = None
    skip_processed = True
    
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--start-from" and i + 1 < len(sys.argv) - 1:
            start_from = sys.argv[i + 2]
        elif arg == "--limit" and i + 1 < len(sys.argv) - 1:
            limit = int(sys.argv[i + 2])
        elif arg == "--reprocess-all":
            skip_processed = False
    
    print(f"[CONFIG] Start from: {start_from or 'beginning'}")
    print(f"[CONFIG] Limit: {limit or 'no limit'}")
    print(f"[CONFIG] Skip already processed: {skip_processed}")
    
    # Get all processable incentives
    incentives = get_all_processable_incentives(start_from, limit)
    
    if not incentives:
        print("[ERROR] No processable incentives found!")
        return
    
    # Filter out already processed if requested
    if skip_processed:
        incentives = [i for i in incentives if not i['already_processed']]
        print(f"[BATCH] After filtering already processed: {len(incentives)} incentives")
    
    if not incentives:
        print("[INFO] All incentives already processed!")
        return
    
    # Initialize the enhanced matching pipeline
    print(f"\n[INIT] Initializing enhanced matching pipeline...")
    pipeline = EnhancedMatchingPipeline()
    
    # Process all incentives
    start_time = time.time()
    successful = 0
    failed = 0
    
    print(f"\n[BATCH] Starting batch processing of {len(incentives)} incentives...")
    print(f"[BATCH] Estimated time: {len(incentives) * 2:.0f} minutes")
    
    for i, incentive in enumerate(incentives, 1):
        try:
            success = process_single_incentive(pipeline, incentive, i, len(incentives))
            
            if success:
                successful += 1
            else:
                failed += 1
            
            # Progress update every 10 incentives
            if i % 10 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (len(incentives) - i) * avg_time
                
                print(f"\n[PROGRESS] {i}/{len(incentives)} completed")
                print(f"[PROGRESS] Success rate: {successful}/{i} ({successful/i*100:.1f}%)")
                print(f"[PROGRESS] Average time per incentive: {avg_time:.1f} seconds")
                print(f"[PROGRESS] Estimated time remaining: {remaining/60:.1f} minutes")
        
        except KeyboardInterrupt:
            print(f"\n[INTERRUPTED] Batch processing interrupted by user")
            print(f"[PROGRESS] Processed {i-1}/{len(incentives)} incentives")
            break
        
        except Exception as e:
            print(f"\n[ERROR] Unexpected error processing incentive {incentive['id']}: {e}")
            failed += 1
            continue
    
    # Final summary
    total_time = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"BATCH PROCESSING COMPLETED")
    print(f"{'='*80}")
    print(f"Total incentives processed: {successful + failed}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {successful/(successful+failed)*100:.1f}%")
    print(f"Total processing time: {total_time/60:.1f} minutes")
    print(f"Average time per incentive: {total_time/(successful+failed):.1f} seconds")
    
    if successful > 0:
        print(f"\n[SUCCESS] {successful} incentives now have matching companies!")
        print(f"[INFO] Results saved to incentives.top_5_companies column")
        print(f"[INFO] You can query results with:")
        print(f"  SELECT incentive_id, title, top_5_companies FROM incentives WHERE top_5_companies IS NOT NULL;")
    
    if failed > 0:
        print(f"\n[WARNING] {failed} incentives failed to process")
        print(f"[INFO] You can retry failed incentives by running the script again")
    
    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()