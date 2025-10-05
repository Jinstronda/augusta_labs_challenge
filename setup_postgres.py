"""
Simple PostgreSQL setup script for incentives data
"""
import os
import pandas as pd
import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

# Load environment variables from config.env file
load_dotenv('config.env')

# Database configuration from environment variables
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def create_database():
    """Create the database if it doesn't exist"""
    try:
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
            print(f"Database '{DB_NAME}' created successfully")
        else:
            print(f"Database '{DB_NAME}' already exists")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")
        raise

def create_table():
    """Create the incentives table"""
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
        cursor.execute("DROP TABLE IF EXISTS incentives CASCADE")
        
        # Create table with all columns
        create_table_query = """
        CREATE TABLE incentives (
            incentive_id VARCHAR(255) PRIMARY KEY,
            title TEXT,
            description TEXT,
            ai_description TEXT,
            eligibility_criteria TEXT,
            document_urls TEXT,
            publication_date TIMESTAMP,
            start_date TIMESTAMP,
            end_date TIMESTAMP,
            total_budget NUMERIC,
            source_link TEXT,
            -- New columns to be filled by LLM later
            sector TEXT,
            geo_requirement TEXT,
            eligible_actions TEXT,
            funding_rate TEXT,
            investment_eur TEXT
        )
        """
        
        cursor.execute(create_table_query)
        conn.commit()
        print("Table 'incentives' created successfully")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")
        raise

def load_data():
    """Load data from CSV into PostgreSQL"""
    try:
        print("Reading CSV file...")
        df = pd.read_csv('filtered_incentives0.3.csv')
        
        print(f"CSV contains {len(df)} rows")
        
        # Map CSV columns to database columns
        df_mapped = pd.DataFrame({
            'incentive_id': df['incentive_project_id'].astype(str),
            'title': df['title'],
            'description': df['description'],
            'ai_description': df['ai_description'],
            'eligibility_criteria': df['eligibility_criteria'],
            'document_urls': df['document_urls'],
            'publication_date': pd.to_datetime(df['date_publication'], format='%d/%m/%Y %H:%M', errors='coerce'),
            'start_date': pd.to_datetime(df['date_start'], format='%d/%m/%Y %H:%M', errors='coerce'),
            'end_date': pd.to_datetime(df['date_end'], format='%d/%m/%Y %H:%M', errors='coerce'),
            'total_budget': pd.to_numeric(df['total_budget'], errors='coerce'),
            'source_link': df['source_link']
        })
        
        # Replace NaT and NaN with None for PostgreSQL compatibility
        df_mapped = df_mapped.where(pd.notna(df_mapped), None)
        
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
        print("Inserting data into database...")
        insert_query = """
        INSERT INTO incentives (
            incentive_id, title, description, ai_description, eligibility_criteria, 
            document_urls, publication_date, start_date, end_date, total_budget, source_link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (incentive_id) DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            ai_description = EXCLUDED.ai_description,
            eligibility_criteria = EXCLUDED.eligibility_criteria,
            document_urls = EXCLUDED.document_urls,
            publication_date = EXCLUDED.publication_date,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date,
            total_budget = EXCLUDED.total_budget,
            source_link = EXCLUDED.source_link
        """
        
        batch_size = 100
        for i in range(0, len(df_mapped), batch_size):
            batch = df_mapped.iloc[i:i+batch_size]
            # Convert to list of tuples, replacing NaT/NaN with None
            data = []
            for row in batch.values:
                clean_row = tuple(None if pd.isna(val) else val for val in row)
                data.append(clean_row)
            cursor.executemany(insert_query, data)
            conn.commit()
            print(f"Inserted {min(i+batch_size, len(df_mapped))}/{len(df_mapped)} rows")
        
        print(f"Successfully loaded {len(df_mapped)} rows into the database")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error loading data: {e}")
        raise

def main():
    """Main setup function"""
    print("=" * 50)
    print("PostgreSQL Incentives Database Setup")
    print("=" * 50)
    
    print("\n1. Creating database...")
    create_database()
    
    print("\n2. Creating table...")
    create_table()
    
    print("\n3. Loading data from CSV...")
    load_data()
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("=" * 50)
    print(f"\nConnection details:")
    print(f"  Database: {DB_NAME}")
    print(f"  Host: {DB_HOST}")
    print(f"  Port: {DB_PORT}")
    print(f"  User: {DB_USER}")
    print(f"  Password: {DB_PASSWORD}")

if __name__ == "__main__":
    main()
