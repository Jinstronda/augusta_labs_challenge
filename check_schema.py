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

print("Incentives table schema:")
cursor.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'incentives' 
    ORDER BY ordinal_position
""")

for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")

print("\nCompanies table schema:")
cursor.execute("""
    SELECT column_name, data_type, is_nullable, column_default
    FROM information_schema.columns 
    WHERE table_name = 'companies' 
    ORDER BY ordinal_position
""")

for row in cursor.fetchall():
    print(f"  {row[0]}: {row[1]} (nullable: {row[2]}, default: {row[3]})")

cursor.close()
conn.close()