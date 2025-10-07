/**
 * API service layer for communicating with the backend
 * 
 * Backend API runs on http://localhost:8000 with endpoints at /api/*
 * 
 * DO NOT modify backend endpoints or add new ones.
 * This service layer matches the existing backend API exactly.
 */

import axios from 'axios';
import type { AxiosError, AxiosInstance } from 'axios';
import type {
  QueryRequest,
  QueryResponse,
  IncentiveResult,
  CompanyResult,
  ErrorResponse,
} from '../types/api';
import { API_BASE_URL, API_ENDPOINTS } from '../types/api';

/**
 * Custom error class for API errors
 */
export class ApiError extends Error {
  public statusCode?: number;
  public detail?: string;

  constructor(
    message: string,
    statusCode?: number,
    detail?: string
  ) {
    super(message);
    this.name = 'ApiError';
    this.statusCode = statusCode;
    this.detail = detail;
  }
}

/**
 * Configuration for the API client
 */
const API_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds matching backend API_TIMEOUT
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Create axios instance with default configuration
 */
const apiClient: AxiosInstance = axios.create(API_CONFIG);

/**
 * Request interceptor for logging (development only)
 */
apiClient.interceptors.request.use(
  (config) => {
    if (import.meta.env.DEV) {
      console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor for error handling
 */
apiClient.interceptors.response.use(
  (response) => {
    if (import.meta.env.DEV) {
      console.log(`[API] Response:`, response.data);
    }
    return response;
  },
  (error: AxiosError<ErrorResponse>) => {
    // Handle different error scenarios
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      const message = data?.error || error.message || 'An error occurred';
      const detail = data?.detail ?? undefined;
      
      console.error(`[API] Error ${status}:`, message, detail);
      throw new ApiError(message, status, detail);
    } else if (error.request) {
      // Request made but no response received
      console.error('[API] No response from server:', error.message);
      throw new ApiError(
        'Service unavailable. Please check your connection and try again.',
        503
      );
    } else {
      // Error setting up the request
      console.error('[API] Request setup error:', error.message);
      throw new ApiError('Failed to make request', 0, error.message);
    }
  }
);

/**
 * Retry logic for failed requests
 * 
 * @param fn - The function to retry
 * @param retries - Number of retry attempts (default: 2)
 * @param delay - Delay between retries in ms (default: 1000)
 */
async function withRetry<T>(
  fn: () => Promise<T>,
  retries: number = 2,
  delay: number = 1000
): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    if (retries > 0 && error instanceof ApiError) {
      // Only retry on network errors or 5xx server errors
      if (!error.statusCode || error.statusCode >= 500) {
        console.log(`[API] Retrying... (${retries} attempts left)`);
        await new Promise((resolve) => setTimeout(resolve, delay));
        return withRetry(fn, retries - 1, delay * 1.5); // Exponential backoff
      }
    }
    throw error;
  }
}

/**
 * Query incentives or companies based on natural language input
 * 
 * @param query - User's natural language query (1-500 characters)
 * @returns Query response with results
 * @throws ApiError if request fails
 * 
 * @example
 * const response = await queryIncentivesOrCompanies('tech incentives');
 * if (response.query_type === 'INCENTIVE') {
 *   // Handle incentive results
 * }
 */
export async function queryIncentivesOrCompanies(
  query: string
): Promise<QueryResponse> {
  // Validate query length (matching backend validation)
  if (!query || query.length < 1) {
    throw new ApiError('Query cannot be empty', 400);
  }
  if (query.length > 500) {
    throw new ApiError('Query too long (max 500 characters)', 400);
  }

  const request: QueryRequest = { query };

  return withRetry(async () => {
    const response = await apiClient.post<QueryResponse>(
      API_ENDPOINTS.query,
      request
    );
    return response.data;
  });
}

/**
 * Get detailed information about a specific incentive
 * 
 * @param incentiveId - The incentive ID to fetch
 * @returns Incentive data with matched companies
 * @throws ApiError if incentive not found or request fails
 * 
 * @example
 * const incentive = await getIncentiveDetail('INC001');
 * console.log(incentive.title, incentive.matched_companies);
 */
export async function getIncentiveDetail(
  incentiveId: string
): Promise<IncentiveResult> {
  if (!incentiveId) {
    throw new ApiError('Incentive ID is required', 400);
  }

  return withRetry(async () => {
    const response = await apiClient.get<IncentiveResult>(
      API_ENDPOINTS.incentiveDetail(incentiveId)
    );
    return response.data;
  });
}

/**
 * Get detailed information about a specific company
 * 
 * @param companyId - The company ID to fetch
 * @returns Company data with eligible incentives
 * @throws ApiError if company not found or request fails
 * 
 * @example
 * const company = await getCompanyDetail(12345);
 * console.log(company.company_name, company.eligible_incentives);
 */
export async function getCompanyDetail(
  companyId: number
): Promise<CompanyResult> {
  if (!companyId || companyId <= 0) {
    throw new ApiError('Valid company ID is required', 400);
  }

  return withRetry(async () => {
    const response = await apiClient.get<CompanyResult>(
      API_ENDPOINTS.companyDetail(companyId)
    );
    return response.data;
  });
}

/**
 * Check if the backend API is healthy
 * 
 * @returns true if API is healthy, false otherwise
 * 
 * @example
 * const isHealthy = await checkHealth();
 * if (!isHealthy) {
 *   showError('Backend service is unavailable');
 * }
 */
export async function checkHealth(): Promise<boolean> {
  try {
    const response = await apiClient.get(API_ENDPOINTS.health, {
      timeout: 5000, // Shorter timeout for health check
    });
    return response.status === 200;
  } catch (error) {
    console.error('[API] Health check failed:', error);
    return false;
  }
}

/**
 * Export the axios instance for advanced use cases
 * (e.g., custom requests, file uploads)
 */
export { apiClient };
