"""
Quick test of the new optimized pipeline.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv('config.env')

# Import the pipeline
from enhanced_incentive_matching import EnhancedMatchingPipeline, get_random_incentive

def test_pipeline():
    """Test the new optimized pipeline."""
    print("="*80)
    print("TESTING NEW OPTIMIZED PIPELINE")
    print("="*80)
    
    # Get a test incentive
    incentive = get_random_incentive()
    if not incentive:
        print("No incentive found")
        return
    
    print(f"\nTest Incentive: {incentive['title']}")
    print(f"Geo Requirement: {incentive['geo_requirement']}")
    
    # Initialize pipeline
    pipeline = EnhancedMatchingPipeline()
    
    # Run the new algorithm
    result = pipeline.find_matching_companies(incentive, max_candidates=70)
    
    # Display results
    pipeline.display_results(result)
    
    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)

if __name__ == "__main__":
    test_pipeline()
