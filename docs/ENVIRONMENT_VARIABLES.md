# Environment Variables

## Overview

This document describes all environment variables used by the Incentive Query UI system (both backend and frontend).

---

## Backend Environment Variables

### Database Configuration

#### `DB_NAME`
- **Description**: PostgreSQL database name
- **Required**: Yes
- **Default**: `incentives_db`
- **Example**: `incentives_db`

#### `DB_USER`
- **Description**: PostgreSQL username
- **Required**: Yes
- **Default**: `postgres`
- **Example**: `postgres`

#### `DB_PASSWORD`
- **Description**: PostgreSQL password
- **Required**: Yes
- **Default**: None
- **Example**: `your_secure_password`
- **Security**: Never commit this to version control

#### `DB_HOST`
- **Description**: PostgreSQL host address
- **Required**: Yes
- **Default**: `localhost`
- **Example**: `localhost` (dev), `db.example.com` (prod)

#### `DB_PORT`
- **Description**: PostgreSQL port
- **Required**: Yes
- **Default**: `5432`
- **Example**: `5432`

---

### API Keys

#### `OPEN_AI`
- **Description**: OpenAI API key for GPT-4-mini
- **Required**: Yes
- **Default**: None
- **Example**: `sk-proj-...`
- **Usage**: Query classification
- **Security**: Never commit this to version control
- **Cost**: ~$0.01-0.02 per query

#### `GOOGLE_MAPS_API_KEY`
- **Description**: Google Maps API key (used by existing system, not UI)
- **Required**: No (for UI), Yes (for batch processing)
- **Default**: None
- **Example**: `AIza...`
- **Usage**: Location enrichment (existing system only)
- **Security**: Never commit this to version control

---

### Qdrant Configuration

#### `QDRANT_PATH`
- **Description**: Path to Qdrant storage directory
- **Required**: Yes
- **Default**: `./qdrant_storage`
- **Example**: `./qdrant_storage` (relative), `/data/qdrant` (absolute)
- **Note**: Must contain pre-computed company embeddings

---

### Server Configuration

#### `CORS_ORIGINS`
- **Description**: Allowed CORS origins (comma-separated)
- **Required**: No
- **Default**: `http://localhost:5173` (dev)
- **Example**: `https://your-frontend.com,https://www.your-frontend.com`
- **Production**: Set to your frontend domain(s)

#### `LOG_LEVEL`
- **Description**: Logging level
- **Required**: No
- **Default**: `INFO`
- **Options**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **Example**: `INFO` (prod), `DEBUG` (dev)

#### `API_TIMEOUT`
- **Description**: API request timeout in seconds
- **Required**: No
- **Default**: `30`
- **Example**: `30`
- **Note**: Applies to OpenAI API calls

---

## Frontend Environment Variables

### API Configuration

#### `VITE_API_URL`
- **Description**: Backend API base URL
- **Required**: Yes
- **Default**: `http://localhost:8000`
- **Example**: 
  - Development: `http://localhost:8000`
  - Production: `https://api.your-domain.com`
- **Note**: Must start with `VITE_` to be exposed to frontend

---

## Configuration Files

### Backend: `.env` or `config.env`

Create a file named `.env` or `config.env` in the project root:

```bash
# Database
DB_NAME=incentives_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# API Keys
OPEN_AI=sk-proj-your-openai-key
GOOGLE_MAPS_API_KEY=your-google-maps-key

# Qdrant
QDRANT_PATH=./qdrant_storage

# Server (optional)
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=INFO
API_TIMEOUT=30
```

**Security**: Add `.env` to `.gitignore`!

---

### Frontend: `.env` or `.env.local`

Create a file named `.env` or `.env.local` in the `frontend/` directory:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000
```

**Development**: Use `.env.local` (not committed)
**Production**: Set via deployment platform (Vercel, Netlify, etc.)

---

## Loading Environment Variables

### Backend (Python)

The backend uses `python-dotenv` to load environment variables:

```python
from dotenv import load_dotenv
import os

