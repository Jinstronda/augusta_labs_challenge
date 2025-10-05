# Getting Started

## Prerequisites

1. **Python 3.11+** installed
2. **PostgreSQL** database running
3. **API Keys**:
   - Google Maps API key
   - OpenAI API key (for GPT-5-mini)
4. **Data Files**:
   - Company data CSV
   - Incentive data CSV

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd incentive-matching
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create `config.env` file:
```bash
# Database
DB_NAME=incentives_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# APIs
GOOGLE_MAPS_API_KEY=your_google_maps_key
OPEN_AI=your_openai_key

# Qdrant
QDRANT_PATH=./qdrant_storage
```

## First-Time Setup

Run these scripts in order:

### 1. Setup Database Tables
```bash
python scripts/setup_postgres.py
python scripts/setup_companies.py
```

This creates the `incentives` and `companies` tables.

### 2. Populate LLM Fields
```bash
python scripts/fill_llm_fields.py
```

This uses GPT-5-mini to extract:
- `ai_description` - Processed incentive description
- `sector` - Industry classification
- `geo_requirement` - Geographic scope
- `eligible_actions` - Eligible activities

### 3. Create Company Embeddings
```bash
python scripts/embed_companies_qdrant.py --full
```

This creates 250K company embeddings (~400MB, takes 30-60 minutes).

### 4. Verify System
```bash
python scripts/setup_enhanced_system.py
```

This checks:
- ✅ Database schema
- ✅ API connections
- ✅ Qdrant collection
- ✅ Model loading

## Testing

### Test Single Incentive
```bash
python tests/test_scoring.py
```

Expected output:
- Processing time: ~60-120 seconds
- 5 companies found
- Both semantic and scored rankings

### Test Batch of 10
```bash
python tests/test_ten_incentives.py
```

Expected output:
- Processing time: ~10-20 minutes
- 10 incentives processed
- Results saved to database

## Production Use

### Process All Incentives
```bash
# Test with 5 first
python scripts/batch_process_with_scoring.py --limit 5

# If good, process all
python scripts/batch_process_with_scoring.py
```

### Monitor Progress
```bash
# In another terminal
python scripts/check_batch_progress.py
```

### View Results
```bash
python tests/verify_scoring.py
```

## Project Structure

```
incentive-matching/
├── enhanced_incentive_matching.py    # Core engine
├── scripts/                          # Setup & processing
├── tests/                            # Test scripts
├── docs/                             # Documentation
├── data/                             # Data files
└── qdrant_storage/                   # Vector database
```

See `PROJECT_STRUCTURE.md` for details.

## Key Files

### Core
- `enhanced_incentive_matching.py` - Main matching engine
- `requirements.txt` - Python dependencies
- `config.env` - Configuration

### Documentation
- `README.md` - Main documentation
- `EQUATION.md` - Scoring formula
- `FINAL_COMMAND.md` - Quick commands
- `PROJECT_STRUCTURE.md` - File organization
- `GETTING_STARTED.md` - This file

### Scripts
- `setup_*.py` - Database setup
- `batch_process_with_scoring.py` - Main processing
- `check_*.py` - Monitoring tools
- `view_incentive_results.py` - View results

### Tests
- `test_scoring.py` - Test single incentive
- `test_ten_incentives.py` - Test batch
- `verify_scoring.py` - Verify results

## Common Issues

### "No module named 'enhanced_incentive_matching'"
- Make sure you're running from the project root
- Scripts automatically add parent directory to path

### "Google Maps API timeout"
- Timeout is set to 100 seconds
- Check internet connection
- Script will continue to next incentive

### "OpenAI API error"
- Check API key in `config.env`
- Check API quota/billing
- Script will continue to next incentive

### "Qdrant collection not found"
- Run: `python scripts/embed_companies_qdrant.py --full`
- This creates the vector database

### "Database connection error"
- Check PostgreSQL is running
- Verify credentials in `config.env`
- Check database exists

## Performance

### Expected Times
- **Single incentive**: 60-120 seconds
- **10 incentives**: 10-20 minutes
- **100 incentives**: 2-3 hours

### Optimization
- Use GPU for 10-20x faster embeddings
- Caching reduces API calls by 90%
- Process in batches for efficiency

## Cost Estimates

### Per 100 Incentives
- **Google Maps API**: $0-8.50 (first run), ~$1 (cached)
- **OpenAI GPT-5-mini**: ~$1-2
- **Total**: $2-10

### Rate Limits
- **Google Maps**: Per minute (no session limits)
- **OpenAI**: Per minute (depends on tier)

## Next Steps

1. ✅ Complete setup (above)
2. ✅ Test with 5 incentives
3. ✅ Verify results
4. ✅ Process all incentives
5. ✅ Monitor progress
6. ✅ Analyze results

## Support

- **Documentation**: See `docs/` folder
- **Issues**: Check `docs/TROUBLESHOOTING.md`
- **Structure**: See `PROJECT_STRUCTURE.md`
- **Commands**: See `FINAL_COMMAND.md`

## Quick Reference

```bash
# Setup
python scripts/setup_postgres.py
python scripts/setup_companies.py
python scripts/fill_llm_fields.py
python scripts/embed_companies_qdrant.py --full
python scripts/setup_enhanced_system.py

# Test
python tests/test_scoring.py

# Process
python scripts/batch_process_with_scoring.py --limit 5

# Monitor
python scripts/check_batch_progress.py

# View
python tests/verify_scoring.py
```

---

**Ready to start?**
```bash
python scripts/setup_postgres.py
```
