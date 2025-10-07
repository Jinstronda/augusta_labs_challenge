# Implementation Plan

## Current Status

**BACKEND: ✅ COMPLETE** - All backend services, API endpoints, error handling, and tests are implemented.

**FRONTEND: 🚧 IN PROGRESS** - Project structure is set up, but all components need to be built.

**REMAINING WORK**: Frontend components (tasks 9-18), deployment config (task 20), documentation (task 21), and E2E testing (task 22).

---

**🚨 CRITICAL CONTEXT 🚨**: This is NOT a standalone project. We are building a query UI ON TOP of an existing incentive-company matching system.

**BEFORE EVERY SINGLE TASK**:
1. **READ THE WHOLE PROJECT FIRST** - Read all .md files (README.md, GETTING_STARTED.md, PROJECT_STRUCTURE.md, EQUATION.md, UI.md)
2. **READ THE RELEVANT CODE** - Read the existing Python files, backend code, and database schemas
3. **UNDERSTAND WHAT EXISTS** - 250K companies in PostgreSQL + Qdrant, 362 processed incentives, reverse index, scoring system
4. **DO NOT MODIFY EXISTING FUNCTIONALITY** - Only add the new UI layer, don't change the core system
5. **INTEGRATE CLEANLY** - Your code should work with what's already there, not replace it

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



- [x] 2. Set up backend project structure
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




- [x] 5. Implement semantic search service
  - Create `backend/app/services/search.py` with SemanticSearchService class
  - Implement `search_companies()` using existing Qdrant vector DB (250k records)
  - Implement `search_incentives()` using PostgreSQL keyword search (small dataset ~300 records)
  - Load `paraphrase-multilingual-MiniLM-L12-v2` model as singleton for company search
  - Add confidence scoring and result ranking
  - Write unit tests for search functionality
  - _Requirements: 2.1, 3.1, 6.1, 6.2, 6.3_

- [x] 6. Implement main query API endpoint
  - Create `backend/app/api/routes.py` with `/api/query` POST endpoint
  - Integrate QueryClassifier, SemanticSearchService, and DatabaseService
  - Route queries based on classification (INCENTIVE vs COMPANY)
  - Format responses with proper data models (Pydantic)
  - Add request timing and logging
  - Write integration tests for the endpoint
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.7, 5.8, 5.9_




- [x] 6.5. Implement detail page API endpoints
  - Add `GET /api/incentive/:id` endpoint to fetch single incentive with companies
  - Add `GET /api/company/:id` endpoint to fetch single company with incentives
  - Reuse DatabaseService methods (get_incentive_with_companies, get_company_with_incentives)
  - Add proper error handling for not found (404) and server errors (500)
  - Write integration tests for both endpoints
  - _Requirements: 5.5, 5.6_

- [x] 7. Add error handling and health checks
  - Implement global exception handler in FastAPI
  - Add `/health` endpoint for monitoring
  - Add proper HTTP status codes for different error types
  - Implement request timeout handling
  - Add CORS middleware configuration
  - _Requirements: 8.4, 9.1, 9.2, 9.4_

- [x] 8. Set up frontend project structure
  - **CONTEXT**: Read README.md, GETTING_STARTED.md, PROJECT_STRUCTURE.md to understand the existing system
  - Create `frontend/` directory with Vite + React + TypeScript
  - Run `npm create vite@latest frontend -- --template react-ts`
  - Install TailwindCSS and configure with custom theme
  - Create basic folder structure (components/, services/, types/, utils/, pages/)
  - **DO NOT** modify existing README.md - this is an existing project
  - _Requirements: 4.1, 8.2_

- [x] 8.1. Install remaining frontend dependencies





  - Install axios for API calls: `npm install axios`
  - Install react-router-dom for navigation: `npm install react-router-dom`
  - Install react-markdown for markdown rendering: `npm install react-markdown`
  - Install type definitions: `npm install -D @types/react-router-dom`
  - _Requirements: 4.1, 4.6, 8.2_