# Load from config.env or .env
load_dotenv('config.env')
load_dotenv('.env')

# Access variables
db_name = os.getenv('DB_NAME', 'incentives_db')
openai_key = os.getenv('OPEN_AI')
```

**File Priority**:
1. System environment variables (highest priority)
2. `.env` file
3. `config.env` file
4. Default values (lowest priority)

---

### Frontend (Vite)

Vite automatically loads environment variables from `.env` files:

```typescript
// Access in code (must start with VITE_)
const apiUrl = import.meta.env.VITE_API_URL;
```

**File Priority** (Vite):
1. `.env.local` (highest priority, not committed)
2. `.env.production` (production builds)
3. `.env.development` (development builds)
4. `.env` (all environments)

**Important**: Only variables starting with `VITE_` are exposed to the frontend!

---

## Environment-Specific Configuration

### Development

**Backend** (`config.env`):
```bash
DB_HOST=localhost
DB_PORT=5432
CORS_ORIGINS=http://localhost:5173
LOG_LEVEL=DEBUG
```

**Frontend** (`.env.local`):
```bash
VITE_API_URL=http://localhost:8000
```

---

### Production

**Backend** (set via deployment platform):
```bash
DB_HOST=your-db-host.com
DB_PORT=5432
DB_PASSWORD=strong_production_password
OPEN_AI=sk-proj-production-key
CORS_ORIGINS=https://your-frontend.com
LOG_LEVEL=INFO
API_TIMEOUT=30
```

**Frontend** (set via deployment platform):
```bash
VITE_API_URL=https://api.your-domain.com
```

---

## Docker Configuration

### Using Environment Files

**docker-compose.yml**:
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    env_file:
      - .env
    ports:
      - "8000:8000"
  
  frontend:
    build: ./frontend
    environment:
      - VITE_API_URL=http://backend:8000
    ports:
      - "80:80"
```

---

### Using Environment Variables

**docker run**:
```bash
docker run -p 8000:8000 \
  -e DB_NAME=incentives_db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=password \
  -e DB_HOST=localhost \
  -e DB_PORT=5432 \
  -e OPEN_AI=sk-proj-... \
  -e QDRANT_PATH=/app/qdrant_storage \
  incentive-backend
```

---

## Deployment Platform Configuration

### Vercel (Frontend)

1. Go to Project Settings → Environment Variables
2. Add:
   - `VITE_API_URL` = `https://your-backend.com`
3. Redeploy

---

### Railway (Backend)

1. Go to Variables tab
2. Add all backend environment variables
3. Railway automatically restarts on changes

---

### Render (Backend)

1. Go to Environment tab
2. Add all backend environment variables
3. Click "Save Changes"

---

### Fly.io (Backend)

Use `fly secrets`:
```bash
fly secrets set DB_PASSWORD=your_password
fly secrets set OPEN_AI=sk-proj-...
fly secrets set CORS_ORIGINS=https://your-frontend.com
```

---

## Security Best Practices

### 1. Never Commit Secrets
Add to `.gitignore`:
```
.env
.env.local
config.env
*.env
```

### 2. Use Different Keys for Dev/Prod
- Development: Use test API keys with low limits
- Production: Use production API keys with monitoring

### 3. Rotate Keys Regularly
- Change API keys every 3-6 months
- Immediately rotate if compromised

### 4. Restrict CORS Origins
```bash
# Bad (allows all origins)
CORS_ORIGINS=*

# Good (specific origins)
CORS_ORIGINS=https://your-frontend.com,https://www.your-frontend.com
```

### 5. Use Strong Database Passwords
- Minimum 16 characters
- Mix of letters, numbers, symbols
- Use password manager

### 6. Limit Database Access
- Create read-only user for UI backend
- Use separate credentials for batch processing

---

## Validation

### Backend Validation

The backend validates required environment variables at startup:

