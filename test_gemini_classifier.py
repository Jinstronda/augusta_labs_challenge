"""
Test Gemini 2.0 Flash classifier via Vertex AI
Compare with GPT-5-mini for query classification and extraction
"""

import os
import json
import time
from google import genai
from google.genai import types

# Set up Vertex AI credentials
VERTEX_AI_API_KEY = "AIzaSyAKWaDFzEYZKxhuwumj1fmv-IHmz_pAGw8"  # Your API key

# Initialize Gemini client
client = genai.Client(api_key=VERTEX_AI_API_KEY)

def create_classification_prompt(query: str) -> str:
    """Create the same prompt used for GPT-5-mini"""
    return f"""Classify this query and extract the search terms.

Types:
1. COMPANY_NAME - User asks for a specific company by name
   Extract: Just the company name
   Example: "I want company named joao" → {{"type": "COMPANY_NAME", "query": "joao"}}
   Example: "Show me Microsoft" → {{"type": "COMPANY_NAME", "query": "Microsoft"}}

2. COMPANY_TYPE - User asks for companies in a market/sector/category
   Extract: The sector/category terms
   Example: "I want electrical companies" → {{"type": "COMPANY_TYPE", "query": "electrical companies"}}
   Example: "Tech startups in Lisbon" → {{"type": "COMPANY_TYPE", "query": "tech startups lisbon"}}

3. INCENTIVE_NAME - User asks for a specific incentive by name or ID
   Extract: Just the incentive name/ID
   Example: "Show me Digital Innovation Fund" → {{"type": "INCENTIVE_NAME", "query": "Digital Innovation Fund"}}
   Example: "Incentive 1288" → {{"type": "INCENTIVE_NAME", "query": "1288"}}

4. INCENTIVE_TYPE - User asks for a group/category of incentives
   Extract: The category/type terms
   Example: "Green energy incentives" → {{"type": "INCENTIVE_TYPE", "query": "green energy"}}
   Example: "R&D funding programs" → {{"type": "INCENTIVE_TYPE", "query": "R&D funding"}}

User Query: "{query}"

Return JSON with type and cleaned query: {{"type": "COMPANY_NAME", "query": "extracted terms"}}

JSON:"""


def classify_with_gemini(query: str) -> tuple[str, str, float]:
    """
    Classify query using Gemini 2.0 Flash
    
    Returns:
        (query_type, cleaned_query, response_time)
    """
    prompt = create_classification_prompt(query)
    
    start_time = time.time()
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',  # Using Gemini 2.5 Flash
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.0,  # Deterministic for classification
                max_output_tokens=100,
                response_mime_type='application/json'  # Force JSON response
            )
        )
        
        response_time = time.time() - start_time
        
        # Parse response
        result_text = response.text.strip()
        result_data = json.loads(result_text)
        
        query_type = result_data.get('type', '').upper()
        cleaned_query = result_data.get('query', '').strip()
        
        return query_type, cleaned_query, response_time
        
    except Exception as e:
        response_time = time.time() - start_time
        print(f"Error: {e}")
        return "ERROR", str(e), response_time


def test_queries():
    """Test various queries with Gemini"""
    
    test_cases = [
        # COMPANY_NAME
        "I want this specific company named joao",
        "Find me C.R.P.B. - PRODUTOS PARA RAMO AUTOMÓVEL",
        "Show me Microsoft",
        "Information about Galp Energia",
        
        # COMPANY_TYPE
        "I want the electrical companies",
        "Show me renewable energy companies",
        "Tech startups in Lisbon",
        "Manufacturing companies in Portugal",
        
        # INCENTIVE_NAME
        "Digital Innovation Fund",
        "Show me incentive 1288",
        "PRR funding details",
        "Information about Fundo Ambiental",
        
        # INCENTIVE_TYPE
        "Green energy incentives",
        "R&D funding programs",
        "Startup grants",
        "Innovation support programs",
    ]
    
    print("=" * 80)
    print("TESTING GEMINI 2.0 FLASH CLASSIFIER")
    print("=" * 80)
    
    total_time = 0
    success_count = 0
    
    for query in test_cases:
        query_type, cleaned_query, response_time = classify_with_gemini(query)
        total_time += response_time
        
        if query_type != "ERROR":
            success_count += 1
            status = "✓"
        else:
            status = "✗"
        
        print(f"\n{status} Query: {query}")
        print(f"  Type: {query_type}")
        print(f"  Cleaned: {cleaned_query}")
        print(f"  Time: {response_time*1000:.0f}ms")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total queries: {len(test_cases)}")
    print(f"Successful: {success_count}")
    print(f"Failed: {len(test_cases) - success_count}")
    print(f"Average time: {(total_time/len(test_cases))*1000:.0f}ms")
    print(f"Total time: {total_time:.2f}s")
    
    print("\n" + "=" * 80)
    print("COMPARISON WITH GPT-5-MINI")
    print("=" * 80)
    print("Gemini 2.0 Flash:")
    print("  - Free tier available")
    print("  - Native JSON mode")
    print("  - Fast response times")
    print("  - Good at structured extraction")
    print("\nGPT-5-mini:")
    print("  - Requires OpenAI API key")
    print("  - JSON parsing needed")
    print("  - Consistent performance")
    print("  - Well-tested for this task")


if __name__ == "__main__":
    test_queries()
