/**
 * Example usage of the API service layer
 * 
 * This file demonstrates how to use the API service in components.
 * DO NOT import this file in production code - it's for reference only.
 */

import {
  queryIncentivesOrCompanies,
  getIncentiveDetail,
  getCompanyDetail,
  checkHealth,
  ApiError,
} from './api';
import { debounce } from '../utils/debounce';
import type { QueryResponse } from '../types/api';

// Example 1: Basic query
async function exampleBasicQuery() {
  try {
    const response = await queryIncentivesOrCompanies('tech incentives');
    
    console.log(`Query type: ${response.query_type}`);
    console.log(`Found ${response.result_count} results`);
    console.log(`Processing time: ${response.processing_time}s`);
    
    if (response.query_type === 'INCENTIVE') {
      // Handle incentive results
      response.results.forEach((result) => {
        if ('title' in result) {
          console.log(`Incentive: ${result.title}`);
          console.log(`Companies: ${result.matched_companies?.length || 0}`);
        }
      });
    } else {
      // Handle company results
      response.results.forEach((result) => {
        if ('company_name' in result) {
          console.log(`Company: ${result.company_name}`);
          console.log(`Incentives: ${result.eligible_incentives?.length || 0}`);
        }
      });
    }
  } catch (error) {
    if (error instanceof ApiError) {
      console.error(`API Error ${error.statusCode}: ${error.message}`);
      if (error.detail) {
        console.error(`Detail: ${error.detail}`);
      }
    } else {
      console.error('Unexpected error:', error);
    }
  }
}

// Example 2: Get incentive detail
async function exampleGetIncentive(incentiveId: string) {
  try {
    const incentive = await getIncentiveDetail(incentiveId);
    
    console.log(`Title: ${incentive.title}`);
    console.log(`Sector: ${incentive.sector}`);
    console.log(`Description: ${incentive.ai_description}`);
    
    incentive.matched_companies.forEach((company, index) => {
      console.log(`${index + 1}. ${company.name} (Score: ${company.company_score})`);
    });
  } catch (error) {
    if (error instanceof ApiError && error.statusCode === 404) {
      console.error('Incentive not found');
    } else {
      console.error('Error fetching incentive:', error);
    }
  }
}

// Example 3: Get company detail
async function exampleGetCompany(companyId: number) {
  try {
    const company = await getCompanyDetail(companyId);
    
    console.log(`Name: ${company.company_name}`);
    console.log(`CAE: ${company.cae_classification}`);
    console.log(`Activities: ${company.activities}`);
    
    company.eligible_incentives.forEach((incentive, index) => {
      console.log(`${index + 1}. ${incentive.title} (Score: ${incentive.company_score})`);
    });
  } catch (error) {
    if (error instanceof ApiError && error.statusCode === 404) {
      console.error('Company not found');
    } else {
      console.error('Error fetching company:', error);
    }
  }
}

// Example 4: Debounced search (for use in React components)
const debouncedSearch = debounce(async (query: string, callback: (results: QueryResponse) => void) => {
  try {
    const results = await queryIncentivesOrCompanies(query);
    callback(results);
  } catch (error) {
    console.error('Search failed:', error);
  }
}, 500);

// Example usage in a React component:
/*
function SearchComponent() {
  const [results, setResults] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSearch = (query: string) => {
    if (!query.trim()) {
      setResults(null);
      return;
    }

    setLoading(true);
    setError(null);

    debouncedSearch(query, (response) => {
      setResults(response);
      setLoading(false);
    });
  };

  return (
    <div>
      <input
        type="text"
        onChange={(e) => handleSearch(e.target.value)}
        placeholder="Search incentives or companies..."
      />
      {loading && <div>Loading...</div>}
      {error && <div>Error: {error}</div>}
      {results && <ResultsDisplay results={results} />}
    </div>
  );
}
*/

// Example 5: Health check before making requests
async function exampleHealthCheck() {
  const isHealthy = await checkHealth();
  
  if (!isHealthy) {
    console.error('Backend service is unavailable');
    // Show error message to user
    return;
  }
  
  // Proceed with API calls
  console.log('Backend is healthy, proceeding with requests');
}

// Example 6: Error handling patterns
async function exampleErrorHandling(query: string) {
  try {
    const response = await queryIncentivesOrCompanies(query);
    return response;
  } catch (error) {
    if (error instanceof ApiError) {
      switch (error.statusCode) {
        case 400:
          console.error('Invalid request:', error.message);
          // Show validation error to user
          break;
        case 404:
          console.error('Not found:', error.message);
          // Show "no results" message
          break;
        case 500:
          console.error('Server error:', error.message);
          // Show "try again later" message
          break;
        case 503:
          console.error('Service unavailable:', error.message);
          // Show "service down" message
          break;
        default:
          console.error('Unknown error:', error.message);
      }
    } else {
      console.error('Unexpected error:', error);
    }
    return null;
  }
}

// Export examples for reference
export {
  exampleBasicQuery,
  exampleGetIncentive,
  exampleGetCompany,
  debouncedSearch,
  exampleHealthCheck,
  exampleErrorHandling,
};
