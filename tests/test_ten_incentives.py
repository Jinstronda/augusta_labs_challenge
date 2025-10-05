"""
Test Script for Ten Incentives with Detailed Logging

This script tests the enhanced matching system on 10 random incentives
and logs detailed results including scores, processing steps, and outcomes.

All logs are saved to the data/ folder for analysis.

Usage:
    python test_ten_incentives.py
"""

import os
import sys
import json
import time
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# Get the project root directory (parent of tests/)
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


def ensure_data_folder():
    """Create data folder if it doesn't exist."""
    if not os.path.exists('data'):
        os.makedirs('data')
        print("[SETUP] Created data/ folder for logs")


def get_ten_random_incentives():
    """Get 10 random incentives for testing."""
    print(f"\n[TEST] Loading 10 random incentives for testing...")
    
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT incentive_id, title, sector, geo_requirement, 
               ai_description, eligible_actions, funding_rate, investment_eur
        FROM incentives
        WHERE sector IS NOT NULL 
        AND eligible_actions IS NOT NULL 
        AND geo_requirement IS NOT NULL
        AND ai_description IS NOT NULL
        ORDER BY RANDOM() 
        LIMIT 10
    """)
    
    results = cursor.fetchall()
    
    incentives = []
    for row in results:
        incentive = {
            'id': row[0], 'title': row[1], 'sector': row[2],
            'geo_requirement': row[3], 'ai_description': row[4],
            'eligible_actions': row[5], 'funding_rate': row[6], 
            'investment_eur': row[7]
        }
        incentives.append(incentive)
    
    cursor.close()
    conn.close()
    
    print(f"[TEST] Selected {len(incentives)} incentives for testing")
    return incentives


def log_detailed_results(incentive, result, processing_log, test_number):
    """Log detailed results to JSON file."""
    
    # Create detailed log entry
    log_entry = {
        'test_number': test_number,
        'timestamp': datetime.now().isoformat(),
        'incentive': {
            'id': incentive['id'],
            'title': incentive['title'],
            'sector': incentive['sector'],
            'geo_requirement': incentive['geo_requirement'],
            'eligible_actions': incentive['eligible_actions'][:200] + "..." if len(incentive['eligible_actions']) > 200 else incentive['eligible_actions']
        },
        'processing': {
            'total_candidates_searched': result.total_candidates_searched,
            'geographic_eligible_count': result.geographic_eligible_count,
            'processing_time_seconds': result.processing_time,
            'companies_found': len(result.companies)
        },
        'outcome': {
            'status': 'success' if result.companies else 'no_companies_found',
            'companies_returned': len(result.companies),
            'max_semantic_score': max([c.get('rerank_score', 0) for c in result.companies]) if result.companies else 0,
            'min_semantic_score': min([c.get('rerank_score', 0) for c in result.companies]) if result.companies else 0,
            'avg_semantic_score': sum([c.get('rerank_score', 0) for c in result.companies]) / len(result.companies) if result.companies else 0
        },
        'companies': []
    }
    
    # Add detailed company information
    for i, company in enumerate(result.companies, 1):
        company_info = {
            'rank': i,
            'id': company['id'],
            'name': company['name'],
            'semantic_score': company.get('rerank_score', 0),
            'cae_classification': company.get('cae', 'N/A'),
            'location_address': company.get('location_address', 'N/A'),
            'website': company.get('website', 'N/A'),
            'activities_preview': company.get('activities', '')[:150] + "..." if company.get('activities') and len(company.get('activities', '')) > 150 else company.get('activities', 'N/A')
        }
        log_entry['companies'].append(company_info)
    
    # Add processing log
    log_entry['processing_log'] = processing_log
    
    # Save to individual file
    filename = f"data/test_{test_number:02d}_incentive_{incentive['id']}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(log_entry, f, indent=2, ensure_ascii=False)
    
    print(f"[LOG] Detailed results saved to {filename}")
    
    return log_entry


def process_single_test_incentive(pipeline, incentive, test_number):
    """Process a single incentive with detailed logging."""
    
    print(f"\n{'='*80}")
    print(f"TEST {test_number}/10 - INCENTIVE {incentive['id']}")
    print(f"{'='*80}")
    print(f"Title: {incentive['title']}")
    print(f"Sector: {incentive['sector']}")
    print(f"Geographic Requirement: {incentive['geo_requirement']}")
    print(f"{'='*80}")
    
    processing_log = []
    start_time = time.time()
    
    try:
        # Capture processing steps
        processing_log.append({
            'step': 'start',
            'timestamp': datetime.now().isoformat(),
            'message': f"Starting processing for incentive {incentive['id']}"
        })
        
        # Process the incentive
        result = pipeline.find_matching_companies(incentive)
        
        processing_time = time.time() - start_time
        
        processing_log.append({
            'step': 'complete',
            'timestamp': datetime.now().isoformat(),
            'message': f"Processing completed in {processing_time:.1f} seconds"
        })
        
        # Determine outcome
        if not result.companies:
            outcome = "NO COMPANIES FOUND"
            print(f"\n[RESULT] {outcome}")
            print(f"[INFO] Searched {result.total_candidates_searched} candidates")
            print(f"[INFO] {result.geographic_eligible_count} were geographically eligible")
        elif len(result.companies) < 5:
            outcome = f"FOUND {len(result.companies)} COMPANIES (LESS THAN 5)"
            print(f"\n[RESULT] {outcome}")
            print(f"[INFO] Searched {result.total_candidates_searched} candidates")
            print(f"[INFO] {result.geographic_eligible_count} were geographically eligible")
        else:
            outcome = f"FOUND {len(result.companies)} COMPANIES (FULL SET)"
            print(f"\n[RESULT] {outcome}")
            print(f"[INFO] Searched {result.total_candidates_searched} candidates")
        
        # Show top companies
        if result.companies:
            print(f"\n[TOP COMPANIES]")
            for i, company in enumerate(result.companies, 1):
                score = company.get('rerank_score', 0)
                print(f"  {i}. {company['name']} (score: {score:.4f})")
        
        print(f"\n[TIMING] Total processing time: {processing_time:.1f} seconds")
        
        # Log detailed results
        log_entry = log_detailed_results(incentive, result, processing_log, test_number)
        
        return True, log_entry
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        processing_log.append({
            'step': 'error',
            'timestamp': datetime.now().isoformat(),
            'message': f"Error occurred: {str(e)}"
        })
        
        print(f"\n[ERROR] Failed to process incentive {incentive['id']}: {str(e)}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        print(f"[TIMING] Failed after {processing_time:.1f} seconds")
        
        # Create error log entry
        error_log = {
            'test_number': test_number,
            'timestamp': datetime.now().isoformat(),
            'incentive': {
                'id': incentive['id'],
                'title': incentive['title'],
                'sector': incentive['sector'],
                'geo_requirement': incentive['geo_requirement']
            },
            'outcome': {
                'status': 'error',
                'error_message': str(e),
                'error_type': type(e).__name__,
                'processing_time_seconds': processing_time
            },
            'processing_log': processing_log
        }
        
        # Save error log
        filename = f"data/test_{test_number:02d}_incentive_{incentive['id']}_ERROR.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(error_log, f, indent=2, ensure_ascii=False)
        
        return False, error_log


def create_summary_report(all_results):
    """Create a summary report of all test results."""
    
    summary = {
        'test_summary': {
            'timestamp': datetime.now().isoformat(),
            'total_tests': len(all_results),
            'successful_tests': sum(1 for r in all_results if r.get('outcome', {}).get('status') == 'success'),
            'failed_tests': sum(1 for r in all_results if r.get('outcome', {}).get('status') == 'error'),
            'no_companies_found': sum(1 for r in all_results if r.get('outcome', {}).get('status') == 'no_companies_found')
        },
        'performance_stats': {},
        'detailed_results': all_results
    }
    
    # Calculate performance statistics
    successful_results = [r for r in all_results if r.get('outcome', {}).get('status') == 'success']
    
    if successful_results:
        processing_times = [r['processing']['processing_time_seconds'] for r in successful_results]
        candidates_searched = [r['processing']['total_candidates_searched'] for r in successful_results]
        companies_found = [r['processing']['companies_found'] for r in successful_results]
        semantic_scores = [r['outcome']['avg_semantic_score'] for r in successful_results if r['outcome']['avg_semantic_score'] > 0]
        
        summary['performance_stats'] = {
            'avg_processing_time': sum(processing_times) / len(processing_times),
            'min_processing_time': min(processing_times),
            'max_processing_time': max(processing_times),
            'avg_candidates_searched': sum(candidates_searched) / len(candidates_searched),
            'avg_companies_found': sum(companies_found) / len(companies_found),
            'avg_semantic_score': sum(semantic_scores) / len(semantic_scores) if semantic_scores else 0,
            'max_semantic_score': max(semantic_scores) if semantic_scores else 0,
            'min_semantic_score': min(semantic_scores) if semantic_scores else 0
        }
    
    # Save summary report
    filename = f"data/TEST_SUMMARY_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"\n[SUMMARY] Complete test summary saved to {filename}")
    
    return summary


def main():
    """Main test function."""
    
    print("="*80)
    print("TESTING ENHANCED MATCHING SYSTEM ON 10 INCENTIVES")
    print("Incremental Search Logic: 10 → 20 → 30 → 40 → 50")
    print("="*80)
    
    # Setup
    ensure_data_folder()
    
    # Get test incentives
    incentives = get_ten_random_incentives()
    
    if not incentives:
        print("[ERROR] No incentives found for testing!")
        return
    
    # Initialize pipeline
    print(f"\n[INIT] Initializing enhanced matching pipeline...")
    pipeline = EnhancedMatchingPipeline()
    
    # Process all test incentives
    start_time = time.time()
    all_results = []
    successful = 0
    failed = 0
    
    for i, incentive in enumerate(incentives, 1):
        success, log_entry = process_single_test_incentive(pipeline, incentive, i)
        
        all_results.append(log_entry)
        
        if success:
            successful += 1
        else:
            failed += 1
        
        # Small delay between tests
        if i < len(incentives):
            print(f"\n[WAIT] Waiting 2 seconds before next test...")
            time.sleep(2)
    
    # Create summary report
    total_time = time.time() - start_time
    
    print(f"\n{'='*80}")
    print(f"TEST COMPLETED")
    print(f"{'='*80}")
    print(f"Total tests: {len(incentives)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {successful/len(incentives)*100:.1f}%")
    print(f"Total time: {total_time/60:.1f} minutes")
    print(f"Average time per test: {total_time/len(incentives):.1f} seconds")
    
    # Generate summary report
    summary = create_summary_report(all_results)
    
    # Show key statistics
    if summary['performance_stats']:
        stats = summary['performance_stats']
        print(f"\n[PERFORMANCE STATISTICS]")
        print(f"Average processing time: {stats['avg_processing_time']:.1f} seconds")
        print(f"Average candidates searched: {stats['avg_candidates_searched']:.0f}")
        print(f"Average companies found: {stats['avg_companies_found']:.1f}")
        print(f"Average semantic score: {stats['avg_semantic_score']:.4f}")
    
    print(f"\n[LOGS] All detailed logs saved to data/ folder")
    print(f"[INFO] Check individual test files: data/test_XX_incentive_YYYY.json")
    print(f"[INFO] Check summary report: data/TEST_SUMMARY_*.json")
    print(f"\n{'='*80}")


if __name__ == "__main__":
    main()