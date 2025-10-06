# Implementation Plan

**IMPORTANT**: Always activate the conda environment before running any Python code:
```bash
conda activate turing0.1
```

- [x] 1. Build reverse index script for company→incentives mapping





  - Create `scripts/build_company_incentive_index.py` that iterates through all incentives
  - Extract companies from `top_5_companies_scored` JSON for each incentive
  - Aggregate all incentives per company and keep top 5 by score
  - Add `eligible_incentives` JSONB column to companies table
  - Save reverse index to database with proper error handling
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_



- [ ] 2. Set up backend project structure
  - Create `backend/` directory with FastAPI project structure
  - Create `backend/app/main.py` with FastAPI app initialization and startup event
  - Add singleton model loading in startup event (CRITICAL for performance)
  - Create `backend/app/config.py` for environment variable configuration
  - Create `backend/requirements.txt` with dependencies (fastapi, uvicorn, psycopg2, sentence-transformers, qdrant-client, openai, python-dotenv)

  - Create `backend/Dockerfile` for containerization
  - _Requirements: 8.1, 8.3, 6.1_

- [x] 3. Implement database service


  - Create `backend/app/services/database.py` with DatabaseService class
  - Implement `get_incentive_with_companies()` method to fetch incentive and parse `top_5_companies_scored`
  - Implement `get_company_with_incentives()` method to fetch company with `eligible_incentives`
  - Add connection pooling and error handling
  - Write unit tests for database service
  - _Requirements: 5.7, 7.7_

- [x] 4. Implement query classifier service


  - Create `backend/app/services/classifier.py` with QueryClassifier class
  - Implement GPT-5-mini classification using exact pattern from existing codebase
  - Add JSON response parsing with error handling
  - Implement fallback keyword-based classification
  - Add debug logging for classification results
  - Write unit tests with mocked OpenAI responses
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 9.3_




- [ ] 5. Implement semantic search service
  - Create `backend/app/services/search.py` with SemanticSearchService class
  - Implement `search_companies()` using existing Qdrant vector DB (250k records)
  - Implement `search_incentives()` using PostgreSQL keyword search (small dataset ~300 records)
  - Load `paraphrase-multilingual-MiniLM-L12-v2` model as singleton for company search


  - Add confidence scoring and result ranking
  - Write unit tests for search functionality
  - _Requirements: 2.1, 3.1, 6.1, 6.2, 6.3_

- [ ] 6. Implement main query API endpoint
  - Create `backend/app/api/routes.py` with `/api/query` POST endpoint
  - Integrate QueryClassifier, SemanticSearchService, and DatabaseService
  - Route queries based on classification (INCENTIVE vs COMPANY)


  - Format responses with proper data models (Pydantic)
  - Add request timing and logging
  - Write integration tests for the endpoint
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.7, 5.8, 5.9_




- [ ] 6.5. Implement detail page API endpoints
  - Add `GET /api/incentive/:id` endpoint to fetch single incentive with companies
  - Add `GET /api/company/:id` endpoint to fetch single company with incentives
  - Reuse DatabaseService methods (get_incentive_with_companies, get_company_with_incentives)
  - Add proper error handling for not found (404) and server errors (500)


  - Write integration tests for both endpoints
  - _Requirements: 5.5, 5.6_

- [ ] 7. Add error handling and health checks
  - Implement global exception handler in FastAPI
  - Add `/health` endpoint for monitoring
  - Add proper HTTP status codes for different error types
  - Implement request timeout handling
  - Add CORS middleware configuration
  - _Requirements: 8.4, 9.1, 9.2, 9.4_

- [ ] 8. Set up frontend project structure
  - Create `frontend/` directory with Vite + React + TypeScript
  - Run `npm create vite@latest frontend -- --template react-ts`
  - Install dependencies: TailwindCSS, axios, react-router-dom, react-markdown
  - Configure TailwindCSS with custom theme
  - Set up React Router for navigation between incentive/company detail views
  - Create basic folder structure (components/, services/, types/, utils/, pages/)
  - _Requirements: 4.1, 8.2_

- [ ] 9. Implement TypeScript interfaces and types

  - Create `frontend/src/types/api.ts` with all API response types
  - Define IncentiveResult, CompanyResult, CompanyMatch, IncentiveMatch interfaces
  - Define QueryRequest, QueryResponse types
  - Add proper null handling for optional fields
  - _Requirements: 2.2, 2.3, 2.4, 3.2, 3.3, 3.4_

- [ ] 10. Implement API service layer

  - Create `frontend/src/services/api.ts` with API client
  - Implement `queryIncentivesOrCompanies()` function using axios
  - Add request timeout configuration (30 seconds)
  - Add error handling and retry logic
  - Implement request debouncing utility
  - _Requirements: 5.1, 6.5, 9.1, 9.2_

