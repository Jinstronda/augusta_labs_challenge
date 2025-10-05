"""
Setup PostgreSQL table for companies and load data from CSV
"""
import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Database configuration
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def create_companies_table():
    """Create the companies table with proper schema"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        # Drop table if exists (for clean setup)
        cursor.execute("DROP TABLE IF EXISTS companies CASCADE")
        
        # Create companies table
        create_table_query = """
        CREATE TABLE companies (
            company_id SERIAL PRIMARY KEY,
            company_name TEXT NOT NULL,
            cae_primary_label TEXT,
            trade_description_native TEXT,
            website TEXT,
            -- Fields for future Google Maps data
            location_address TEXT,
            location_lat NUMERIC,
            location_lon NUMERIC,
            location_region TEXT,
            -- Tracking fields
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("✓ Table 'companies' created successfully")
        
        # Create indexes for fast filtering
        print("Creating indexes...")
        cursor.execute("CREATE INDEX idx_companies_cae ON companies(cae_primary_label)")
        cursor.execute("CREATE INDEX idx_companies_region ON companies(location_region)")
        conn.commit()
        print("✓ Indexes created successfully")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error creating table: {e}")
        raise


def load_companies_data():
    """Load companies from CSV into PostgreSQL"""
    try:
        print("\nReading FILTERED_COMPANIES.csv...")
        df = pd.read_csv('FILTERED_COMPANIES.csv')
        
        print(f"✓ CSV contains {len(df)} companies")
        
        # Replace NaN with None for PostgreSQL compatibility
        df = df.where(pd.notna(df), None)
        
        # Connect to database
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        # Insert data in batches
        print("Inserting companies into database...")
        insert_query = """
        INSERT INTO companies (
            company_name, cae_primary_label, trade_description_native, website
        ) VALUES (%s, %s, %s, %s)
        """
        
        batch_size = 500
        for i in range(0, len(df), batch_size):
            batch = df.iloc[i:i+batch_size]
            
            # Convert to list of tuples, replacing NaT/NaN with None
            data = []
            for row in batch.values:
                clean_row = tuple(None if pd.isna(val) else val for val in row)
                data.append(clean_row)
            
            cursor.executemany(insert_query, data)
            conn.commit()
            
            if (i + batch_size) % 10000 == 0 or (i + batch_size) >= len(df):
                print(f"  Inserted {min(i+batch_size, len(df)):,}/{len(df):,} companies")
        
        print(f"✓ Successfully loaded {len(df):,} companies into the database")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error loading data: {e}")
        raise


def verify_data():
    """Verify the loaded data"""
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()
        
        # Get total count
        cursor.execute("SELECT COUNT(*) FROM companies")
        total = cursor.fetchone()[0]
        
        # Get count with websites
        cursor.execute("SELECT COUNT(*) FROM companies WHERE website IS NOT NULL AND website != ''")
        with_websites = cursor.fetchone()[0]
        
        # Get sample records
        cursor.execute("""
            SELECT company_id, company_name, cae_primary_label, website
            FROM companies
            LIMIT 3
        """)
        samples = cursor.fetchall()
        
        print("\n" + "=" * 70)
        print("Data Verification")
        print("=" * 70)
        print(f"\nTotal Companies: {total:,}")
        print(f"With Websites: {with_websites:,} ({with_websites/total*100:.1f}%)")
        print(f"Without Websites: {total-with_websites:,} ({(total-with_websites)/total*100:.1f}%)")
        
        print("\nSample Records:")
        print("-" * 70)
        for record in samples:
            print(f"\nID: {record[0]}")
            print(f"  Name: {record[1]}")
            print(f"  CAE: {record[2][:60]}..." if record[2] and len(record[2]) > 60 else f"  CAE: {record[2]}")
            print(f"  Website: {record[3] if record[3] else 'None'}")
        
        print("\n" + "=" * 70)
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"✗ Error verifying data: {e}")
        raise


def main():
    """Main setup function"""
    print("=" * 70)
    print("PostgreSQL Companies Table Setup")
    print("=" * 70)
    
    print("\n1. Creating companies table...")
    create_companies_table()
    
    print("\n2. Loading data from FILTERED_COMPANIES.csv...")
    load_companies_data()
    
    print("\n3. Verifying loaded data...")
    verify_data()
    
    print("\n" + "=" * 70)
    print("✓ Setup completed successfully!")
    print("=" * 70)
    print(f"\nDatabase: {DB_NAME}")
    print(f"Table: companies")
    print(f"Ready for: RAG pipeline with Qdrant + LlamaIndex")


if __name__ == "__main__":
    main()