```python
# backend/app/config.py
import os

class Settings:
    def __init__(self):
        # Required variables
        self.db_name = os.getenv('DB_NAME')
        self.db_user = os.getenv('DB_USER')
        self.db_password = os.getenv('DB_PASSWORD')
        self.openai_key = os.getenv('OPEN_AI')
        
        # Validate
        if not self.openai_key:
            raise ValueError("OPEN_AI environment variable is required")
        if not self.db_password:
            raise ValueError("DB_PASSWORD environment variable is required")
```

**Test validation**:
```bash
cd backend
python -c "from app.config import Settings; Settings()"
```

---

### Frontend Validation

Check environment variables at build time:

```typescript
// frontend/src/config.ts
const apiUrl = import.meta.env.VITE_API_URL;

if (!apiUrl) {
  throw new Error('VITE_API_URL environment variable is required');
}

export const config = {
  apiUrl
};
```

---

## Troubleshooting

### "Environment variable not found"

**Problem**: Variable not loaded

**Solutions**:
1. Check file name (`.env` or `config.env`)
2. Check file location (project root for backend, `frontend/` for frontend)
3. Restart server after changing `.env`
4. For frontend, variable must start with `VITE_`

---

### "CORS error"

**Problem**: Frontend can't access backend

**Solutions**:
1. Check `CORS_ORIGINS` includes frontend URL
2. Restart backend after changing CORS settings
3. Check frontend is using correct `VITE_API_URL`

---

### "Database connection failed"

**Problem**: Can't connect to PostgreSQL

**Solutions**:
1. Verify `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`
2. Check PostgreSQL is running
3. Check firewall allows connection
4. Test connection: `psql -h $DB_HOST -U $DB_USER -d $DB_NAME`

---

### "OpenAI API error"

**Problem**: Can't access OpenAI API

**Solutions**:
1. Verify `OPEN_AI` key is correct
2. Check API key has credits
3. Check API key permissions
4. Test: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPEN_AI"`

---

## Example Configurations

### Minimal Development Setup

**Backend** (`config.env`):
```bash
DB_NAME=incentives_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
OPEN_AI=sk-proj-your-dev-key
QDRANT_PATH=./qdrant_storage
```

**Frontend** (`.env.local`):
```bash
VITE_API_URL=http://localhost:8000
```

---

### Production Setup

**Backend** (deployment platform):
```bash
DB_NAME=incentives_prod
DB_USER=incentives_user
DB_PASSWORD=strong_random_password_here
DB_HOST=db.production.com
DB_PORT=5432
OPEN_AI=sk-proj-your-prod-key
QDRANT_PATH=/data/qdrant_storage
CORS_ORIGINS=https://incentives.your-domain.com
LOG_LEVEL=INFO
API_TIMEOUT=30
```

**Frontend** (deployment platform):
```bash
VITE_API_URL=https://api.your-domain.com
```

---

## Summary

| Variable | Backend | Frontend | Required | Default |
|----------|---------|----------|----------|---------|
| `DB_NAME` | ✅ | ❌ | Yes | `incentives_db` |
| `DB_USER` | ✅ | ❌ | Yes | `postgres` |
| `DB_PASSWORD` | ✅ | ❌ | Yes | None |
| `DB_HOST` | ✅ | ❌ | Yes | `localhost` |
| `DB_PORT` | ✅ | ❌ | Yes | `5432` |
| `OPEN_AI` | ✅ | ❌ | Yes | None |
| `GOOGLE_MAPS_API_KEY` | ✅ | ❌ | No* | None |
| `QDRANT_PATH` | ✅ | ❌ | Yes | `./qdrant_storage` |
| `CORS_ORIGINS` | ✅ | ❌ | No | `http://localhost:5173` |
| `LOG_LEVEL` | ✅ | ❌ | No | `INFO` |
| `API_TIMEOUT` | ✅ | ❌ | No | `30` |
| `VITE_API_URL` | ❌ | ✅ | Yes | `http://localhost:8000` |

*Required for batch processing, not for UI

---

For more information, see:
- API Documentation: `docs/API_DOCUMENTATION.md`
- Architecture: `docs/UI_ARCHITECTURE.md`
- Troubleshooting: `docs/TROUBLESHOOTING_UI.md`