- [ ] 11. Build QueryInput component

  - Create `frontend/src/components/QueryInput.tsx`
  - Implement textarea with auto-resize functionality
  - Add submit button with loading state
  - Handle Enter key submission (Shift+Enter for new line)
  - Add input validation (min 1 char, max 500 chars)
  - Style with TailwindCSS
  - _Requirements: 4.2, 4.3_

- [ ] 12. Build IncentiveCard component

  - Create `frontend/src/components/IncentiveCard.tsx`
  - Display incentive metadata (title, description, sector, geo, actions)
  - Render top 5 companies with rank badges as clickable cards
  - Add onClick handler to navigate to company detail view
  - Add progress bars for company scores
  - Add links to company websites
  - Style with TailwindCSS cards and shadows with hover effects
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 4.6_

- [ ] 13. Build CompanyCard component

  - Create `frontend/src/components/CompanyCard.tsx`
  - Display company metadata (name, CAE, activities, location)
  - Render eligible incentives sorted by score as clickable cards
  - Add onClick handler to navigate to incentive detail view
  - Add rank indicators and score badges
  - Add expandable sections for long descriptions
  - Style with TailwindCSS with hover effects
  - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 4.6_

- [ ] 14. Build ResultsDisplay component

  - Create `frontend/src/components/ResultsDisplay.tsx`
  - Route to IncentiveCard or CompanyCard based on query type
  - Handle loading states with skeleton loaders
  - Display "No results found" message with suggestions
  - Add error message display
  - _Requirements: 2.5, 3.6, 9.5_

- [ ] 15. Build ChatInterface component

  - Create `frontend/src/components/ChatInterface.tsx`
  - Implement chat message history state management
  - Render user messages and assistant responses
  - Add auto-scroll to latest message
  - Implement "New Chat" button to clear history
  - Style with ChatGPT-like layout
  - _Requirements: 4.1, 4.3, 4.4, 4.5, 4.7, 4.8_

- [ ] 16. Build main App component and routing

  - Create `frontend/src/App.tsx` with React Router setup
  - Create routes: `/` (chat), `/incentive/:id`, `/company/:id`
  - Create `frontend/src/pages/IncentiveDetailPage.tsx` for incentive detail view
  - Create `frontend/src/pages/CompanyDetailPage.tsx` for company detail view
  - Integrate ChatInterface and QueryInput components on home route
  - Add header with logo, "New Chat" button, and back navigation
  - Implement responsive layout (desktop/tablet/mobile)
  - Add dark mode support (optional)
  - _Requirements: 4.1, 4.6, 4.8, 2.5, 3.5_

- [ ] 17. Optimize frontend performance

  - Implement code splitting with React.lazy()
  - Add memoization to expensive components with React.memo()
  - Implement virtual scrolling for long lists (if needed)
  - Configure Vite for optimal bundle size
  - Add service worker for offline support (optional)
  - _Requirements: 6.3, 6.4_

- [ ] 18. Write frontend tests

  - Set up Jest and React Testing Library
  - Write unit tests for QueryInput component
  - Write unit tests for IncentiveCard and CompanyCard
  - Write integration tests for ChatInterface
  - Add Playwright tests for full user flow
  - _Requirements: All frontend requirements_

- [ ] 19. Write backend tests

  - Set up pytest with test fixtures
  - Write unit tests for QueryClassifier with mocked OpenAI
  - Write unit tests for SemanticSearchService with mocked Qdrant
  - Write unit tests for DatabaseService with test database
  - Write integration tests for `/api/query` endpoint
  - _Requirements: All backend requirements_

- [ ] 20. Create deployment configuration
  - Create `docker-compose.yml` for local development
  - Create production Dockerfile for backend
  - Create Vercel/Netlify config for frontend static build
  - Add environment variable documentation in README
  - Create health check monitoring script
  - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 21. Write documentation
  - Create `README.md` with setup instructions
  - Document API endpoints with example requests/responses
  - Add architecture diagram
  - Document environment variables
  - Add troubleshooting guide
  - _Requirements: 8.5_

- [ ] 22. End-to-end testing and polish
  - Test full flow: query → classification → search → display
  - Test navigation: click company → see incentives, click incentive → see companies
  - Test error scenarios (API down, timeout, no results)
  - Test responsive design on different screen sizes
  - Optimize loading times and add performance monitoring
  - Fix any UI/UX issues
  - _Requirements: All requirements_

- [ ] 23. Future: Create incentive embeddings for multi-result queries
  - Create script `scripts/create_incentive_embeddings.py`
  - Generate embeddings for all incentives using `paraphrase-multilingual-MiniLM-L12-v2`
  - Store embeddings in new Qdrant collection `incentives`
  - Update search service to use vector search for incentives
  - Implement multi-result display (top 3-5) for general queries
  - Add result filtering and ranking
  - _Requirements: Future enhancement for better search quality_
