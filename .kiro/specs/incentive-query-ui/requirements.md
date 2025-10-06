# Requirements Document

## Introduction

This feature provides a ChatGPT-like web interface for querying the incentive-company matching system. Users can ask natural language questions about either incentives or companies, and the system intelligently routes the query to return relevant results with ranked matches.

The system uses an LLM-based query classifier to determine intent (incentive search vs company search), then retrieves and displays the appropriate data with clear, intuitive formatting. The UI is optimized for performance, easy to host, and built with modern JavaScript frameworks.

## Requirements

### Requirement 1: Query Classification

**User Story:** As a user, I want to type natural language queries so that I can find incentives or companies without knowing the exact search syntax.

#### Acceptance Criteria

1. WHEN a user submits a query THEN the system SHALL use an LLM to classify the query as either "INCENTIVE" or "COMPANY" type
2. WHEN the query mentions incentive names, programs, or funding types THEN the system SHALL classify it as "INCENTIVE"
3. WHEN the query mentions company names, industries, or business activities THEN the system SHALL classify it as "COMPANY"
4. WHEN the classification is ambiguous THEN the system SHALL default to "INCENTIVE" search
5. WHEN classification fails THEN the system SHALL return a helpful error message suggesting query reformulation

### Requirement 2: Incentive Search Results

**User Story:** As a user searching for incentives, I want to see the incentive details and its top matching companies so that I can understand which businesses would benefit most.

#### Acceptance Criteria

1. WHEN a query is classified as "INCENTIVE" THEN the system SHALL search for matching incentives using PostgreSQL keyword search
2. WHEN an incentive is found THEN the system SHALL display the incentive's title, description, sector, geographic requirement, and eligible actions
3. WHEN an incentive is found THEN the system SHALL display the top 5 companies ranked by company score from `top_5_companies_scored`
4. WHEN displaying companies THEN the system SHALL show company name, score, CAE classification, website, and location as clickable cards
5. WHEN a user clicks on a company card THEN the system SHALL navigate to that company's detail view showing its eligible incentives
6. WHEN no matching incentive is found THEN the system SHALL display a "No results found" message with suggestions

### Requirement 3: Company Search Results

**User Story:** As a user searching for companies, I want to see which incentives the company is eligible for so that I can identify funding opportunities.

#### Acceptance Criteria

1. WHEN a query is classified as "COMPANY" THEN the system SHALL search for matching companies using Qdrant vector search
2. WHEN a company is found THEN the system SHALL display the company's name, CAE classification, activities, website, and location
3. WHEN a company is found THEN the system SHALL retrieve all incentives from the pre-computed `eligible_incentives` JSONB column
4. WHEN displaying incentives THEN the system SHALL show the incentive title, the company's rank, the company's score as clickable cards
5. WHEN a user clicks on an incentive card THEN the system SHALL navigate to that incentive's detail view showing its top 5 companies
6. WHEN displaying incentives THEN the system SHALL sort them by the company's score (highest first)
7. WHEN no matching company is found THEN the system SHALL display a "No results found" message

### Requirement 4: ChatGPT-like Interface

**User Story:** As a user, I want a clean, familiar chat interface so that I can easily interact with the system.

#### Acceptance Criteria

1. WHEN the page loads THEN the system SHALL display a centered chat input box with placeholder text
2. WHEN a user types a query THEN the system SHALL show a send button or allow Enter key submission
3. WHEN a query is submitted THEN the system SHALL display the user's message in the chat history
4. WHEN processing a query THEN the system SHALL show a loading indicator
5. WHEN results are ready THEN the system SHALL display them as a formatted response in the chat history
6. WHEN displaying results THEN the system SHALL use cards, badges, and clear typography for readability
7. WHEN the chat history grows THEN the system SHALL auto-scroll to the latest message
8. WHEN a user wants to start over THEN the system SHALL provide a "New Chat" button to clear history

### Requirement 5: Backend API