- [x] 9. Implement TypeScript interfaces and types



  - **PREREQUISITE**: Complete task 8.1 first (install dependencies)
  - **READ THE WHOLE PROJECT FIRST** - Understand the existing system architecture
  - **READ**: backend/app/models.py - This defines the EXACT API response structure
  - **READ**: backend/app/api/routes.py - See what endpoints return
  - Create `frontend/src/types/api.ts` matching the backend Pydantic models EXACTLY
  - Define IncentiveResult, CompanyResult, CompanyMatch, IncentiveMatch interfaces
  - Define QueryRequest, QueryResponse types matching backend exactly
  - Add proper null handling for optional fields
  - **DO NOT** change any backend types or add new fields
  - _Requirements: 2.2, 2.3, 2.4, 3.2, 3.3, 3.4_




- [x] 10. Implement API service layer




- [ ] 10. Implement API service layer

  - **PREREQUISITE**: Complete tasks 8.1 and 9 first (install axios and define types)
  - **READ THE WHOLE PROJECT FIRST** - Understand how the backend API works
  - **READ**: backend/app/config.py - API configuration (ports, CORS, timeouts)
  - **READ**: backend/app/api/routes.py - All available endpoints
  - Backend API runs on http://localhost:8000 with endpoints at /api/*
  - Create `frontend/src/services/api.ts` with API client pointing to existing backend
  - Implement `queryIncentivesOrCompanies()` function using axios
  - Implement `getIncentiveDetail(id)` and `getCompanyDetail(id)` functions
  - Add request timeout configuration (30 seconds matching backend)
  - Add error handling and retry logic
  - Implement request debouncing utility in `frontend/src/utils/debounce.ts`
  - **DO NOT** modify backend endpoints or add new ones
  - _Requirements: 5.1, 5.5, 5.6, 6.5, 9.1, 9.2_
- [ ] 11. Build QueryInput component








- [ ] 11. Build QueryInput component

  - **READ THE WHOLE PROJECT FIRST** - Understand the query flow and validation rules
  - **READ**: UI.md - Understand the ChatGPT-like interface requirements
  - **READ**: backend/app/models.py - QueryRequest validation (min 1, max 500 chars)
  - Create `frontend/src/components/QueryInput.tsx`
  - Implement textarea with auto-resize functionality
  - Add submit button with loading state
  - Handle Enter key submission (Shift+Enter for new line)
  - Add input validation matching backend exactly (min 1 char, max 500 chars)
  - Style with TailwindCSS
  - **DO NOT** change backend validation rules
  - _Requirements: 4.2, 4.3_

- [x] 12. Build IncentiveCard component






  - **READ THE WHOLE PROJECT FIRST** - Understand the incentive data structure and scoring
  - **READ**: EQUATION.md - Understand the scoring formula being displayed
  - **READ**: backend/app/models.py - IncentiveResult and CompanyMatch structures
  - **READ**: enhanced_incentive_matching.py - See how companies are scored
  - Create `frontend/src/components/IncentiveCard.tsx`
  - Display incentive metadata (title, description, sector, geo, actions)
  - Render top 5 companies with rank badges as clickable cards
  - Add onClick handler to navigate to company detail view
  - Add progress bars for company scores (from existing scoring system)
  - Add links to company websites
  - Style with TailwindCSS cards and shadows with hover effects
  - **DO NOT** change scoring logic or data structures
  - _Requirements: 2.2, 2.3, 2.4, 2.5, 4.6_




- [ ] 13. Build CompanyCard component

  - **READ THE WHOLE PROJECT FIRST** - Understand the company data and reverse index
  - **READ**: scripts/build_company_incentive_index.py - How eligible_incentives is built
  - **READ**: backend/app/models.py - CompanyResult and IncentiveMatch structures
  - **READ**: scripts/setup_companies.py - Company data schema
  - Create `frontend/src/components/CompanyCard.tsx`
  - Display company metadata (name, CAE, activities, location)
  - Render eligible incentives sorted by score as clickable cards (from reverse index)
  - Add onClick handler to navigate to incentive detail view




  - Add rank indicators and score badges
  - Add expandable sections for long descriptions
  - Style with TailwindCSS with hover effects
  - **DO NOT** modify the reverse index or company data structures
  - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 4.6_

