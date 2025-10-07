"""Test Gemini response structure"""
from google import genai
from google.genai import types
import json

GEMINI_API_KEY = "AIzaSyAKWaDFzEYZKxhuwumj1fmv-IHmz_pAGw8"
client = genai.Client(api_key=GEMINI_API_KEY)

query = "Give me 5 green technology companies"

prompt = f"""Classify this query and extract the search terms.

Types:
1. COMPANY_NAME - User asks for a specific company by name
2. COMPANY_TYPE - User asks for companies in a market/sector/category
3. INCENTIVE_NAME - User asks for a specific incentive by name or ID
4. INCENTIVE_TYPE - User asks for a group/category of incentives

User Query: "{query}"

Return JSON with type and cleaned query: {{"type": "COMPANY_TYPE", "query": "green technology companies"}}

JSON:"""

print("Testing Gemini response structure...")
print("=" * 80)

try:
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.0,
            max_output_tokens=100,
            response_mime_type='application/json'
        )
    )
    
    print(f"Response object: {response}")
    print(f"Response type: {type(response)}")
    print(f"Has text attr: {hasattr(response, 'text')}")
    
    if hasattr(response, 'text'):
        print(f"response.text: {response.text}")
        print(f"response.text type: {type(response.text)}")
    
    if hasattr(response, 'candidates'):
        print(f"response.candidates: {response.candidates}")
        if response.candidates:
            print(f"First candidate: {response.candidates[0]}")
            if hasattr(response.candidates[0], 'content'):
                print(f"Candidate content: {response.candidates[0].content}")
                if hasattr(response.candidates[0].content, 'parts'):
                    print(f"Content parts: {response.candidates[0].content.parts}")
                    if response.candidates[0].content.parts:
                        print(f"First part: {response.candidates[0].content.parts[0]}")
                        if hasattr(response.candidates[0].content.parts[0], 'text'):
                            print(f"Part text: {response.candidates[0].content.parts[0].text}")
    
    # Try to get the actual text
    if response.text:
        result = json.loads(response.text)
        print(f"\nParsed result: {result}")
    else:
        print("\nresponse.text is None or empty!")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
