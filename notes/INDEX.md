# Documentation Index

## 🚀 Start Here

1. **[GETTING_STARTED.md](GETTING_STARTED.md)** - Complete setup guide
2. **[FINAL_COMMAND.md](FINAL_COMMAND.md)** - Quick commands
3. **[README.md](README.md)** - System overview

## 📚 Core Documentation

### System Overview
- **[README.md](README.md)** - Main documentation (Paul Graham style)
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - File organization
- **[EQUATION.md](EQUATION.md)** - Scoring formula details

### Getting Started
- **[GETTING_STARTED.md](GETTING_STARTED.md)** - Step-by-step setup
- **[FINAL_COMMAND.md](FINAL_COMMAND.md)** - Quick start commands
- **[docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Command reference

### Implementation
- **[docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)** - What was built
- **[docs/SYSTEM_STATUS.md](docs/SYSTEM_STATUS.md)** - Current status
- **[docs/CHANGELOG.md](docs/CHANGELOG.md)** - Version history

## 🔧 Technical Documentation

### System Architecture
- **[docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md)** - Architecture details
- **[docs/ENHANCED_SYSTEM_DOCUMENTATION.md](docs/ENHANCED_SYSTEM_DOCUMENTATION.md)** - Enhanced features
- **[docs/COMPANIES_SCHEMA.md](docs/COMPANIES_SCHEMA.md)** - Data schema

### Guides
- **[docs/RUN_BATCH_SCORING.md](docs/RUN_BATCH_SCORING.md)** - Batch processing guide
- **[docs/DOCUMENTATION_UPDATE.md](docs/DOCUMENTATION_UPDATE.md)** - Documentation changes

## 📁 File Organization

```
incentive-matching/
│
├── Core Files
│   ├── enhanced_incentive_matching.py    # Main engine
│   ├── requirements.txt                   # Dependencies
│   └── config.env                         # Configuration
│
├── Documentation (Root)
│   ├── README.md                          # Main docs
│   ├── GETTING_STARTED.md                 # Setup guide
│   ├── FINAL_COMMAND.md                   # Quick commands
│   ├── EQUATION.md                        # Scoring formula
│   ├── PROJECT_STRUCTURE.md               # File organization
│   └── INDEX.md                           # This file
│
├── docs/                                  # Detailed docs
│   ├── CHANGELOG.md
│   ├── COMPANIES_SCHEMA.md
│   ├── DOCUMENTATION_UPDATE.md
│   ├── ENHANCED_SYSTEM_DOCUMENTATION.md
│   ├── IMPLEMENTATION_SUMMARY.md
│   ├── QUICK_REFERENCE.md
│   ├── RUN_BATCH_SCORING.md
│   ├── SYSTEM_OVERVIEW.md
│   └── SYSTEM_STATUS.md
│
├── scripts/                               # Utility scripts
│   ├── setup_postgres.py
│   ├── setup_companies.py
│   ├── fill_llm_fields.py
│   ├── embed_companies_qdrant.py
│   ├── setup_enhanced_system.py
│   ├── batch_process_all_incentives.py
│   ├── batch_process_with_scoring.py
│   ├── check_schema.py
│   ├── check_batch_progress.py
│   ├── check_database_status.py
│   └── view_incentive_results.py
│
├── tests/                                 # Test scripts
│   ├── test_incentive_matching.py
│   ├── test_scoring.py
│   ├── test_ten_incentives.py
│   └── verify_scoring.py
│
├── data/                                  # Data files
│   ├── raw/                              # Original data
│   ├── processed/                        # Processed data
│   └── test_*.json                       # Test samples
│
└── notes/                                 # Personal notes
    ├── somestuff.md
    └── theplan.MD
```

## 🎯 By Task

### First-Time Setup
1. [GETTING_STARTED.md](GETTING_STARTED.md) - Complete guide
2. [docs/SYSTEM_STATUS.md](docs/SYSTEM_STATUS.md) - System requirements

### Running the System
1. [FINAL_COMMAND.md](FINAL_COMMAND.md) - Quick commands
2. [docs/RUN_BATCH_SCORING.md](docs/RUN_BATCH_SCORING.md) - Batch guide
3. [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Command reference

### Understanding the System
1. [README.md](README.md) - Overview
2. [EQUATION.md](EQUATION.md) - Scoring formula
3. [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md) - Architecture

### Troubleshooting
1. [GETTING_STARTED.md](GETTING_STARTED.md#common-issues) - Common issues
2. [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md#troubleshooting) - Quick fixes
3. [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - File locations

### Development
1. [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md) - What was built
2. [docs/CHANGELOG.md](docs/CHANGELOG.md) - Version history
3. [docs/DOCUMENTATION_UPDATE.md](docs/DOCUMENTATION_UPDATE.md) - Doc changes

## 📊 By Role

### For Users
- Start: [GETTING_STARTED.md](GETTING_STARTED.md)
- Quick: [FINAL_COMMAND.md](FINAL_COMMAND.md)
- Reference: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

### For Developers
- Overview: [README.md](README.md)
- Architecture: [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md)
- Implementation: [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)

### For Researchers
- Formula: [EQUATION.md](EQUATION.md)
- Results: [README.md](README.md#what-works)
- Limitations: [README.md](README.md#what-doesnt-work)

## 🔍 By Topic

### Semantic Matching
- [README.md](README.md#architecture) - How it works
- [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md) - Technical details

### Company Scoring
- [EQUATION.md](EQUATION.md) - Formula details
- [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md) - Implementation

### Geographic Filtering
- [docs/ENHANCED_SYSTEM_DOCUMENTATION.md](docs/ENHANCED_SYSTEM_DOCUMENTATION.md) - Enhanced features
- [README.md](README.md#enhanced-system-with-geographic-filtering) - Overview

### Batch Processing
- [docs/RUN_BATCH_SCORING.md](docs/RUN_BATCH_SCORING.md) - Complete guide
- [FINAL_COMMAND.md](FINAL_COMMAND.md) - Quick start

### API Integration
- [README.md](README.md#cost) - Cost estimates
- [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md#api-integrations) - Technical details

## 📝 Quick Links

### Setup
```bash
# See: GETTING_STARTED.md
python scripts/setup_postgres.py
python scripts/setup_companies.py
python scripts/fill_llm_fields.py
python scripts/embed_companies_qdrant.py --full
python scripts/setup_enhanced_system.py
```

### Test
```bash
# See: FINAL_COMMAND.md
python tests/test_scoring.py
```

### Process
```bash
# See: docs/RUN_BATCH_SCORING.md
python scripts/batch_process_with_scoring.py --limit 5
```

### Monitor
```bash
# See: docs/QUICK_REFERENCE.md
python scripts/check_batch_progress.py
python tests/verify_scoring.py
```

## 🆘 Need Help?

1. **Getting Started**: [GETTING_STARTED.md](GETTING_STARTED.md)
2. **Quick Commands**: [FINAL_COMMAND.md](FINAL_COMMAND.md)
3. **Common Issues**: [GETTING_STARTED.md](GETTING_STARTED.md#common-issues)
4. **File Locations**: [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
5. **Command Reference**: [docs/QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

## 📈 Version History

See [docs/CHANGELOG.md](docs/CHANGELOG.md) for version history.

**Current Version**: 2.1.0 (Company Scoring System)

---

**Start here**: [GETTING_STARTED.md](GETTING_STARTED.md)
