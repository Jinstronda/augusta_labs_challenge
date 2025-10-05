"""
This is important.
The thing is:
We need to be able to get collumns for a lot of data in order to match the companies.
This will run every single Incentive through a LLM that will add data to it from region to funding.
"""
import os
import json
import psycopg2
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Database configuration
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPEN_AI")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

PROMPT_TEMPLATE = """You are an expert data extraction AI. Your task is to analyze an incentive's description and its structured eligibility criteria to populate a specific JSON object. You must follow the instructions and format precisely.

### INPUT FORMAT
You will receive two pieces of information for each task:
1.  **ai_description**: A natural language summary of the incentive.
2.  **eligibility_criteria**: A JSON string containing specific, structured data about the incentive.

### OUTPUT FORMAT
Your response MUST be a single, valid JSON object and nothing else. Do not include any explanatory text, markdown formatting like `json`, or any introductory phrases. The JSON object must have the following structure:

{{
  "sector": "string or null",
  "geo_requirement": "string or null",
  "eligible_actions": "string or null",
  "funding_rate": "string or null",
  "investment_eur": "string or null"
}}

### FIELD DEFINITIONS AND INSTRUCTIONS
sector: Identify the primary industry, economic area, or target group. Look for keywords like "Saúde" (Health), "Pesca" (Fishing), "Turismo" (Tourism), "Administração Pública" (Public Administration), "Cultura" (Culture), "PME" (SMEs), etc.
geo_requirement: Extract the most specific geographical scope.
Priority Rule: Always prioritize the most specific, named territory from the eligibility_criteria.
Specificity Hierarchy:
If a specific territory like a GAL, NUTS III region, or cross-border area is named (e.g., "Território de intervenção do GAL ADELIA OR MAR", "Região NUTS III Alto Alentejo"), you MUST use that exact name. Do not generalize it.
If the criteria refer to a broad list of places within a larger region (e.g., "Municípios do NUTS II Centro"), then you can generalize to that larger region (e.g., "Centro (NUTS II)").
If no specific region is mentioned, infer from the context (e.g., a national agency often implies "Portugal").
eligible_actions: Concisely describe the main activities, project types, or investments that are supported. Look for keys like eligible_actions, project_type, tipologia_de_ação, eligible_operations. Summarize them into a clear string.
funding_rate: Extract any mention of co-financing rates or support percentages. Look for keys like funding_rate, cofinancing_rate, taxa_apoio, FEDER. Format it as a string (e.g., "até 85%", "60% FEDER"). If no rate is mentioned, the value must be null.
investment_eur: Extract any minimum or maximum project costs or investment values. Look for keys like minimum_project_cost_eur, max_investment_eur, custo_total_mínimo, investimento_mínimo_elegível. If no value is mentioned, the value must be null.

### EXAMPLES

INPUT 1:
ai_description: "Apoio destinado a entidades do setor não lucrativo e autarquias locais para projetos de conservação marinha e requalificação do espaço marítimo no território de intervenção do GAL ADELIA OR MAR, com um investimento máximo definido."
eligibility_criteria: {{"entity_type": ["Entidades do setor não lucrativo", "Autarquias locais"], "eligible_actions": ["Conservação e proteção da biodiversidade marinha", "Promoção da literacia do oceano", "Requalificação sustentável do espaço marítimo", "Apoio a infraestruturas verdes de preservação da paisagem costeira"], "geographic_scope": "Território de intervenção do GAL ADELIA OR MAR (São Jorge, Faial, Pico, Flores e Corvo)", "max_investment_eur": 28130}}
OUTPUT 1:
{{
  "sector": "Economia do Mar / Setor Não Lucrativo",
  "geo_requirement": "Território de intervenção do GAL ADELIA OR MAR (São Jorge, Faial, Pico, Flores e Corvo)",
  "eligible_actions": "Conservação da biodiversidade marinha, promoção da literacia do oceano, requalificação do espaço marítimo e apoio a infraestruturas verdes costeiras",
  "funding_rate": null,
  "investment_eur": "Máximo 28,130 EUR"
}}
INPUT 2:
ai_description: "Incentivo para a reabilitação urbana em municípios da região Centro, com foco em edifícios, espaço público e eficiência energética. O cofinanciamento é de 85% FEDER e existe um custo mínimo de projeto de 250.000 euros."
eligibility_criteria: {{"location": "Áreas de Reabilitação Urbana (ARU) dos centros urbanos dos municípios elegíveis", "cofinancing_rate": "85% FEDER", "eligible_actions": "Intervenções de reabilitação e regeneração urbanas (reabilitação de edifícios, espaço público, criação de equipamentos coletivos, medidas de eficiência energética e mobilidade intra/interurbana)", "eligible_entities": "Municípios do NUTS II Centro identificados no aviso (ex.: Abrantes, Águeda, Alcobaça, Viseu, entre outros)", "application_deadline": "31/12/2024", "minimum_project_cost_eur": 250000}}
OUTPUT 2:
{{
  "sector": "Reabilitação Urbana / Administração Pública",
  "geo_requirement": "Centro (NUTS II)",
  "eligible_actions": "Reabilitação de edifícios, espaço público, criação de equipamentos coletivos, eficiência energética e mobilidade urbana",
  "funding_rate": "85% FEDER",
  "investment_eur": "Mínimo 250,000 EUR"
}}
INPUT 3:
ai_description: "Este aviso financia projetos em Alto Alentejo e Alentejo Litoral para modernização de infraestruturas."
eligibility_criteria: {{"region": "Região NUTS III Alto Alentejo e Região NUTS III Alentejo Litoral", "entities": "Municípios e entidades públicas"}}
OUTPUT 3:
{{
  "sector": "Infraestruturas / Administração Pública",
  "geo_requirement": "Região NUTS III Alto Alentejo e Região NUTS III Alentejo Litoral",
  "eligible_actions": "Modernização de infraestruturas públicas",
  "funding_rate": null,
  "investment_eur": null
}}
### TASK
Now, process the following input and provide the JSON output.

INPUT:
ai_description: {ai_description}
eligibility_criteria: {eligibility_criteria}"""


