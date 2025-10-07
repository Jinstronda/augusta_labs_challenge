"""Test the new 4-type classifier with query extraction"""
from backend.app.services.classifier import QueryClassifier

classifier = QueryClassifier()

test_queries = [
    "I want this specific company named joao",
    "I want the electrical companies",
    "Find me C.R.P.B. - PRODUTOS PARA RAMO AUTOMÓVEL",
    "Show me renewable energy companies",
    "Digital Innovation Fund",
    "Green energy incentives",
    "R&D funding programs",
    "Show me Microsoft",
]

print("=" * 80)
print("TESTING NEW CLASSIFIER")
print("=" * 80)

for query in test_queries:
    try:
        query_type, cleaned_query = classifier.classify(query)
        print(f"\nQuery: {query}")
        print(f"  Type: {query_type}")
        print(f"  Cleaned: {cleaned_query}")
    except Exception as e:
        print(f"\nQuery: {query}")
        print(f"  ERROR: {e}")

print("\n" + "=" * 80)
