# Reverse Index: Company → Eligible Incentives

## Overview

The reverse index is a pre-computed mapping that stores each company's top 5 eligible incentives in the `companies.eligible_incentives` JSONB column. This enables fast company queries without scanning all incentives.

## How It Works

### 1. Data Source
The script reads from `incentives.top_5_companies_scored`, which contains the top 5 companies for each incentive along with their scores.

### 2. Index Building
For each incentive:
- Extract all companies from `top_5_companies_scored` JSON
- Add the incentive to each company's list
- Track the company's rank and score for that incentive

### 3. Aggregation
For each company:
- Sort all incentives by `company_score` (descending)
- Keep only the top 5 incentives
- Store as JSONB in `companies.eligible_incentives`

## Usage

### Building the Index

```bash
# Activate conda environment
conda activate turing0.1

# Run the script
python scripts/build_company_incentive_index.py
```

### Querying the Index

```python
import psycopg2
import json

# Connect to database
conn = psycopg2.connect(...)
cursor = conn.cursor()

# Get company with eligible incentives
cursor.execute("""
    SELECT company_id, company_name, eligible_incentives
    FROM companies
    WHERE company_id = %s
""", (company_id,))

company_id, company_name, incentives_json = cursor.fetchone()
incentives = json.loads(incentives_json)

# incentives is a list of dicts:
# [
#   {
#     "incentive_id": "INC001",
#     "title": "Digital Innovation Fund",
#     "rank": 1,
#     "company_score": 0.92
#   },
#   ...
# ]
```

### Example Query

```sql
-- Find companies eligible for a specific incentive
SELECT c.company_id, c.company_name, 
       jsonb_array_elements(c.eligible_incentives) as incentive
FROM companies c
WHERE c.eligible_incentives @> '[{"incentive_id": "1288"}]'::jsonb;

-- Find companies with high scores for any incentive
SELECT c.company_id, c.company_name,
       (jsonb_array_elements(c.eligible_incentives)->>'company_score')::float as score
FROM companies c
WHERE c.eligible_incentives IS NOT NULL
  AND (jsonb_array_elements(c.eligible_incentives)->>'company_score')::float > 0.8
ORDER BY score DESC;
```

## Data Structure

### companies.eligible_incentives (JSONB)

```json
[
  {
    "incentive_id": "1288",
    "title": "Digital Innovation Fund",
    "rank": 1,
    "company_score": 0.92
  },
  {
    "incentive_id": "2228",
    "title": "Green Energy Transition",
    "rank": 3,
    "company_score": 0.87
  }
]
```

### Fields

- `incentive_id` (string): Unique identifier for the incentive
- `title` (string): Incentive title
- `rank` (integer): Company's rank in the incentive's top 5 (1-5)
- `company_score` (float): Company's match score (0-1)

## Performance

### Before (scanning all incentives)
- Query time: ~500ms for 300 incentives
- Requires parsing all `top_5_companies_scored` JSON

### After (pre-computed index)
- Query time: ~5ms (single row lookup)
- Direct JSONB column access

## Statistics

Current coverage (as of last run):
- Total companies: 250,000
- Companies with eligible_incentives: 526 (0.21%)
- Incentives processed: 223
- Processing time: ~0.45 seconds

## Maintenance

### When to Rebuild

Rebuild the index after:
1. Running batch processing on new incentives
2. Updating company match scores
3. Adding new companies to the database

### Incremental Updates

For production, consider implementing incremental updates:
```python
# Update only companies affected by new incentive
def update_company_index(incentive_id):
    # Get companies from new incentive
    # Update their eligible_incentives
    # Re-sort and keep top 5
    pass
```

## Testing

Run the test suite to verify the index:

```bash
python tests/test_reverse_index.py
```

Tests verify:
- Column exists with correct type (JSONB)
- Data structure matches specification
- Incentives are sorted by score (descending)
- Top 5 limit is enforced
- Coverage statistics

## Troubleshooting

### No companies indexed
**Problem**: Script completes but no companies have `eligible_incentives`

**Solution**: Ensure incentives have `top_5_companies_scored` data:
```sql
SELECT COUNT(*) FROM incentives WHERE top_5_companies_scored IS NOT NULL;
```

If count is 0, run batch processing first:
```bash
python scripts/batch_process_with_scoring.py
```

### JSON parsing errors
**Problem**: Error parsing `top_5_companies_scored` JSON

**Solution**: Check JSON format in database:
```sql
SELECT incentive_id, top_5_companies_scored 
FROM incentives 
WHERE top_5_companies_scored IS NOT NULL 
LIMIT 1;
```

Ensure it matches the expected structure.

### Performance issues
**Problem**: Script takes too long

**Solution**: 
1. Check database connection (use connection pooling)
2. Increase batch size in `save_reverse_index()`
3. Add indexes on frequently queried columns

## Future Enhancements

1. **Incremental Updates**: Update only affected companies when new incentives are processed
2. **Caching**: Add Redis cache for frequently accessed companies
3. **Webhooks**: Trigger index rebuild automatically after batch processing
4. **Analytics**: Track which companies are queried most often
5. **Versioning**: Keep history of index changes for auditing
