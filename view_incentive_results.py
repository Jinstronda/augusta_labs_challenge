"""
View Incentive Matching Results

This script allows you to view the matching results for specific incentives
or browse all processed incentives.

Usage:
    python view_incentive_results.py                    # Show all processed
    python view_incentive_results.py --incentive 2332   # Show specific incentive
    python view_incentive_results.py --latest 10        # Show latest 10 processed
"""

import os
import sys
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


def view_specific_incentive(incentive_id):
    """View results for a specific incentive."""
    
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT incentive_id, title, sector, geo_requirement, 
               eligible_actions, top_5_companies
        FROM incentives
        WHERE incentive_id = %s
    """, (incentive_id,))
    
    result = cursor.fetchone()
    
    if not result:
        print(f"[ERROR] Incentive {incentive_id} not found!")
        return
    
    incentive_id, title, sector, geo_req, actions, results_json = result
    
    print("="*80)
    print(f"INCENTIVE MATCHING RESULTS")
    print("="*80)
    print(f"ID: {incentive_id}")
    print(f"Title: {title}")
    print(f"Sector: {sector}")
    print(f"Geographic Requirement: {geo_req}")
    print(f"Eligible Actions: {actions[:100]}...")
    
    if not results_json:
        print(f"\n[INFO] This incentive has not been processed yet.")
        print(f"[INFO] Run: python batch_process_all_incentives.py --start-from {incentive_id} --limit 1")
        return
    
    results = json.loads(results_json) if isinstance(results_json, str) else results_json
    
    print(f"\n{'-'*80}")
    print(f"PROCESSING METADATA")
    print(f"{'-'*80}")
    print(f"Processed at: {results.get('processed_at', 'Unknown')}")
    print(f"Processing time: {results.get('processing_time', 0):.1f} seconds")
    print(f"Candidates searched: {results.get('total_candidates_searched', 0)}")
    print(f"Geographic eligible: {results.get('geographic_eligible_count', 0)}")
    
    companies = results.get('companies', [])
    
    print(f"\n{'-'*80}")
    print(f"TOP {len(companies)} MATCHING COMPANIES")
    print(f"{'-'*80}")
    
    for i, company in enumerate(companies, 1):
        print(f"\n{'='*80}")
        print(f"COMPANY #{i}")
        print(f"{'='*80}")
        print(f"Name: {company.get('name', 'N/A')}")
        print(f"Semantic Score: {company.get('semantic_score', 0):.4f}")
        print(f"CAE Classification: {company.get('cae_classification', 'N/A')}")
        print(f"Location: {company.get('location_address', 'N/A')}")
        print(f"Website: {company.get('website', 'N/A')}")
        
        activities = company.get('activities', '')
        if activities:
            print(f"Activities: {activities[:200]}...")
    
    cursor.close()
    conn.close()


def view_all_processed(limit=None):
    """View all processed incentives."""
    
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    
    query = """
        SELECT incentive_id, title, sector, geo_requirement,
               JSON_ARRAY_LENGTH(top_5_companies->'companies') as company_count,
               (top_5_companies->>'processing_time')::float as processing_time,
               top_5_companies->>'processed_at' as processed_at
        FROM incentives
        WHERE top_5_companies IS NOT NULL
        ORDER BY incentive_id
    """
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    if not results:
        print("[INFO] No processed incentives found!")
        return
    
    print("="*120)
    print(f"ALL PROCESSED INCENTIVES ({len(results)} total)")
    print("="*120)
    print(f"{'ID':<6} {'Title':<50} {'Sector':<25} {'Companies':<10} {'Time':<8} {'Processed'}")
    print("-"*120)
    
    for row in results:
        incentive_id, title, sector, geo_req, company_count, proc_time, processed_at = row
        
        # Truncate long fields
        title_short = title[:47] + "..." if len(title) > 50 else title
        sector_short = sector[:22] + "..." if len(sector) > 25 else sector
        
        # Format processed time
        if processed_at:
            processed_short = processed_at[:16]  # YYYY-MM-DD HH:MM
        else:
            processed_short = "Unknown"
        
        print(f"{incentive_id:<6} {title_short:<50} {sector_short:<25} {company_count:<10} {proc_time:<8.1f} {processed_short}")
    
    cursor.close()
    conn.close()
    
    print(f"\n[INFO] Use 'python view_incentive_results.py --incentive <ID>' to see detailed results")


def main():
    """Main function to handle command line arguments."""
    
    if len(sys.argv) == 1:
        # No arguments, show all processed
        view_all_processed()
        
    elif "--incentive" in sys.argv:
        # Show specific incentive
        try:
            idx = sys.argv.index("--incentive")
            incentive_id = sys.argv[idx + 1]
            view_specific_incentive(incentive_id)
        except (IndexError, ValueError):
            print("[ERROR] Please provide incentive ID: --incentive <ID>")
            
    elif "--latest" in sys.argv:
        # Show latest N processed
        try:
            idx = sys.argv.index("--latest")
            limit = int(sys.argv[idx + 1])
            view_all_processed(limit)
        except (IndexError, ValueError):
            print("[ERROR] Please provide number: --latest <N>")
            
    else:
        print("Usage:")
        print("  python view_incentive_results.py                    # Show all processed")
        print("  python view_incentive_results.py --incentive 2332   # Show specific incentive")
        print("  python view_incentive_results.py --latest 10        # Show latest 10 processed")


if __name__ == "__main__":
    main()