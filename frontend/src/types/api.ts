/**
 * TypeScript types matching backend API models
 */

export type QueryType = "SPECIFIC_COMPANY" | "COMPANY_GROUP" | "SPECIFIC_INCENTIVE" | "INCENTIVE_GROUP";

// Company types
export interface CompanyMatch {
  id: number;
  name: string;
  cae_classification?: string;
  activities?: string;
  website?: string;
  location_address?: string;
  rank?: number;
  company_score?: number;
  semantic_score?: number;
  score_components?: Record<string, any>;
}

export interface IncentiveResult {
  incentive_id: string;
  title: string;
  description?: string;
  ai_description?: string;
  eligibility_criteria?: string;
  sector?: string;
  geo_requirement?: string;
  eligible_actions?: string;
  funding_rate?: string;
  investment_eur?: string;
  start_date?: string;
  end_date?: string;
  total_budget?: number;
  source_link?: string;
  matched_companies: CompanyMatch[];
  confidence?: string;
  relevance_score?: number;
}

// Incentive types
export interface IncentiveMatch {
  incentive_id: string;
  title: string;
  description?: string;
  ai_description?: string;
  sector?: string;
  geo_requirement?: string;
  eligible_actions?: string;
  funding_rate?: string;
  start_date?: string;
  end_date?: string;
  source_link?: string;
  rank?: number;
  company_score?: number;
}

export interface CompanyResult {
  company_id: number;
  company_name: string;
  cae_classification?: string;
  activities?: string;
  website?: string;
  location_address?: string;
  location_lat?: number;
  location_lon?: number;
  eligible_incentives: IncentiveMatch[];
  confidence?: string;
  search_score?: number;
}

// Query types
export interface QueryRequest {
  query: string;
}

export interface QueryResponse {
  query_type: QueryType;
  query: string;
  results: (IncentiveResult | CompanyResult)[];
  result_count: number;
  processing_time: number;
  confidence?: string;
}

export interface ErrorResponse {
  error: string;
  detail?: string;
  status_code: number;
}
