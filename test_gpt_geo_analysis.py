"""
Test script for GPT-5-mini geographic analysis
"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv('config.env')

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPEN_AI"))

def test_gpt_geo_analysis():
    """Test GPT-5-mini geographic analysis with sample data."""
    
    # Sample companies with locations
    company_data = [
        {
            "company_id": 1,
            "name": "MUNICÍPIO DE GRÂNDOLA",
            "address": "Grândola"
        },
        {
            "company_id": 2,
            "name": "SUCESSO E GRATIDÃO, UNIPESSOAL, LDA",
            "address": "Praceta Ten. Domingos António Mte., 8800-320 Tavira"
        },
        {
            "company_id": 3,
            "name": "AZULDISPONÍVEL, LDA",
            "address": "R. Vieira Lusitano 10A, 1070-280 Lisboa"
        }
    ]
    
    geo_requirement = "Alentejo"
    
    # Create the prompt
    prompt = f"""You are analyzing geographic eligibility for Portuguese government incentives.

TASK: Determine if each company's location meets the geographic requirement.

GEOGRAPHIC REQUIREMENT: {geo_requirement}

PORTUGUESE GEOGRAPHIC CONTEXT:
- NUTS II regions: Norte, Centro, Lisboa, Alentejo, Algarve, Região Autónoma dos Açores, Região Autónoma da Madeira
- "Nacional" means anywhere in Portugal is eligible
- "Centro (NUTS II)" refers to the Centro region specifically
- City names like "Lisboa" may refer to the municipality or broader metropolitan area
- When addresses are ambiguous or unclear, be conservative (return false)

COMPANIES TO ANALYZE:
{json.dumps(company_data, indent=2, ensure_ascii=False)}

OUTPUT REQUIREMENTS:
- Return ONLY a JSON object, no explanation
- Format: {{"company_id": true, "company_id": true, ...}}
- true = company location meets the requirement
- false = company location does not meet the requirement
- Include ALL companies in the response
- Use company_id as keys (not names)

JSON OUTPUT:"""

    print("=" * 80)
    print("TESTING GPT-5-MINI GEOGRAPHIC ANALYSIS")
    print("=" * 80)
    print(f"Geographic Requirement: {geo_requirement}")
    print(f"Number of companies: {len(company_data)}")
    print("\nCompanies:")
    for company in company_data:
        print(f"  {company['company_id']}: {company['name']} - {company['address']}")
    
    print("\n" + "-" * 80)
    print("PROMPT:")
    print("-" * 80)
    print(prompt)
    
    print("\n" + "-" * 80)
    print("CALLING GPT-5-MINI...")
    print("-" * 80)
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-5-mini",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1000
        )
        
        result_text = response.choices[0].message.content.strip()
        
        print(f"RAW RESPONSE:")
        print(f"'{result_text}'")
        print(f"Response length: {len(result_text)}")
        
        if not result_text:
            print("\n❌ EMPTY RESPONSE!")
            return
        
        # Try to extract JSON
        json_start = result_text.find('{')
        json_end = result_text.rfind('}') + 1
        
        print(f"\nJSON extraction:")
        print(f"  json_start: {json_start}")
        print(f"  json_end: {json_end}")
        
        if json_start >= 0 and json_end > json_start:
            json_text = result_text[json_start:json_end]
            print(f"  Extracted JSON: '{json_text}'")
            
            try:
                parsed_json = json.loads(json_text)
                print(f"\n✅ SUCCESS! Parsed JSON:")
                print(json.dumps(parsed_json, indent=2))
                
                # Validate results
                for company in company_data:
                    company_id = str(company['company_id'])
                    result = parsed_json.get(company_id, "MISSING")
                    print(f"  Company {company_id}: {result}")
                
            except json.JSONDecodeError as e:
                print(f"\n❌ JSON PARSE ERROR: {e}")
                
        else:
            print(f"\n❌ NO JSON FOUND IN RESPONSE")
            
    except Exception as e:
        print(f"❌ API ERROR: {e}")

def test_different_prompts():
    """Test different prompt variations."""
    
    company_data = [
        {"company_id": 1, "name": "Test Company", "address": "Lisboa"}
    ]
    
    prompts = [
        # Simple prompt
        f"""Analyze if this company is in Alentejo region:
Company: Test Company, Address: Lisboa
Return JSON: {{"1": true/false}}""",
        
        # Very explicit prompt
        f"""You must return ONLY JSON. No text before or after.
Is this company in Alentejo? Company 1: Lisboa
JSON:""",
        
        # Different format
        f"""Geographic analysis for Alentejo region:
Company 1: Lisboa
Output format: {{"1": boolean}}
Response:"""
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{'='*60}")
        print(f"TESTING PROMPT VARIATION {i}")
        print(f"{'='*60}")
        print(prompt)
        print(f"\n{'-'*40}")
        
        try:
            response = openai_client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=100
            )
            
            result = response.choices[0].message.content.strip()
            print(f"Response: '{result}'")
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print("Testing GPT-5-mini geographic analysis...")
    test_gpt_geo_analysis()
    
    print("\n" + "="*80)
    print("TESTING DIFFERENT PROMPT VARIATIONS")
    print("="*80)
    test_different_prompts()