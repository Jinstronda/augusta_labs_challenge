"""
Test the simplified GPT prompt
"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv('config.env')
openai_client = OpenAI(api_key=os.getenv("OPEN_AI"))

def test_simple_prompt():
    company_data = [
        {"company_id": 1, "name": "Test Company 1", "address": "Lisboa"},
        {"company_id": 2, "name": "Test Company 2", "address": "Grândola"},
        {"company_id": 3, "name": "Test Company 3", "address": "Porto"}
    ]
    
    geo_requirement = "Alentejo"
    
    # Create simplified prompt
    company_list = []
    for company in company_data:
        company_list.append(f"Company {company['company_id']}: {company['address']}")
    
    companies_text = "\n".join(company_list)
    
    prompt = f"""Analyze if companies are in {geo_requirement} region of Portugal.

NUTS II regions: Norte, Centro, Lisboa, Alentejo, Algarve, Açores, Madeira
"Nacional" = anywhere in Portugal

Companies:
{companies_text}

Return JSON only: {{"company_id": true/false, ...}}

JSON:"""

    print("SIMPLIFIED PROMPT:")
    print("=" * 60)
    print(prompt)
    print("=" * 60)
    print(f"Prompt length: {len(prompt)} characters")
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=4000
        )
        
        result = response.choices[0].message.content.strip()
        print(f"\nResponse: '{result}'")
        print(f"Length: {len(result)}")
        
        if result:
            try:
                parsed = json.loads(result)
                print(f"Parsed JSON: {parsed}")
            except:
                print("Failed to parse as JSON")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_simple_prompt()