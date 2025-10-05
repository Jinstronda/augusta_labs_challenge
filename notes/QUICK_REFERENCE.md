# Quick Reference Guide

## 🚀 Common Commands

### Testing
```bash
# Test single random incentive
python test_incentive_matching.py

# Test 10 random incentives
python test_ten_incentives.py

# Process all incentives
python batch_process_all_incentives.py

# Resume from specific incentive
python batch_process_all_incentives.py --start-from 100

# Process limited number
python batch_process_all_incentives.py --limit 50
```

### Database Operations
```bash
# Check database schema
python check_schema.py

# Check batch processing progress
python check_batch_progress.py

# View results for specific incentive
python view_incentive_results.py

# Check overall database status
python check_database_status.py
```

### Setup (First Time Only)
```bash
# 1. Initialize database tables
python setup_postgres.py
python setup_companies.py

# 2. Fill LLM-generated fields
python fill_llm_fields.py

# 3. Create company embeddings
python embed_companies_qdrant.py --full

# 4. Setup enhanced system
python setup_enhanced_system.py
```

## 📊 Understanding Results

### Rerank Scores
- **0.7 - 1.0**: Excellent match - company mission directly aligns
- **0.5 - 0.7**: Good match - relevant activities and sector
- **0.3 - 0.5**: Moderate match - some relevance
- **< 0.3**: Weak match - limited relevance

### Geographic Status
- **success_nominatim**: Found via free Nominatim API
- **success_google**: Found via Google Maps API
- **not_found**: Location not found
- **api_error**: API call failed
- **cached**: Retrieved from database cache

## 🔍 Query Composition

### Companies (Embedded)
```
"{company_name} {cae_primary_label} {trade_description_native}"
```

### Incentives (Query)
```
"{sector} {ai_description} {eligible_actions}"
```

## 📁 Key Files

### Core System
| File | Purpose |
|------|---------|
| `enhanced_incentive_matching.py` | Main matching pipeline |
| `embed_companies_qdrant.py` | Create company embeddings |
| `setup_enhanced_system.py` | Initialize system |

### Testing
| File | Purpose |
|------|---------|
| `test_incentive_matching.py` | Test single incentive |
| `test_ten_incentives.py` | Test 10 incentives |
| `batch_process_all_incentives.py` | Process all incentives |

### Utilities
| File | Purpose |
|------|---------|
| `check_schema.py` | Verify database schema |
| `check_batch_progress.py` | Monitor batch progress |
| `view_incentive_results.py` | View results |
| `check_database_status.py` | Database health |

### Documentation
| File | Purpose |
|------|---------|
| `README.md` | System overview |
| `ENHANCED_SYSTEM_DOCUMENTATION.md` | Enhanced system details |
| `SYSTEM_STATUS.md` | Current status |
| `CHANGELOG.md` | Version history |
| `QUICK_REFERENCE.md` | This file |

## 🔧 Configuration

### Environment Variables (config.env)
```bash
# Database
DB_NAME=incentives_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# APIs
GOOGLE_MAPS_API_KEY=your_key
OPEN_AI=your_openai_key

# Qdrant
QDRANT_PATH=./qdrant_storage
```

## 🐛 Troubleshooting

### "No embeddings found"
```bash
python embed_companies_qdrant.py --full
```

### "ai_description is NULL"
```bash
python fill_llm_fields.py
```

### "Location table not found"
```bash
python setup_enhanced_system.py
```

### "API rate limit exceeded"
- Wait a few minutes
- Check API key validity
- Consider using Nominatim (free)

### "Model download failed"
- Check internet connection
- Ensure ~2.5GB free disk space
- Models cache in `~/.cache/huggingface/`

## 📈 Performance Tips

### Speed Up Processing
1. Use GPU if available (10-20x faster)
2. Enable location caching (>90% hit rate)
3. Process in batches for efficiency
4. Use `--limit` for testing

### Reduce API Costs
1. Location caching reduces Google Maps calls
2. Consider switching to Nominatim (free)
3. Process incrementally with `--start-from`

### Improve Match Quality
1. Ensure ai_description is populated
2. Verify company descriptions are detailed
3. Check sector and geo_requirement are accurate
4. Review top matches and adjust if needed

## 🎯 Best Practices

### Before Processing
- [ ] Database tables initialized
- [ ] LLM fields populated (ai_description)
- [ ] Company embeddings created
- [ ] Enhanced system setup complete
- [ ] API keys configured

### During Processing
- [ ] Monitor with `check_batch_progress.py`
- [ ] Check logs for errors
- [ ] Verify results with `view_incentive_results.py`
- [ ] Resume with `--start-from` if interrupted

### After Processing
- [ ] Review match quality scores
- [ ] Verify geographic filtering accuracy
- [ ] Check for any failed incentives
- [ ] Export results if needed

## 📞 Quick Help

### "How do I test the system?"
```bash
python test_incentive_matching.py
```

### "How do I process all incentives?"
```bash
python batch_process_all_incentives.py
```

### "How do I check progress?"
```bash
python check_batch_progress.py
```

### "How do I view results?"
```bash
python view_incentive_results.py
```

### "Something's broken, where do I start?"
```bash
python check_schema.py
python check_database_status.py
```

---

**Tip**: Keep this file open while working with the system!