def get_incentives_to_process(limit=None):
    """Get incentives that need LLM processing"""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    
    query = """
        SELECT incentive_id, ai_description, eligibility_criteria
        FROM incentives
        WHERE sector IS NULL
    """ 
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return results


def process_with_gpt5(ai_description, eligibility_criteria):
    # Debug: Print input data
    print(f"  [DEBUG] ai_description: {ai_description[:200] if ai_description else 'None'}...")
    print(f"  [DEBUG] eligibility_criteria: {eligibility_criteria[:200] if eligibility_criteria else 'None'}...")
    
    # prompt
    prompt = PROMPT_TEMPLATE.format(
        ai_description=ai_description or "No description available",
        eligibility_criteria=eligibility_criteria or "{}"
    )
    
    print(f"  [DEBUG] Prompt length: {len(prompt)} characters")
    
    try:
        # call gpt 5 mini, which is cheap
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            # gpt 5 models only support temperature=1 (default)
            max_completion_tokens=2000  # GPT-5 uses max_completion_tokens instead of max_tokens
        )
        
        # Debug: Print full response
        print(f"  [DEBUG] Response object type: {type(response)}")
        print(f"  [DEBUG] Response choices: {len(response.choices)}")
        
        message = response.choices[0].message
        print(f"  [DEBUG] Message content: {message.content}")
        print(f"  [DEBUG] Message refusal: {getattr(message, 'refusal', None)}")
        
        # Extract the response
        content = message.content
        
        if not content:
            print(f"  ✗ Empty response from API")
            if hasattr(message, 'refusal') and message.refusal:
                print(f"  ✗ Model refused: {message.refusal}")
            return None
            
        content = content.strip()
        
        # Parse JSON
        result = json.loads(content)
        
        return result
    
    except json.JSONDecodeError as e:
        print(f"  ✗ JSON parsing error: {e}")
        print(f"  Response was: {content[:200] if content else 'EMPTY'}")
        return None
    except Exception as e:
        print(f"  ✗ API error: {e}")
        import traceback
        traceback.print_exc()
        return None


def update_incentive(incentive_id, data):
    """Update incentive with extracted data"""
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    
    update_query = """
        UPDATE incentives
        SET 
            sector = %s,
            geo_requirement = %s,
            eligible_actions = %s,
            funding_rate = %s,
            investment_eur = %s
        WHERE incentive_id = %s
    """
    cursor.execute(update_query, (
        data.get('sector'),
        data.get('geo_requirement'),
        data.get('eligible_actions'),
        data.get('funding_rate'),
        data.get('investment_eur'),
        incentive_id
    ))
    conn.commit()
    cursor.close()
    conn.close() 
def main():
    print("=" * 70)
    print("GPT-5-mini Field Extraction - Testing Mode")
    print("=" * 70)
    print("\n📊 Fetching 2 incentives for testing...")
    incentives = get_incentives_to_process(limit=None)
    if not incentives:
        print("✓ No incentives need processing!")
        return
    print(f"Found {len(incentives)} incentives to process\n")
    success_count = 0
    for idx, (incentive_id, ai_description, eligibility_criteria) in enumerate(incentives, 1):
        print(f"Processing {idx}/{len(incentives)} - ID: {incentive_id}")
        
        # Skip if both ai_description and eligibility_criteria are None
        if not ai_description and not eligibility_criteria:
            print(f"  ⚠ Skipping - no data available\n")
            continue
        
        print(f"  Description: {ai_description[:100] if ai_description else 'None'}...")
        result = process_with_gpt5(ai_description, eligibility_criteria)
        if result:
            print(f"  ✓ Extracted data:")
            print(f"    - Sector: {result.get('sector')}")
            print(f"    - Geo: {result.get('geo_requirement')}")
            
            # Handle None values for actions
            actions = result.get('eligible_actions')
            if actions and isinstance(actions, str) and len(actions) > 50:
                print(f"    - Actions: {actions[:50]}...")
            else:
                print(f"    - Actions: {actions}")
            
            print(f"    - Funding: {result.get('funding_rate')}")
            print(f"    - Investment: {result.get('investment_eur')}")
            update_incentive(incentive_id, result)
            print(f"  ✓ Database updated")
            success_count += 1
        print()
    print("=" * 70)
    print(f"✓ Processing completed: {success_count} successful")
    print("=" * 70)
    if success_count > 0:
        print(f"\n🎉 Successfully processed {success_count} incentives!")
        print("\nRun check_status.py to see the updated statistics.")


if __name__ == "__main__":
    main()
