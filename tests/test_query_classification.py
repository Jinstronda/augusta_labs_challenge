"""
Test query classification with the 4 query types
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.classifier import QueryClassifier

def test_classification():
    """Test all 4 query types"""
    
    classifier = QueryClassifier()
    
    test_cases = [
        # SPECIFIC_COMPANY
        ("Show me Galp Energia", "SPECIFIC_COMPANY"),
        ("Find Microsoft", "SPECIFIC_COMPANY"),
        ("Information about Tesla", "SPECIFIC_COMPANY"),
        
        # COMPANY_GROUP
        ("Companies in renewable energy", "COMPANY_GROUP"),
        ("Tech startups in Lisbon", "COMPANY_GROUP"),
        ("Manufacturing companies", "COMPANY_GROUP"),
        
        # SPECIFIC_INCENTIVE
        ("Show me Digital Innovation Fund", "SPECIFIC_INCENTIVE"),
        ("Incentive 1288", "SPECIFIC_INCENTIVE"),
        ("PRR funding details", "SPECIFIC_INCENTIVE"),
        
        # INCENTIVE_GROUP
        ("Green energy incentives", "INCENTIVE_GROUP"),
        ("R&D funding programs", "INCENTIVE_GROUP"),
        ("Startup grants", "INCENTIVE_GROUP"),
    ]
    
    print("=" * 80)
    print("QUERY CLASSIFICATION TESTS")
    print("=" * 80)
    
    correct = 0
    total = len(test_cases)
    
    for query, expected in test_cases:
        try:
            result = classifier.classify(query)
            status = "✓" if result == expected else "✗"
            correct += 1 if result == expected else 0
            
            print(f"\n{status} Query: {query}")
            print(f"  Expected: {expected}")
            print(f"  Got: {result}")
            
        except Exception as e:
            print(f"\n✗ Query: {query}")
            print(f"  Error: {e}")
    
    print("\n" + "=" * 80)
    print(f"RESULTS: {correct}/{total} correct ({correct/total*100:.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    test_classification()