**User Story:** As a developer, I want a clean REST API so that the frontend can efficiently query the database.

#### Acceptance Criteria

1. WHEN the backend starts THEN it SHALL expose a `/api/query` endpoint accepting POST requests
2. WHEN `/api/query` receives a query THEN it SHALL classify the query type using an LLM
3. WHEN the query type is "INCENTIVE" THEN it SHALL search incentives using keyword search and return top match with companies
4. WHEN the query type is "COMPANY" THEN it SHALL search companies using vector embeddings and return top match with incentives
5. WHEN a detail page requests an incentive by ID THEN it SHALL return the incentive data with top 5 companies
6. WHEN a detail page requests a company by ID THEN it SHALL return the company data with eligible incentives
7. WHEN database queries fail THEN the system SHALL return appropriate HTTP error codes (500) with error messages
8. WHEN the API returns results THEN it SHALL include query type, matched entity, and related entities in JSON format
9. WHEN the backend starts THEN it SHALL connect to PostgreSQL using environment variables for configuration

### Requirement 6: Performance Optimization

**User Story:** As a user, I want fast query responses so that I can efficiently explore the data.

#### Acceptance Criteria

1. WHEN the backend starts THEN it SHALL load embedding models once as singletons (not per request)
2. WHEN searching for companies THEN the system SHALL use Qdrant vector search with pre-computed embeddings
3. WHEN searching for incentives THEN the system SHALL use PostgreSQL keyword search (dataset is small)
4. WHEN retrieving company locations THEN the system SHALL use cached data from the database
5. WHEN loading the frontend THEN the system SHALL use code splitting and lazy loading for optimal bundle size
6. WHEN rendering results THEN the system SHALL use virtual scrolling if displaying large lists
7. WHEN making API calls THEN the system SHALL implement request debouncing to avoid excessive queries

### Requirement 7: Reverse Index Generation

**User Story:** As a developer, I want companies to have pre-computed eligible incentives so that company queries are fast.

#### Acceptance Criteria

1. WHEN the batch processing completes THEN a script SHALL build a reverse index of company→incentives
2. WHEN building the reverse index THEN the script SHALL iterate through all incentives with `top_5_companies_scored`
3. WHEN processing each incentive THEN the script SHALL extract all companies and their scores from the JSON
4. WHEN a company appears in multiple incentives THEN the script SHALL collect all incentive matches for that company
5. WHEN all incentives are processed THEN the script SHALL keep only the top 5 incentives per company (by score)
6. WHEN saving the reverse index THEN the script SHALL store results in `companies.eligible_incentives` as JSONB
7. WHEN the reverse index is complete THEN company queries SHALL use this pre-computed data instead of scanning all incentives

### Requirement 8: Deployment and Hosting

**User Story:** As a developer, I want easy deployment options so that I can host the application with minimal configuration.

#### Acceptance Criteria

1. WHEN deploying the backend THEN it SHALL be containerizable with Docker
2. WHEN deploying the frontend THEN it SHALL be buildable as static files for hosting on any web server
3. WHEN configuring the application THEN it SHALL use environment variables for all configuration (database, API keys, etc.)
4. WHEN the application starts THEN it SHALL include health check endpoints for monitoring
5. WHEN documentation is needed THEN it SHALL include a README with setup and deployment instructions

### Requirement 9: Error Handling and User Feedback

**User Story:** As a user, I want clear error messages so that I understand what went wrong and how to fix it.

#### Acceptance Criteria

1. WHEN the backend is unreachable THEN the system SHALL display a "Service unavailable" message
2. WHEN a query takes too long THEN the system SHALL show a timeout message after 30 seconds
3. WHEN the LLM classification fails THEN the system SHALL fall back to keyword-based classification
4. WHEN database queries fail THEN the system SHALL log errors and display a user-friendly message
5. WHEN no results are found THEN the system SHALL suggest alternative queries or broader search terms
