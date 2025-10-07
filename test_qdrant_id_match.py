"""Test if Qdrant point IDs match PostgreSQL company_ids"""
import psycopg2
from dotenv import load_dotenv
import os
from qdrant_client import QdrantClient

load_dotenv('config.env')

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT')
)
cursor = conn.cursor()

# Connect to Qdrant
qdrant_client = QdrantClient(path="./qdrant_storage")

print("=" * 80)
print("TESTING QDRANT POINT ID vs POSTGRESQL COMPANY_ID MATCH")
print("=" * 80)

# Test a few point IDs
test_point_ids = [0, 1, 10, 100, 1000, 10000]

for point_id in test_point_ids:
    # Get point from Qdrant
    try:
        points = qdrant_client.retrieve(
            collection_name="companies",
            ids=[point_id],
            with_payload=True
        )
        
        if points:
            point = points[0]
            qdrant_name = point.payload.get('company_name', 'N/A')
            
            # Get company from PostgreSQL using point_id as company_id
            cursor.execute(
                "SELECT company_id, company_name FROM companies WHERE company_id = %s",
                (point_id,)
            )
            pg_result = cursor.fetchone()
            
            if pg_result:
                pg_id, pg_name = pg_result
                match = "✓ MATCH" if qdrant_name == pg_name else "✗ MISMATCH"
                print(f"\nPoint ID: {point_id}")
                print(f"  Qdrant: {qdrant_name}")
                print(f"  PostgreSQL: {pg_name}")
                print(f"  {match}")
            else:
                print(f"\nPoint ID: {point_id}")
                print(f"  Qdrant: {qdrant_name}")
                print(f"  PostgreSQL: NOT FOUND")
                print(f"  ✗ MISMATCH")
    except Exception as e:
        print(f"\nPoint ID: {point_id} - Error: {e}")

# Test the specific case: C.R.P.B. (company_id 13)
print("\n" + "=" * 80)
print("SPECIFIC TEST: C.R.P.B. (company_id 13)")
print("=" * 80)

try:
    points = qdrant_client.retrieve(
        collection_name="companies",
        ids=[13],
        with_payload=True
    )
    
    if points:
        point = points[0]
        print(f"Qdrant point 13: {point.payload.get('company_name', 'N/A')}")
    else:
        print("Point 13 not found in Qdrant")
except Exception as e:
    print(f"Error: {e}")

cursor.execute("SELECT company_name FROM companies WHERE company_id = 13")
result = cursor.fetchone()
if result:
    print(f"PostgreSQL company_id 13: {result[0]}")

conn.close()

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
print("If IDs don't match, we need to:")
print("1. Store company_id in Qdrant payload, OR")
print("2. Use PostgreSQL for SPECIFIC_COMPANY queries")
