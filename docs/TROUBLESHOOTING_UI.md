# Troubleshooting Guide - UI Layer

## Overview

This guide covers common issues you might encounter when setting up, running, or deploying the Incentive Query UI.

---

## Table of Contents

1. [Backend Issues](#backend-issues)
2. [Frontend Issues](#frontend-issues)
3. [Database Issues](#database-issues)
4. [API Issues](#api-issues)
5. [Deployment Issues](#deployment-issues)
6. [Performance Issues](#performance-issues)

---

## Backend Issues

### Issue: "ModuleNotFoundError: No module named 'app'"

**Symptoms**: Backend fails to start with import errors

**Cause**: Running from wrong directory or missing dependencies

**Solutions**:
```bash
# 1. Make sure you're in the backend directory
cd backend

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run from backend directory
uvicorn app.main:app --reload
```

---

### Issue: "OPEN_AI environment variable is required"

**Symptoms**: Backend crashes on startup

**Cause**: Missing OpenAI API key

**Solutions**:
```bash
# 1. Check if config.env exists in project root
ls ../config.env

# 2. Add OPEN_AI to config.env
echo "OPEN_AI=sk-proj-your-key" >> ../config.env

# 3. Or set environment variable directly
export OPEN_AI=sk-proj-your-key

# 4. Restart backend
uvicorn app.main:app --reload
```

---

### Issue: "Qdrant collection 'companies' not found"

**Symptoms**: Company search fails with collection error

**Cause**: Qdrant embeddings not created

**Solutions**:
```bash
# 1. Check if qdrant_storage exists
ls ../qdrant_storage

# 2. Create embeddings (from project root)
cd ..
conda activate turing0.1
python scripts/embed_companies_qdrant.py --full

# 3. Wait for completion (~30-60 minutes)
# 4. Restart backend
cd backend
uvicorn app.main:app --reload
```

---

### Issue: "Model loading takes forever"

**Symptoms**: Backend startup takes 30+ seconds

**Cause**: Models loading on CPU instead of GPU

**Solutions**:
```bash
# 1. Check if CUDA is available
python -c "import torch; print(torch.cuda.is_available())"

# 2. If False, install CUDA-enabled PyTorch
pip install torch --index-url https://download.pytorch.org/whl/cu118

# 3. Verify GPU is used
python -c "from sentence_transformers import SentenceTransformer; m = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2'); print(m.device)"
```

**Note**: CPU is fine for development, but GPU is recommended for production

---

### Issue: "OpenAI API timeout"

**Symptoms**: Queries fail with timeout errors

**Cause**: OpenAI API slow or network issues

**Solutions**:
```bash
# 1. Increase timeout in config.env
echo "API_TIMEOUT=60" >> ../config.env

# 2. Check OpenAI API status
curl https://status.openai.com

# 3. Test API directly
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPEN_AI"

# 4. Restart backend
uvicorn app.main:app --reload
```

---

### Issue: "Database connection refused"

**Symptoms**: Backend can't connect to PostgreSQL

**Cause**: PostgreSQL not running or wrong credentials

**Solutions**:
```bash
# 1. Check if PostgreSQL is running
# Windows:
sc query postgresql-x64-14

# Linux/Mac:
sudo systemctl status postgresql

# 2. Test connection manually
psql -h localhost -U postgres -d incentives_db

# 3. Verify credentials in config.env
cat ../config.env | grep DB_

# 4. Update if needed
# Edit config.env with correct values

# 5. Restart backend
uvicorn app.main:app --reload
```

---

## Frontend Issues

### Issue: "npm: command not found"

**Symptoms**: Can't run npm commands

**Cause**: Node.js not installed

**Solutions**:
```bash
# 1. Install Node.js (v18 or higher)
# Download from: https://nodejs.org

# 2. Verify installation
node --version
npm --version

# 3. Install dependencies
cd frontend
npm install
```

---

### Issue: "VITE_API_URL is not defined"

**Symptoms**: Frontend can't connect to backend

**Cause**: Missing environment variable

**Solutions**:
```bash
# 1. Create .env.local in frontend directory
cd frontend
echo "VITE_API_URL=http://localhost:8000" > .env.local

# 2. Restart dev server
npm run dev
```

---

### Issue: "CORS error when calling API"

**Symptoms**: Browser console shows CORS errors

**Cause**: Backend not allowing frontend origin

**Solutions**:
```bash
# 1. Check backend CORS configuration
cat ../config.env | grep CORS

# 2. Add frontend URL to CORS_ORIGINS
echo "CORS_ORIGINS=http://localhost:5173" >> ../config.env

# 3. Restart backend
cd ../backend
uvicorn app.main:app --reload

# 4. Clear browser cache and reload frontend
```

---

### Issue: "Module not found: Can't resolve 'axios'"

**Symptoms**: Frontend build fails with missing module

**Cause**: Dependencies not installed

**Solutions**:
```bash
# 1. Install dependencies
cd frontend
npm install

# 2. If still failing, clear cache
rm -rf node_modules package-lock.json
npm install

# 3. Restart dev server
npm run dev
```

---

### Issue: "Blank page after build"

**Symptoms**: Production build shows blank page

**Cause**: Incorrect base path or API URL

**Solutions**:
```bash
# 1. Check browser console for errors
# Open DevTools (F12) → Console

# 2. Verify VITE_API_URL is set for production
echo "VITE_API_URL=https://your-backend.com" > .env.production

# 3. Rebuild
npm run build

# 4. Test locally
npm run preview
```

---

## Database Issues

### Issue: "Table 'incentives' does not exist"

**Symptoms**: Backend queries fail with table not found

**Cause**: Database not initialized

**Solutions**:
```bash
# 1. Run setup scripts (from project root)
conda activate turing0.1
python scripts/setup_postgres.py
python scripts/setup_companies.py

# 2. Verify tables exist
psql -h localhost -U postgres -d incentives_db -c "\dt"

# 3. Restart backend
cd backend
uvicorn app.main:app --reload
```

---

### Issue: "Column 'eligible_incentives' does not exist"

**Symptoms**: Company queries fail with column error

**Cause**: Reverse index not built

**Solutions**:
```bash
# 1. Build reverse index (from project root)
conda activate turing0.1
python scripts/build_company_incentive_index.py

# 2. Wait for completion (~5-10 minutes)

# 3. Verify column exists
psql -h localhost -U postgres -d incentives_db \
  -c "SELECT column_name FROM information_schema.columns WHERE table_name='companies' AND column_name='eligible_incentives';"

# 4. Restart backend
cd backend
uvicorn app.main:app --reload
```

---

### Issue: "No results found for any query"

**Symptoms**: All queries return 404

**Cause**: Database empty or data not processed

**Solutions**:
```bash
# 1. Check if incentives exist
psql -h localhost -U postgres -d incentives_db \
  -c "SELECT COUNT(*) FROM incentives;"

# 2. If 0, run batch processing
conda activate turing0.1
python scripts/batch_process_with_scoring.py --limit 5

# 3. Check if companies exist
psql -h localhost -U postgres -d incentives_db \
  -c "SELECT COUNT(*) FROM companies;"

# 4. If 0, run setup
python scripts/setup_companies.py

# 5. Restart backend
cd backend
uvicorn app.main:app --reload
```

---

## API Issues

### Issue: "Query classification always returns INCENTIVE"

**Symptoms**: Company queries treated as incentive queries

**Cause**: OpenAI API error or fallback classification

**Solutions**:
```bash
# 1. Check backend logs for classification errors
# Look for "[CLASSIFIER] Error:" messages

# 2. Test OpenAI API
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $OPEN_AI" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-4-mini","messages":[{"role":"user","content":"test"}]}'

# 3. Check API key has credits
# Visit: https://platform.openai.com/usage

# 4. If API is down, classification falls back to keywords
# This is expected behavior
```

---

### Issue: "Queries timeout after 30 seconds"

**Symptoms**: Long queries fail with timeout

**Cause**: Default timeout too short

**Solutions**:
```bash
# 1. Increase backend timeout
echo "API_TIMEOUT=60" >> ../config.env

# 2. Increase frontend timeout
# Edit frontend/src/services/api.ts
# Change: timeout: 30000 → timeout: 60000

# 3. Restart both backend and frontend
```

---

### Issue: "Search returns wrong results"

**Symptoms**: Results don't match query intent

**Cause**: Query classification or search algorithm issue

**Solutions**:
```bash
# 1. Check classification in backend logs
# Look for "[CLASSIFIER] Classified as: ..." messages

# 2. Try more specific queries
# Instead of: "tech"
# Try: "incentivos para empresas de tecnologia"

# 3. Check if data is processed correctly
psql -h localhost -U postgres -d incentives_db \
  -c "SELECT incentive_id, title, sector FROM incentives LIMIT 5;"

# 4. Verify embeddings exist
python -c "from qdrant_client import QdrantClient; c = QdrantClient(path='./qdrant_storage'); print(c.get_collection('companies'))"
```

---

## Deployment Issues

### Issue: "Docker build fails"

**Symptoms**: Docker build errors

**Cause**: Missing files or incorrect Dockerfile

**Solutions**:
```bash
# 1. Check Dockerfile exists
ls backend/Dockerfile

# 2. Build with verbose output
docker build -t incentive-backend ./backend --progress=plain

# 3. Check for missing files in .dockerignore
cat backend/.dockerignore

# 4. Try building without cache
docker build --no-cache -t incentive-backend ./backend
```

---

### Issue: "Container exits immediately"

**Symptoms**: Docker container starts then stops

**Cause**: Missing environment variables or startup error

**Solutions**:
```bash
# 1. Check container logs
docker logs <container-id>

# 2. Run with environment variables
docker run -p 8000:8000 \
  -e DB_HOST=host.docker.internal \
  -e DB_NAME=incentives_db \
  -e DB_USER=postgres \
  -e DB_PASSWORD=password \
  -e OPEN_AI=sk-proj-... \
  -e QDRANT_PATH=/app/qdrant_storage \
  incentive-backend

# 3. Or use env file
docker run -p 8000:8000 --env-file .env incentive-backend
```

---

### Issue: "Frontend can't reach backend in production"

**Symptoms**: API calls fail in production

**Cause**: Wrong API URL or CORS configuration

**Solutions**:
```bash
# 1. Check frontend API URL
# In deployment platform, verify VITE_API_URL is set correctly

# 2. Check backend CORS
# In deployment platform, verify CORS_ORIGINS includes frontend URL

# 3. Test API directly
curl https://your-backend.com/health

# 4. Check browser console for specific error
# Open DevTools (F12) → Network tab
```

---

### Issue: "Vercel deployment fails"

**Symptoms**: Frontend build fails on Vercel

**Cause**: Build errors or missing environment variables

**Solutions**:
```bash
# 1. Check build logs in Vercel dashboard

# 2. Test build locally
cd frontend
npm run build

# 3. Add environment variables in Vercel
# Settings → Environment Variables
# Add: VITE_API_URL = https://your-backend.com

# 4. Redeploy
```

---

## Performance Issues

### Issue: "Queries take 5+ seconds"

**Symptoms**: Slow API responses

**Cause**: Models loading per request or slow database

**Solutions**:
```bash
# 1. Check if models are loaded as singletons
# Look for "[STARTUP] Models loaded successfully" in logs

# 2. If not, verify startup event in backend/app/main.py
# Should have @app.on_event("startup")

# 3. Check database query performance
psql -h localhost -U postgres -d incentives_db \
  -c "EXPLAIN ANALYZE SELECT * FROM incentives WHERE title ILIKE '%tech%';"

# 4. Add indexes if needed
psql -h localhost -U postgres -d incentives_db \
  -c "CREATE INDEX IF NOT EXISTS idx_incentives_title ON incentives(title);"

# 5. Restart backend
uvicorn app.main:app --reload
```

---

### Issue: "High memory usage"

**Symptoms**: Backend uses 4+ GB RAM

**Cause**: Large models loaded in memory

**Solutions**:
```bash
# 1. This is expected behavior
# Embedding model: ~500MB
# Reranker model: ~1GB
# Qdrant: ~400MB for 250K vectors

# 2. If memory is limited, use smaller models
# Edit backend/app/services/search.py
# Change model to: 'paraphrase-MiniLM-L6-v2' (smaller)

# 3. Or increase server memory
# Recommended: 4GB minimum, 8GB ideal
```

---

### Issue: "Frontend bundle too large"

**Symptoms**: Slow initial page load

**Cause**: Large bundle size

**Solutions**:
```bash
# 1. Analyze bundle
cd frontend
npm run build
npx vite-bundle-visualizer

# 2. Implement code splitting (already done in App.tsx)
# Verify lazy loading is used

# 3. Remove unused dependencies
npm prune

# 4. Optimize images
# Use WebP format, compress images

# 5. Enable compression in production
# Nginx/Apache should gzip assets
```

---

## Common Error Messages

### "Failed to fetch"

**Meaning**: Frontend can't reach backend

**Check**:
1. Backend is running (`curl http://localhost:8000/health`)
2. CORS is configured correctly
3. Firewall allows connection
4. API URL is correct in frontend

---

### "404 Not Found"

**Meaning**: Resource doesn't exist

**Check**:
1. Database has data
2. Query is specific enough
3. ID is correct (for detail endpoints)
4. Endpoint path is correct

---

### "500 Internal Server Error"

**Meaning**: Backend error

**Check**:
1. Backend logs for stack trace
2. Database connection
3. API keys are valid
4. Models loaded successfully

---

### "503 Service Unavailable"

**Meaning**: Service temporarily down

**Check**:
1. Backend is running
2. Database is accessible
3. Qdrant is accessible
4. System resources (CPU, memory)

---

## Debugging Tips

### Enable Debug Logging

**Backend**:
```bash
# In config.env
LOG_LEVEL=DEBUG

# Restart backend
uvicorn app.main:app --reload --log-level debug
```

**Frontend**:
```typescript
// In frontend/src/services/api.ts
// Add console.log statements
console.log('API Request:', url, data);
console.log('API Response:', response);
```

---

### Check Backend Health

```bash
# Health check
curl http://localhost:8000/health

# Test query endpoint
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query":"test"}'

# Test detail endpoints
curl http://localhost:8000/api/incentive/2270
curl http://localhost:8000/api/company/12345
```

---

### Check Database

```bash
# Connect to database
psql -h localhost -U postgres -d incentives_db

# Check tables
\dt

# Check data
SELECT COUNT(*) FROM incentives;
SELECT COUNT(*) FROM companies;

# Check specific incentive
SELECT * FROM incentives WHERE incentive_id = '2270';

# Check company with incentives
SELECT company_id, company_name, eligible_incentives 
FROM companies 
WHERE company_id = 12345;
```

---

### Check Qdrant

```python
# In Python
from qdrant_client import QdrantClient

client = QdrantClient(path="./qdrant_storage")

# Check collection
collection = client.get_collection("companies")
print(f"Vectors: {collection.vectors_count}")
print(f"Points: {collection.points_count}")

# Test search
results = client.query_points(
    collection_name="companies",
    query=[0.1] * 384,  # Random vector
    limit=5
)
print(results)
```

---

### Monitor Performance

**Backend**:
```bash
# Install monitoring tools
pip install py-spy

# Profile backend
py-spy top --pid <backend-pid>

# Record flame graph
py-spy record -o profile.svg --pid <backend-pid>
```

**Frontend**:
```javascript
// In browser DevTools
// Performance tab → Record → Perform actions → Stop

// Network tab → Check request times
// Console tab → Check for errors
```

---

## Getting Help

### Check Documentation
1. API Documentation: `docs/API_DOCUMENTATION.md`
2. Architecture: `docs/UI_ARCHITECTURE.md`
3. Environment Variables: `docs/ENVIRONMENT_VARIABLES.md`
4. Main README: `README.md`

### Check Logs
1. Backend logs: Terminal where uvicorn is running
2. Frontend logs: Browser DevTools → Console
3. Database logs: PostgreSQL logs
4. System logs: Check system event logs

### Test Components Individually
1. Test database connection
2. Test API endpoints with curl
3. Test frontend with mock data
4. Test models in Python REPL

### Common Solutions
1. Restart everything (backend, frontend, database)
2. Clear caches (browser, npm, pip)
3. Reinstall dependencies
4. Check environment variables
5. Verify data is processed

---

## Quick Fixes Checklist

- [ ] Backend is running (`curl http://localhost:8000/health`)
- [ ] Frontend is running (`curl http://localhost:5173`)
- [ ] PostgreSQL is running
- [ ] Database has data (incentives and companies)
- [ ] Qdrant embeddings exist (`./qdrant_storage`)
- [ ] Environment variables are set (`.env` or `config.env`)
- [ ] CORS is configured correctly
- [ ] API keys are valid (OpenAI)
- [ ] Dependencies are installed (`pip install -r requirements.txt`, `npm install`)
- [ ] Models loaded successfully (check startup logs)

---

## Still Having Issues?

1. **Check existing issues**: Review this guide thoroughly
2. **Enable debug logging**: Set `LOG_LEVEL=DEBUG`
3. **Test components**: Isolate the problem (backend vs frontend vs database)
4. **Check logs**: Look for specific error messages
5. **Verify setup**: Ensure all setup scripts ran successfully
6. **Test with curl**: Bypass frontend to test backend directly
7. **Check resources**: Ensure sufficient CPU, memory, disk space

---

For more information, see:
- API Documentation: `docs/API_DOCUMENTATION.md`
- Architecture: `docs/UI_ARCHITECTURE.md`
- Environment Variables: `docs/ENVIRONMENT_VARIABLES.md`
