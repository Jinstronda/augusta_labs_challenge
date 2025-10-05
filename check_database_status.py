"""
Check the current status of the database to understand available data for matching
"""
import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config.env')

# Database configuration
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")


def check_incentives_table():
    """Check incentives table status"""
    print("\n" + "=" * 70)
    print("INCENTIVES TABLE STATUS")
    print("=" * 70)

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Total count
    cursor.execute("SELECT COUNT(*) FROM incentives")
    total = cursor.fetchone()[0]
    print(f"\nTotal incentives: {total}")

    # Check LLM-processed fields
    cursor.execute("SELECT COUNT(*) FROM incentives WHERE sector IS NOT NULL")
    with_sector = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incentives WHERE geo_requirement IS NOT NULL")
    with_geo = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incentives WHERE eligible_actions IS NOT NULL")
    with_actions = cursor.fetchone()[0]

    print(f"\nLLM-Processed Fields:")
    print(f"  With sector: {with_sector}/{total} ({with_sector/total*100:.1f}%)")
    print(f"  With geo_requirement: {with_geo}/{total} ({with_geo/total*100:.1f}%)")
    print(f"  With eligible_actions: {with_actions}/{total} ({with_actions/total*100:.1f}%)")

    # Sample sectors
    cursor.execute("""
        SELECT sector, COUNT(*) as count
        FROM incentives
        WHERE sector IS NOT NULL
        GROUP BY sector
        ORDER BY count DESC
        LIMIT 10
    """)
    sectors = cursor.fetchall()

    if sectors:
        print("\nTop 10 Sectors:")
        for sector, count in sectors:
            print(f"  - {sector}: {count} incentives")

    # Sample incentive with all LLM fields
    cursor.execute("""
        SELECT incentive_id, title, sector, geo_requirement, eligible_actions, funding_rate, investment_eur
        FROM incentives
        WHERE sector IS NOT NULL
        LIMIT 3
    """)
    samples = cursor.fetchall()

    if samples:
        print("\nSample Processed Incentives:")
        for idx, (id, title, sector, geo, actions, funding, investment) in enumerate(samples, 1):
            print(f"\n  {idx}. [{id}] {title[:60]}...")
            print(f"     Sector: {sector}")
            print(f"     Geo: {geo}")
            print(f"     Actions: {actions[:80] if actions else 'None'}...")
            print(f"     Funding: {funding}")
            print(f"     Investment: {investment}")

    cursor.close()
    conn.close()


def check_companies_table():
    """Check companies table status"""
    print("\n" + "=" * 70)
    print("COMPANIES TABLE STATUS")
    print("=" * 70)

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Total count
    cursor.execute("SELECT COUNT(*) FROM companies")
    total = cursor.fetchone()[0]
    print(f"\nTotal companies: {total:,}")

    # With websites
    cursor.execute("SELECT COUNT(*) FROM companies WHERE website IS NOT NULL AND website != ''")
    with_websites = cursor.fetchone()[0]
    print(f"With websites: {with_websites:,} ({with_websites/total*100:.1f}%)")

    # Sample CAE labels
    cursor.execute("""
        SELECT cae_primary_label, COUNT(*) as count
        FROM companies
        WHERE cae_primary_label IS NOT NULL
        GROUP BY cae_primary_label
        ORDER BY count DESC
        LIMIT 10
    """)
    cae_labels = cursor.fetchall()

    print("\nTop 10 CAE Classifications:")
    for cae, count in cae_labels:
        print(f"  - {cae[:60]}: {count:,} companies")

    # Sample companies
    cursor.execute("""
        SELECT company_id, company_name, cae_primary_label, website
        FROM companies
        LIMIT 3
    """)
    samples = cursor.fetchall()

    print("\nSample Companies:")
    for id, name, cae, website in samples:
        print(f"\n  ID {id}: {name}")
        print(f"    CAE: {cae[:60] if cae else 'None'}...")
        print(f"    Website: {website if website else 'None'}")

    cursor.close()
    conn.close()


def check_matching_readiness():
    """Check if the database is ready for matching"""
    print("\n" + "=" * 70)
    print("MATCHING READINESS ANALYSIS")
    print("=" * 70)

    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()

    # Check incentives with complete LLM fields
    cursor.execute("""
        SELECT COUNT(*)
        FROM incentives
        WHERE sector IS NOT NULL
        AND eligible_actions IS NOT NULL
    """)
    ready_incentives = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM incentives")
    total_incentives = cursor.fetchone()[0]

    print(f"\nIncentives ready for matching: {ready_incentives}/{total_incentives}")
    print(f"  ({ready_incentives/total_incentives*100:.1f}% have sector + eligible_actions)")

    # Recommendations
    print("\n" + "=" * 70)
    print("RECOMMENDATIONS FOR MATCHING")
    print("=" * 70)

    if ready_incentives == 0:
        print("\n[!] NO INCENTIVES READY FOR MATCHING")
        print("    Action needed: Run fill_llm_fields.py to process incentives")
    elif ready_incentives < total_incentives * 0.5:
        print(f"\n[!] Only {ready_incentives/total_incentives*100:.1f}% of incentives are processed")
        print("    Recommendation: Process more incentives with fill_llm_fields.py")
    else:
        print(f"\n[OK] {ready_incentives} incentives are ready for matching!")

    print("\nSuggested matching strategy:")
    print("  1. Use 'sector' field to filter companies by CAE classification")
    print("  2. Use 'eligible_actions' for semantic search in Qdrant")
    print("  3. Optional: Filter by 'geo_requirement' (when location data available)")
    print("  4. Return top 20-40 companies ranked by similarity score")

    # Sample query for testing
    cursor.execute("""
        SELECT incentive_id, title, sector, eligible_actions
        FROM incentives
        WHERE sector IS NOT NULL
        AND eligible_actions IS NOT NULL
        ORDER BY RANDOM()
        LIMIT 1
    """)
    sample = cursor.fetchone()

    if sample:
        id, title, sector, actions = sample
        print("\nSample incentive for testing:")
        print(f"  ID: {id}")
        print(f"  Title: {title[:60]}...")
        print(f"  Sector: {sector}")
        print(f"  Actions: {actions[:100]}...")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("DATABASE STATUS CHECKER")
    print("=" * 70)

    try:
        check_incentives_table()
        check_companies_table()
        check_matching_readiness()

        print("\n" + "=" * 70)
        print("STATUS CHECK COMPLETED")
        print("=" * 70)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