- [ ] 14. Build ResultsDisplay component


  - **READ THE WHOLE PROJECT FIRST** - Understand query types and response formats
  - **READ**: backend/app/services/classifier.py - How queries are classified (INCENTIVE vs COMPANY)




  - **READ**: backend/app/models.py - QueryResponse structure
  - Create `frontend/src/components/ResultsDisplay.tsx`
  - Route to IncentiveCard or CompanyCard based on query type
  - Handle loading states with skeleton loaders
  - Display "No results found" message with suggestions
  - Add error message display
  - **DO NOT** change query classification logic
  - _Requirements: 2.5, 3.6, 9.5_


- [ ] 15. Build ChatInterface component




  - **READ THE WHOLE PROJECT FIRST** - Understand the chat-based query interface
  - **READ**: UI.md - ChatGPT-like interface requirements
  - **READ**: backend/app/api/routes.py - Query endpoint behavior
  - Create `frontend/src/components/ChatInterface.tsx`
  - Implement chat message history state management
  - Render user messages and assistant responses
  - Add auto-scroll to latest message
  - Implement "New Chat" button to clear history
  - Style with ChatGPT-like layout
  - **DO NOT** modify backend query processing
  - _Requirements: 4.1, 4.3, 4.4, 4.5, 4.7, 4.8_



- [ ] 16. Build main App component and routing






  - **READ THE WHOLE PROJECT FIRST** - Understand the navigation flow
  - **READ**: UI.md - Interface requirements and navigation patterns
  - **READ**: backend/app/api/routes.py - Available detail endpoints
  - Create `frontend/src/App.tsx` with React Router setup
  - Create routes: `/` (chat), `/incentive/:id`, `/company/:id`
  - Create `frontend/src/pages/IncentiveDetailPage.tsx` for incentive detail view
  - Create `frontend/src/pages/CompanyDetailPage.tsx` for company detail view
  - Integrate ChatInterface and QueryInput components on home route
  - Add header with logo, "New Chat" button, and back navigation

  - Implement responsive layout (desktop/tablet/mobile)
  - Add dark mode support (optional)
  - **DO NOT** add new backend routes or modify existing ones
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



- [x] 19. Write backend tests
  - Set up pytest with test fixtures
  - Write unit tests for QueryClassifier with mocked OpenAI
  - Write unit tests for SemanticSearchService with mocked Qdrant
  - Write unit tests for DatabaseService with test database
  - Write integration tests for `/api/query` endpoint
  - _Requirements: All backend requirements_



- [ ] 20. Write documentation


  - **READ THE WHOLE PROJECT FIRST** - Understand the complete system before documenting
  - **READ**: All existing .md files to understand current documentation
  - **IMPORTANT**: Update README.md at the END, adding webchat section WITHOUT removing existing content
  - Document API endpoints with example requests/responses
  - Add architecture diagram showing how UI integrates with existing system
  - Document environment variables (both backend and frontend)
  - Add troubleshooting guide for the UI layer
  - **DO NOT** remove or modify existing documentation about the matching system
  - _Requirements: 8.5_

- [ ] 21. End-to-end testing and polish


  - Test full flow: query → classification → search → display
  - Test navigation: click company → see incentives, click incentive → see companies
  - Test error scenarios (API down, timeout, no results)
  - Test responsive design on different screen sizes
  - Optimize loading times and add performance monitoring
  - Fix any UI/UX issues
  - _Requirements: All requirements_

- [ ] 22. Future: Create incentive embeddings for multi-result queries
  - Create script `scripts/create_incentive_embeddings.py`
  - Generate embeddings for all incentives using `paraphrase-multilingual-MiniLM-L12-v2`
  - Store embeddings in new Qdrant collection `incentives`
  - Update search service to use vector search for incentives
  - Implement multi-result display (top 3-5) for general queries
  - Add result filtering and ranking
  - _Requirements: Future enhancement for better search quality_

---

## UI/UX Design Refinement Tasks

**GOAL**: Create a state-of-the-art, beautiful, and highly usable interface using Playwright MCP for visual testing and iteration.

