"""Test company search issue"""
import psycopg2
from dotenv import load_dotenv
import os

load_dotenv('config.env')

conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
)

cursor = conn.cursor()

# Search for C.R.P.B.
print("=" * 80)
print("SEARCHING FOR: C.R.P.B.")
print("=" * 80)
cursor.execute("SELECT company_id, company_name FROM companies WHERE company_name LIKE %s LIMIT 5", ('%C.R.P.B.%',))
results = cursor.fetchall()
print(f"\nFound {len(results)} companies matching 'C.R.P.B.':")
for r in results:
    print(f"  ID: {r[0]}, Name: {r[1]}")

# Search for PERICÃO
print("\n" + "=" * 80)
print("SEARCHING FOR: PERICÃO")
print("=" * 80)
cursor.execute("SELECT company_id, company_name FROM companies WHERE company_name LIKE %s LIMIT 5", ('%PERICÃO%',))
results = cursor.fetchall()
print(f"\nFound {len(results)} companies matching 'PERICÃO':")
for r in results:
    print(f"  ID: {r[0]}, Name: {r[1]}")

# Check what company_id range exists
print("\n" + "=" * 80)
print("COMPANY ID RANGE")
print("=" * 80)
cursor.execute("SELECT MIN(company_id), MAX(company_id), COUNT(*) FROM companies")
min_id, max_id, count = cursor.fetchone()
print(f"Min ID: {min_id}, Max ID: {max_id}, Total: {count}")

conn.close()
