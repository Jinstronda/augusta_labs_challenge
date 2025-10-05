# 🚀 Batch Processing with Company Scoring

## Quick Start

### Process ALL Incentives
```bash
python batch_process_with_scoring.py
```

### Process Limited Number (for testing)
```bash
# Process only 10 incentives
python batch_process_with_scoring.py --limit 10

# Process only 5 incentives
python batch_process_with_scoring.py --limit 5
```

---

## What This Does

The batch processor will:

1. ✅ Find all incentives that **don't have scored results yet**
2. ✅ For each incentive:
   - Semantic search (250K companies)
   - Geographic filtering (Google Maps API)
   - Geographic eligibility (GPT-5-mini)
   - **Company scoring (Universal Formula via GPT-5-mini)**
3. ✅ Save TWO sets of results:
   - `top_5_companies` - Ranked by semantic similarity
   - `top_5_companies_scored` - Ranked by Company Score

---

## Performance

### Expected Times
- **Per Incentive**: 60-120 seconds
- **10 Incentives**: ~15-20 minutes
- **100 Incentives**: ~2-3 hours
- **All Incentives**: Depends on total count

### API Usage
- **Google Maps API**: ~5-10 calls per incentive (with caching)
- **OpenAI API (GPT-5-mini)**: ~2 calls per incentive
  - 1 for geographic analysis
  - 1 for company scoring

---

## Safety Features

### Automatic Timeout Protection
- Google Maps API timeout: **100 seconds** (increased from 10s)
- If API fails, continues to next incentive
- All errors are logged

### Resume Capability
- Only processes incentives **without scored results**
- Can stop and restart anytime
- Already processed incentives are skipped

### Error Handling
- Individual failures don't stop the batch
- Full error traceback for debugging
- Summary report at the end

---

## Monitoring Progress

### Real-time Progress
The script shows:
```
[PROGRESS] 5/100 completed
[PROGRESS] Success: 4, Failed: 1, Skipped: 0
[PROGRESS] Elapsed: 8.5m, Est. remaining: 162.5m
```

### Check Progress in Another Terminal
```bash
python check_batch_progress.py
```

### View Results
```bash
python verify_scoring.py
```

---

## Output Format

### Database Columns

#### `top_5_companies` (Semantic Ranking)
```json
{
  "companies": [
    {
      "id": 12345,
      "rank": 1,
      "semantic_score": 0.9244,
      "name": "Company Name",
      "cae_classification": "...",
      "website": "...",
      "location_address": "...",
      "activities": "..."
    }
  ],
  "total_candidates_searched": 10,
  "processing_time": 74.95,
  "processed_at": "2025-01-15T10:30:00",
  "geographic_eligible_count": 5
}
```

#### `top_5_companies_scored` (Company Score Ranking)
```json
{
  "companies": [
    {
      "id": 12345,
      "rank": 1,
      "company_score": 0.6955,
      "semantic_score": 0.9244,
      "score_components": {
        "s": 1.0,
        "m": 0.41,
        "g": 1.0,
        "o": 0.70,
        "org_direction": 0,
        "w": 0
      },
      "name": "Company Name",
      "cae_classification": "...",
      "website": "...",
      "location_address": "...",
      "activities": "..."
    }
  ],
  "processing_time": 74.95,
  "processed_at": "2025-01-15T10:30:00",
  "scoring_formula": "0.50S + 0.20M + 0.10G + 0.15O' + 0.05W"
}
```

---

## Troubleshooting

### "No incentives to process"
✅ All incentives already have scored results!

### "Google Maps API timeout"
- Timeout increased to 100 seconds
- If still timing out, check internet connection
- Script will continue to next incentive

### "OpenAI API error"
- Check API key in `config.env`
- Check API quota/billing
- Script will continue to next incentive

### "Out of memory"
- Close other applications
- Process in smaller batches with `--limit`

### Script stops unexpectedly
- Check error message in terminal
- Resume by running the same command again
- Already processed incentives will be skipped

---

## Cost Estimation

### Google Maps API
- **Free tier**: 1,000 requests/day
- **Cost**: $17 per 1,000 requests after free tier
- **With caching**: ~90% reduction after first run

### OpenAI API (GPT-5-mini)
- **Cost**: Very low (GPT-5-mini is cheap)
- **Estimate**: ~$0.01-0.02 per incentive
- **100 incentives**: ~$1-2

---

## Best Practices

### First Run
```bash
# Test with small batch first
python batch_process_with_scoring.py --limit 5

# Verify results
python verify_scoring.py

# If good, process all
python batch_process_with_scoring.py
```

### Long Running Process
```bash
# Run in background (Windows)
start /B python batch_process_with_scoring.py > batch_log.txt 2>&1

# Check progress
python check_batch_progress.py

# View log
type batch_log.txt
```

### Resume After Interruption
```bash
# Just run again - it will skip already processed incentives
python batch_process_with_scoring.py
```

---

## Verification

### Check Results
```bash
# View latest scored incentive
python verify_scoring.py

# Check overall progress
python check_batch_progress.py

# View specific incentive
python view_incentive_results.py
```

### SQL Queries
```sql
-- Count scored incentives
SELECT COUNT(*) FROM incentives WHERE top_5_companies_scored IS NOT NULL;

-- View scored results
SELECT incentive_id, title, top_5_companies_scored 
FROM incentives 
WHERE top_5_companies_scored IS NOT NULL 
LIMIT 5;

-- Compare semantic vs scored rankings
SELECT 
    incentive_id,
    title,
    top_5_companies->'companies'->0->>'name' as semantic_top,
    top_5_companies_scored->'companies'->0->>'name' as scored_top
FROM incentives
WHERE top_5_companies_scored IS NOT NULL;
```

---

## Full Command Reference

```bash
# Process all unscored incentives
python batch_process_with_scoring.py

# Process with limit
python batch_process_with_scoring.py --limit 10

# Check progress
python check_batch_progress.py

# Verify results
python verify_scoring.py

# View specific incentive
python view_incentive_results.py

# Test single incentive
python test_scoring.py
```

---

## Support

If you encounter issues:
1. Check error message in terminal
2. Verify API keys in `config.env`
3. Check database connection
4. Review `EQUATION.md` for scoring formula
5. Check `TROUBLESHOOTING.md` for common issues

---

**Ready to run?**
```bash
python batch_process_with_scoring.py --limit 5
```

This will process 5 incentives as a test run (~5-10 minutes).
