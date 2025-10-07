# API Service Layer

This directory contains the API service layer for communicating with the backend.

## Overview

The API service provides a clean interface for making requests to the backend API running on `http://localhost:8000`.

## Features

- ✅ Type-safe API calls with TypeScript
- ✅ Automatic retry logic for failed requests
- ✅ Request/response interceptors for logging
- ✅ 30-second timeout matching backend configuration
- ✅ Comprehensive error handling
- ✅ Input validation

## Usage

### Query Incentives or Companies

```typescript
import { queryIncentivesOrCompanies } from '@/services';

try {
  const response = await queryIncentivesOrCompanies('tech incentives');
  
  if (response.query_type === 'INCENTIVE') {
    // Handle incentive results
    response.results.forEach((incentive) => {
      console.log(incentive.title);
      console.log(incentive.matched_companies);
    });
  } else {
    // Handle company results
    response.results.forEach((company) => {
      console.log(company.company_name);
      console.log(company.eligible_incentives);
    });
  }
} catch (error) {
  if (error instanceof ApiError) {
    console.error(`Error ${error.statusCode}: ${error.message}`);
  }
}
```

### Get Incentive Detail

```typescript
import { getIncentiveDetail } from '@/services';

try {
  const incentive = await getIncentiveDetail('INC001');
  console.log(incentive.title);
  console.log(incentive.matched_companies);
} catch (error) {
  if (error instanceof ApiError && error.statusCode === 404) {
    console.error('Incentive not found');
  }
}
```

### Get Company Detail

```typescript
import { getCompanyDetail } from '@/services';

try {
  const company = await getCompanyDetail(12345);
  console.log(company.company_name);
  console.log(company.eligible_incentives);
} catch (error) {
  if (error instanceof ApiError && error.statusCode === 404) {
    console.error('Company not found');
  }
}
```

### Check Backend Health

```typescript
import { checkHealth } from '@/services';

const isHealthy = await checkHealth();
if (!isHealthy) {
  showError('Backend service is unavailable');
}
```

### Debouncing API Calls

```typescript
import { debounce } from '@/utils';
import { queryIncentivesOrCompanies } from '@/services';

// Create debounced search function
const debouncedSearch = debounce(async (query: string) => {
  try {
    const results = await queryIncentivesOrCompanies(query);
    setResults(results);
  } catch (error) {
    console.error('Search failed:', error);
  }
}, 500); // Wait 500ms after user stops typing

// Use in input handler
const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
  const query = e.target.value;
  debouncedSearch(query);
};

// Cancel pending search
debouncedSearch.cancel();
```

## Error Handling

The API service throws `ApiError` instances with the following properties:

- `message`: Human-readable error message
- `statusCode`: HTTP status code (if available)
- `detail`: Additional error details from backend

Common error scenarios:

- **400**: Invalid request (e.g., empty query, query too long)
- **404**: Resource not found (incentive or company)
- **500**: Server error
- **503**: Service unavailable (backend not reachable)

## Configuration

The API client is configured with:

- **Base URL**: `http://localhost:8000`
- **Timeout**: 30 seconds (matching backend)
- **Retry Logic**: 2 retries with exponential backoff for 5xx errors
- **Headers**: `Content-Type: application/json`

## Testing

Run tests with:

```bash
npm test src/services/__tests__/api.test.ts
```

## Notes

- **DO NOT** modify backend endpoints or add new ones
- All types must match `backend/app/models.py` exactly
- The API client automatically retries failed requests
- Request/response logging is enabled in development mode only
