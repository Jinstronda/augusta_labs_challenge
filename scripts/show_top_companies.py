"""
Display top 5 companies with most eligible incentives
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
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cursor = conn.cursor()

# Query top 5 companies by number of eligible incentives
cursor.execute("""
    SELECT 
        company_id,
        company_name,
        eligible_incentives,
        jsonb_array_length(eligible_incentives) as num_incentives
    FROM companies
    WHERE eligible_incentives IS NOT NULL
    ORDER BY jsonb_array_length(eligible_incentives) DESC
    LIMIT 5
""")

results = cursor.fetchall()

print("=" * 80)
print("TOP 5 COMPANIES WITH MOST ELIGIBLE INCENTIVES")
print("=" * 80)

for idx, (company_id, company_name, incentives_json, num_incentives) in enumerate(results, 1):
    incentives = json.loads(incentives_json) if isinstance(incentives_json, str) else incentives_json
    
    print(f"\n{idx}. [{company_id}] {company_name}")
    print(f"   Total Eligible Incentives: {num_incentives}")
    print(f"   Incentives:")
    
    for i, inc in enumerate(incentives, 1):
        title = inc['title'][:70] + "..." if len(inc['title']) > 70 else inc['title']
        print(f"      {i}. {title}")
        print(f"         Score: {inc['company_score']:.3f} | Rank: {inc['rank']}")

print("\n" + "=" * 80)

cursor.close()
conn.close()
