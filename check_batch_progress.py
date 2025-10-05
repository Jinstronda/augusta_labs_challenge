"""
Check Batch Processing Progress

This script checks the current status of batch processing by querying
the database for incentives with results.

Usage:
    python check_batch_progress.py
"""

import os
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


def check_progress():
    """Check the current batch processing progress."""
    
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    
    print("="*60)
    print("BATCH PROCESSING PROGRESS")
    print("="*60)
    
    # Total incentives
    cursor.execute("SELECT COUNT(*) FROM incentives")
    total_incentives = cursor.fetchone()[0]
    
    # Processable incentives (have required fields)
    cursor.execute("""
        SELECT COUNT(*) FROM incentives
        WHERE sector IS NOT NULL 
        AND eligible_actions IS NOT NULL 
        AND geo_requirement IS NOT NULL
    """)
    processable = cursor.fetchone()[0]
    
    # Processed incentives (have results)
    cursor.execute("""
        SELECT COUNT(*) FROM incentives
        WHERE top_5_companies IS NOT NULL
    """)
    processed = cursor.fetchone()[0]
    
    # Recent processing (last 24 hours)
    cursor.execute("""
        SELECT COUNT(*) FROM incentives
        WHERE top_5_companies IS NOT NULL
        AND top_5_companies->>'processed_at' > (NOW() - INTERVAL '24 hours')::text
    """)
    recent = cursor.fetchone()[0]
    
    print(f"Total incentives in database: {total_incentives:,}")
    print(f"Processable incentives: {processable:,}")
    print(f"Already processed: {processed:,}")
    print(f"Remaining to process: {processable - processed:,}")
    print(f"Progress: {processed/processable*100:.1f}%")
    print(f"Processed in last 24h: {recent:,}")
    
    # Show some sample results
    if processed > 0:
        print(f"\n{'-'*60}")
        print("SAMPLE PROCESSED INCENTIVES")
        print(f"{'-'*60}")
        
        cursor.execute("""
            SELECT incentive_id, title, 
                   JSON_ARRAY_LENGTH(top_5_companies->'companies') as company_count,
                   (top_5_companies->>'processing_time')::float as processing_time
            FROM incentives
            WHERE top_5_companies IS NOT NULL
            ORDER BY incentive_id
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            incentive_id, title, company_count, proc_time = row
            print(f"ID {incentive_id}: {title[:50]}...")
            print(f"  Companies found: {company_count}")
            print(f"  Processing time: {proc_time:.1f}s")
            print()
    
    # Show processing statistics
    if processed > 0:
        print(f"{'-'*60}")
        print("PROCESSING STATISTICS")
        print(f"{'-'*60}")
        
        cursor.execute("""
            SELECT 
                AVG((top_5_companies->>'processing_time')::float) as avg_time,
                MIN((top_5_companies->>'processing_time')::float) as min_time,
                MAX((top_5_companies->>'processing_time')::float) as max_time,
                AVG(JSON_ARRAY_LENGTH(top_5_companies->'companies')) as avg_companies
            FROM incentives
            WHERE top_5_companies IS NOT NULL
        """)
        
        stats = cursor.fetchone()
        if stats[0]:  # Check if we have data
            avg_time, min_time, max_time, avg_companies = stats
            print(f"Average processing time: {avg_time:.1f} seconds")
            print(f"Min/Max processing time: {min_time:.1f}s / {max_time:.1f}s")
            print(f"Average companies found: {avg_companies:.1f}")
            
            # Estimate remaining time
            remaining = processable - processed
            if remaining > 0:
                estimated_time = remaining * avg_time / 60
                print(f"Estimated time for remaining: {estimated_time:.1f} minutes")
    
    cursor.close()
    conn.close()
    
    print(f"\n{'='*60}")


if __name__ == "__main__":
    check_progress()