# Project Structure

```
incentive-matching/
│
├── enhanced_incentive_matching.py    # Core matching engine
├── requirements.txt                   # Python dependencies
├── config.env                         # Configuration (API keys, DB credentials)
│
├── README.md                          # Main documentation
├── EQUATION.md                        # Scoring formula details
├── FINAL_COMMAND.md                   # Quick start guide
│
├── data/                              # Data files
│   ├── raw/                          # Original data files
│   │   └── Data_Preview.xlsx         # Excel preview of data
│   ├── processed/                    # Processed data files
│   │   ├── ai_descriptions.csv       # LLM-generated descriptions
│   │   ├── eligibility_criteria.csv  # Extracted criteria
│   │   ├── FILTERED_COMPANIES.csv    # Filtered company list
│   │   └── filtered_incentives0.3.csv # Filtered incentives
│   └── test_*.json                   # Test incentive samples
│
├── scripts/                           # Utility scripts
│   ├── setup_postgres.py             # Initialize incentives table
│   ├── setup_companies.py            # Initialize companies table
│   ├── fill_llm_fields.py            # Populate LLM fields
│   ├── embed_companies_qdrant.py     # Create company embeddings
│   ├── setup_enhanced_system.py      # Setup enhanced system
│   ├── batch_process_all_incentives.py      # Batch process (semantic only)
│   ├── batch_process_with_scoring.py        # Batch process (with scoring)
│   ├── check_schema.py               # Verify database schema
│   ├── check_batch_progress.py       # Monitor batch progress
│   ├── check_database_status.py      # Database health check
│   └── view_incentive_results.py     # View results
│
├── tests/                             # Test scripts
│   ├── test_incentive_matching.py    # Test basic matching
│   ├── test_scoring.py               # Test scoring system
│   ├── test_ten_incentives.py        # Test batch of 10
│   └── verify_scoring.py             # Verify scored results
│
├── docs/                              # Documentation
│   ├── CHANGELOG.md                  # Version history
│   ├── COMPANIES_SCHEMA.md           # Company data schema
│   ├── DOCUMENTATION_UPDATE.md       # Documentation changes
│   ├── ENHANCED_SYSTEM_DOCUMENTATION.md  # Enhanced system details
│   ├── IMPLEMENTATION_SUMMARY.md     # Implementation overview
│   ├── QUICK_REFERENCE.md            # Quick command reference
│   ├── RUN_BATCH_SCORING.md          # Batch processing guide
│   ├── SYSTEM_OVERVIEW.md            # System architecture
│   └── SYSTEM_STATUS.md              # Current system status
│
├── notes/                             # Personal notes
│   ├── somestuff.md                  # Misc notes
│   └── theplan.MD                    # Planning notes
│
└── qdrant_storage/                    # Vector database storage
    └── collection/                    # Company embeddings (250K vectors)
```

## File Purposes

### Core Files

**enhanced_incentive_matching.py**
- Main matching engine
- Contains all classes: DatabaseManager, LocationService, GeographicAnalyzer, CompanyScorer, EnhancedMatchingPipeline
- Single source of truth for matching logic

**requirements.txt**
- Python package dependencies
- Install with: `pip install -r requirements.txt`

**config.env**
- Database credentials
- API keys (Google Maps, OpenAI)
- Configuration settings

### Setup Scripts (Run Once)

1. **setup_postgres.py** - Create incentives table
2. **setup_companies.py** - Create companies table
3. **fill_llm_fields.py** - Populate ai_description and other LLM fields
4. **embed_companies_qdrant.py** - Create 250K company embeddings
5. **setup_enhanced_system.py** - Verify system is ready

### Processing Scripts (Main Workflow)

**batch_process_with_scoring.py**
- Process all incentives with company scoring
- Saves to both `top_5_companies` and `top_5_companies_scored`
- Resume capability
- Progress monitoring

**batch_process_all_incentives.py**
- Legacy: Process with semantic matching only
- Use `batch_process_with_scoring.py` instead

### Monitoring Scripts

**check_batch_progress.py**
- View processing progress
- Statistics on completed incentives
- Average processing time

**check_schema.py**
- Verify database schema
- Check for required columns
- Validate data types

**check_database_status.py**
- Overall database health
- Connection status
- Table counts

**view_incentive_results.py**
- View results for specific incentive
- Interactive selection
- Detailed company information

### Test Scripts

**test_incentive_matching.py**
- Test basic semantic matching
- Single random incentive
- No geographic filtering

**test_scoring.py**
- Test full pipeline with scoring
- Single random incentive
- Includes geographic filtering and scoring

**test_ten_incentives.py**
- Test batch of 10 incentives
- Full pipeline
- Performance testing

**verify_scoring.py**
- View latest scored results
- Compare semantic vs scored rankings
- Show score components

### Data Files

**data/raw/**
- Original, unprocessed data
- Excel files, raw CSVs

**data/processed/**
- Processed data ready for use
- LLM-generated fields
- Filtered datasets

**data/test_*.json**
- Sample incentives for testing
- Used in test scripts

### Documentation

**README.md** - Start here
**EQUATION.md** - Scoring formula
**FINAL_COMMAND.md** - Quick start
**docs/** - Detailed documentation

## Typical Workflow

### First Time Setup
```bash
python scripts/setup_postgres.py
python scripts/setup_companies.py
python scripts/fill_llm_fields.py
python scripts/embed_companies_qdrant.py --full
python scripts/setup_enhanced_system.py
```

### Process Incentives
```bash
# Test with 5
python scripts/batch_process_with_scoring.py --limit 5

# Process all
python scripts/batch_process_with_scoring.py
```

### Monitor & Verify
```bash
# Check progress
python scripts/check_batch_progress.py

# View results
python tests/verify_scoring.py
```

### Testing
```bash
# Test single incentive
python tests/test_scoring.py

# Test batch of 10
python tests/test_ten_incentives.py
```

## Key Directories

**qdrant_storage/** - Vector database (400MB for 250K companies)
**__pycache__/** - Python bytecode cache (auto-generated)
**.git/** - Git version control
**.claude/** - Claude AI configuration
**.cursor/** - Cursor IDE configuration

## Notes

- Keep `config.env` secure (contains API keys)
- `qdrant_storage/` can be deleted and regenerated
- `__pycache__/` can be deleted (auto-regenerates)
- `notes/` is for personal use only
- `data/raw/` should not be modified
- `data/processed/` can be regenerated from raw data
