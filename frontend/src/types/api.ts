/**
 * TypeScript types matching backend/app/models.py EXACTLY
 * 
 * DO NOT modify these types without updating the backend Pydantic models first.
 * These types must stay in sync with the backend API.
 */

// Request types

export interface QueryRequest {
  query: string; // min_length=1, max_length=500
}

// Company types

export interface CompanyMatch {
  id: number;
  name: string;
  cae_classification: string | null;
  activities: string | null;
  website: string | null;
  location_address: string | null;
  rank: number | null;
  company_score: number | null;
  semantic_score: number | null;
  score_components: Record<string, any> | null;
}

export interface IncentiveResult {
  incentive_id: string;
  title: string;
  description: string | null;
  ai_description: string | null;
  eligibility_criteria: string | null;
  sector: string | null;
  geo_requirement: string | null;
  eligible_actions: string | null;
  funding_rate: string | null;
  investment_eur: string | null;
  start_date: string | null;
  end_date: string | null;
  total_budget: number | null;
  source_link: string | null;
  matched_companies: CompanyMatch[];
}

// Incentive types

export interface IncentiveMatch {
  incentive_id: string;
  title: string;
  description: string | null;
  ai_description: string | null;
  sector: string | null;
  geo_requirement: string | null;
  eligible_actions: string | null;
  funding_rate: string | null;
  start_date: string | null;
  end_date: string | null;
  source_link: string | null;
  rank: number | null;
  company_score: number | null;
}

export interface CompanyResult {
  company_id: number;
  company_name: string;
  cae_classification: string | null;
  activities: string | null;
  website: string | null;
  location_address: string | null;
  location_lat: number | null;
  location_lon: number | null;
  eligible_incentives: IncentiveMatch[];
}

// Main query response

export type QueryType = "INCENTIVE" | "COMPANY";

export interface QueryResponse {
  query_type: QueryType;
  query: string;
  results: IncentiveResult[] | CompanyResult[];
  result_count: number;
  processing_time: number;
  confidence: string | null;
}

// Type guards to check which type of results we have

export function isIncentiveResults(
  response: QueryResponse
): response is QueryResponse & { results: IncentiveResult[] } {
  return response.query_type === "INCENTIVE";
}

export function isCompanyResults(
  response: QueryResponse
): response is QueryResponse & { results: CompanyResult[] } {
  return response.query_type === "COMPANY";
}

// Error response

export interface ErrorResponse {
  error: string;
  detail: string | null;
  status_code: number;
}

// API endpoints (for reference)

export const API_BASE_URL = "http://localhost:8000";

export const API_ENDPOINTS = {
  query: "/api/query",
  incentiveDetail: (id: string) => `/api/incentive/${id}`,
  companyDetail: (id: number) => `/api/company/${id}`,
  health: "/health",
} as const;
