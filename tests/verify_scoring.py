"""
Verify the scoring results in the database.
"""
import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv('config.env')

DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

conn = psycopg2.connect(
    dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
    host=DB_HOST, port=DB_PORT
)
cursor = conn.cursor()

# Get latest scored incentive
cursor.execute("""
    SELECT incentive_id, title, top_5_companies, top_5_companies_scored
    FROM incentives
    WHERE top_5_companies_scored IS NOT NULL
    ORDER BY incentive_id DESC
    LIMIT 1
""")

result = cursor.fetchone()

if not result:
    print("No scored results found!")
else:
    incentive_id, title, semantic_results, scored_results = result
    
    print(f"\n{'='*80}")
    print(f"INCENTIVE: {title}")
    print(f"ID: {incentive_id}")
    print(f"{'='*80}")
    
    # Parse JSON (handle both dict and string)
    semantic = semantic_results if isinstance(semantic_results, dict) else json.loads(semantic_results)
    scored = scored_results if isinstance(scored_results, dict) else json.loads(scored_results)
    
    print(f"\n{'='*80}")
    print(f"TOP 5 COMPANIES - SEMANTIC RANKING")
    print(f"{'='*80}")
    for i, company in enumerate(semantic['companies'][:5], 1):
        print(f"\n{i}. {company['name']}")
        print(f"   Semantic Score: {company['semantic_score']:.4f}")
    
    print(f"\n{'='*80}")
    print(f"TOP 5 COMPANIES - COMPANY SCORE RANKING")
    print(f"{'='*80}")
    for i, company in enumerate(scored['companies'][:5], 1):
        print(f"\n{i}. {company['name']}")
        print(f"   Company Score: {company['company_score']:.4f}")
        print(f"   Semantic Score: {company['semantic_score']:.4f}")
        
        # Show score components
        components = company.get('score_components', {})
        print(f"   Components:")
        print(f"     S (Semantic): {components.get('s', 0):.3f}")
        print(f"     M (CAE Overlap): {components.get('m', 0):.3f}")
        print(f"     G (Geographic): {components.get('g', 0):.3f}")
        print(f"     O (Org Capacity): {components.get('o', 0):.3f}")
        print(f"     W (Website): {components.get('w', 0):.3f}")
        print(f"     Org Direction: {components.get('org_direction', 0)}")
    
    print(f"\n{'='*80}")
    print(f"FORMULA: {scored['scoring_formula']}")
    print(f"{'='*80}")

cursor.close()
conn.close()
