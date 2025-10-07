/**
 * API service for communicating with the backend
 */

import type {
  QueryRequest,
  QueryResponse,
  IncentiveResult,
  CompanyResult,
} from "@/types/api";

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_TIMEOUT = 30000; // 30 seconds

class ApiError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public detail?: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/**
 * Query incentives or companies based on natural language input
 */
export async function queryIncentivesOrCompanies(
  query: string
): Promise<QueryResponse> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(`${API_BASE_URL}/api/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ query } as QueryRequest),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.error || "Query failed",
        response.status,
        errorData.detail
      );
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error) {
      if (error.name === "AbortError") {
        throw new ApiError("Request timeout - please try again", 408);
      }
      throw new ApiError(error.message);
    }

    throw new ApiError("An unexpected error occurred");
  }
}

/**
 * Get detailed information about a specific incentive
 */
export async function getIncentiveDetail(
  incentiveId: string
): Promise<IncentiveResult> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/incentive/${incentiveId}`,
      {
        signal: controller.signal,
      }
    );

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.error || "Failed to fetch incentive",
        response.status,
        errorData.detail
      );
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error) {
      if (error.name === "AbortError") {
        throw new ApiError("Request timeout - please try again", 408);
      }
      throw new ApiError(error.message);
    }

    throw new ApiError("An unexpected error occurred");
  }
}

/**
 * Get detailed information about a specific company
 */
export async function getCompanyDetail(
  companyId: number
): Promise<CompanyResult> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_TIMEOUT);

  try {
    const response = await fetch(`${API_BASE_URL}/api/company/${companyId}`, {
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.error || "Failed to fetch company",
        response.status,
        errorData.detail
      );
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof ApiError) {
      throw error;
    }

    if (error instanceof Error) {
      if (error.name === "AbortError") {
        throw new ApiError("Request timeout - please try again", 408);
      }
      throw new ApiError(error.message);
    }

    throw new ApiError("An unexpected error occurred");
  }
}

/**
 * Check if the backend is healthy and ready
 */
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`, {
      method: "GET",
    });

    if (response.ok) {
      const data = await response.json();
      return data.status === "healthy";
    }
    return false;
  } catch (error) {
    return false;
  }
}

/**
 * Wait for backend to be ready with retries
 */
export async function waitForBackend(
  maxRetries: number = 30,
  retryDelay: number = 1000
): Promise<boolean> {
  for (let i = 0; i < maxRetries; i++) {
    const isHealthy = await checkBackendHealth();
    if (isHealthy) {
      return true;
    }
    await new Promise((resolve) => setTimeout(resolve, retryDelay));
  }
  return false;
}

export { ApiError };
