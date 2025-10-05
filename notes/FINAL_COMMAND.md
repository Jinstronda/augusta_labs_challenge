# 🎯 FINAL COMMAND - Run Batch Scoring

## ✅ Ready to Run

Everything is set up and tested. Here's your command:

```bash
python batch_process_with_scoring.py
```

---

## 🧪 Test First (Recommended)

Process just 5 incentives to verify everything works:

```bash
python scripts/batch_process_with_scoring.py --limit 5
```

**Expected output:**
- Processing time: ~5-10 minutes
- Success: 5 incentives
- Results saved to both columns

---

## 📊 What Gets Saved

### Two Result Columns

1. **`top_5_companies`** - Semantic ranking (already exists)
   - Ranked by BGE reranker scores
   - Pure semantic similarity

2. **`top_5_companies_scored`** - Company Score ranking (NEW)
   - Ranked by Universal Company Match Formula
   - Formula: `0.50S + 0.20M + 0.10G + 0.15O' + 0.05W`
   - Includes score components breakdown

---

## 🔍 Verify Results

After processing, check the results:

```bash
python verify_scoring.py
```

**Shows:**
- Latest scored incentive
- Top 5 companies by semantic score
- Top 5 companies by company score
- Score components breakdown

---

## 📈 Monitor Progress

While batch is running, check progress in another terminal:

```bash
python check_batch_progress.py
```

---

## ⚙️ System Features

### ✅ Automatic Timeout Protection
- Google Maps API: 100 second timeout per request
- Rate limits: Per minute (handled by API, not code)
- No artificial session limits
- Handles API failures gracefully
- Continues to next incentive on error

### ✅ Resume Capability
- Only processes incentives without `top_5_companies_scored`
- Can stop and restart anytime
- Already processed incentives are skipped

### ✅ Error Handling
- Individual failures don't stop the batch
- Full error logging
- Summary report at the end

---

## 💰 Cost Estimate

### For 100 Incentives

**Google Maps API:**
- First run: ~500-1000 calls ($0-$8.50)
- Subsequent runs: ~50-100 calls (90% cached)
- Rate limit: Per minute (no session limits)

**OpenAI API (GPT-5-mini):**
- ~200 calls total
- Cost: ~$1-2

**Total: ~$2-10 for 100 incentives**

---

## 🎯 The Formula

```
FINAL SCORE = 0.50S + 0.20M + 0.10G + 0.15O′ + 0.05W
```

Where:
- **S** (0.50): Semantic Similarity - Core alignment
- **M** (0.20): CAE/Activity Overlap - Sectoral relevance
- **G** (0.10): Geographic Fit - Location suitability
- **O′** (0.15): Contextual Organizational Fit - Size/type match
- **W** (0.05): Website Presence - Digital maturity

See `EQUATION.md` for full details.

---

## 🚀 Full Workflow

```bash
# 1. Test with 5 incentives
python batch_process_with_scoring.py --limit 5

# 2. Verify results
python verify_scoring.py

# 3. If good, process all
python batch_process_with_scoring.py

# 4. Monitor progress (in another terminal)
python check_batch_progress.py

# 5. View final results
python verify_scoring.py
```

---

## 📝 Example Output

```
================================================================================
BATCH PROCESSING WITH COMPANY SCORING
================================================================================
Total incentives to process: 150
Max candidates per incentive: 50
================================================================================

[INIT] Initializing enhanced matching pipeline...

================================================================================
PROCESSING INCENTIVE 1/150
================================================================================
ID: 1330
Title: Requalificar as instalações dos Serviços Locais de Saúde Mental...
================================================================================

[PIPELINE] Searching with 10 candidates...
[LOCATION] Enriching 10 companies with location data...
[GEO ANALYSIS] 9/10 companies eligible
[SCORING] Calculating company scores for 5 companies...

✅ SUCCESS: Found 5 companies
   Processing time: 74.95s

[PROGRESS] 1/150 completed
[PROGRESS] Success: 1, Failed: 0, Skipped: 0
[PROGRESS] Elapsed: 1.2m, Est. remaining: 186.8m
```

---

## 🎉 Ready?

Run this command to start:

```bash
python batch_process_with_scoring.py --limit 5
```

Or go all-in:

```bash
python batch_process_with_scoring.py
```

---

## 📚 Documentation

- `EQUATION.md` - Scoring formula details
- `RUN_BATCH_SCORING.md` - Complete guide
- `QUICK_REFERENCE.md` - Quick commands
- `SYSTEM_STATUS.md` - System overview

---

**Good luck! 🚀**