- [ ] 23. Research best-in-class UI/UX patterns for search interfaces


  - **USE Context7 MCP** to research modern search UI patterns and best practices
  - Research Context7 docs for: TailwindCSS, React design patterns, shadcn/ui components
  - Study ChatGPT-like interfaces: clean layouts, card designs, hover states, transitions
  - Research best practices for:
    - Clickable company/incentive names with clear visual affordance (underlines, hover effects, cursor changes)
    - Card layouts with proper spacing, shadows, and hierarchy
    - Color schemes for scores/rankings (green for high, yellow for medium, etc.)
    - Loading states and skeleton screens
    - Empty states and error messages
    - Responsive design patterns
  - Document findings and create a design checklist for implementation
  - _Requirements: 4.1, 4.6, 4.7, 4.8_

- [ ] 24. Set up Playwright MCP for visual testing


  - **USE Desktop Commander MCP** to initialize the frontend dev server
  - Start backend API: `conda activate turing0.1 && cd backend && uvicorn app.main:app --reload`
  - Start frontend dev server: `cd frontend && npm run dev`
  - **USE Playwright MCP** to navigate to http://localhost:5173
  - Take initial screenshots of the current UI state
  - Learn Playwright MCP commands:
    - `browser_snapshot` - Get accessibility tree of current page
    - `browser_take_screenshot` - Capture visual state
    - `browser_click` - Interact with elements
    - `browser_type` - Enter text in inputs
  - Test basic navigation flow and document any issues
  - _Requirements: 4.1, 9.5_

- [ ] 25. First design iteration - Core UI improvements


  - **USE Playwright MCP** to take screenshots of current state
  - **USE Context7 MCP** to look up TailwindCSS utility classes and modern design patterns
  - Implement improvements based on task 23 research:
    - Make company and incentive names clearly clickable (underline on hover, color change, cursor pointer)
    - Improve card designs with better shadows, borders, and spacing
    - Add smooth hover transitions and animations
    - Improve typography hierarchy (larger titles, better contrast)
    - Add visual indicators for scores (progress bars, badges, color coding)
    - Improve loading states with skeleton screens
    - Add empty state illustrations/messages
  - **USE Playwright MCP** to take screenshots after changes
  - Compare before/after and identify remaining issues
  - _Requirements: 2.5, 3.6, 4.6, 4.7_

- [ ] 26. Second design iteration - Polish and refinement


  - **USE Playwright MCP** to test full user flow with screenshots:
    - Search for an incentive → view results → click company → view company detail
    - Search for a company → view results → click incentive → view incentive detail
  - **USE Context7 MCP** to research advanced UI patterns (micro-interactions, transitions)
  - Refine based on visual testing:
    - Add micro-interactions (button press effects, card lift on hover)
    - Improve color palette and contrast ratios for accessibility
    - Add icons for better visual communication (location icons, score badges, external link icons)
    - Improve spacing and alignment consistency
    - Add smooth page transitions
    - Ensure all clickable elements have clear visual affordance
  - **USE Playwright MCP** to take final screenshots
  - Test on different viewport sizes (mobile, tablet, desktop)
  - _Requirements: 4.6, 4.7, 4.8, 9.5_

- [ ] 27. Final design validation and documentation


  - **USE Playwright MCP** to capture final screenshots of all key screens:
    - Home page with empty state
    - Search results for incentive query
    - Search results for company query
    - Incentive detail page
    - Company detail page
    - Error states
    - Loading states
  - Create a visual design document with before/after comparisons
  - Document all design decisions and patterns used
  - Verify all interactive elements:
    - All company names are clickable and navigate correctly
    - All incentive titles are clickable and navigate correctly
    - Hover states work consistently
    - Loading states appear correctly
    - Error messages are clear and helpful
  - Get user feedback and make final adjustments
  - _Requirements: 4.1, 4.6, 4.7, 4.8, 9.5_

---

## Summary

**Total Tasks**: 27 (excluding future enhancements)
**Completed**: 10 backend tasks + reverse index
**Remaining**: 11 frontend tasks + documentation + E2E testing + 5 design refinement tasks

**Next Steps**: Start with task 8.1 (install frontend dependencies), then proceed with frontend component development (tasks 9-18), followed by design refinement (tasks 23-27).
