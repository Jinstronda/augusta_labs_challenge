"""
Pydantic models for API requests and responses
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


# Request models

class QueryRequest(BaseModel):
    """Request model for query endpoint"""
    query: str = Field(..., min_length=1, max_length=500, description="User's natural language query")


# Response models - Company

class CompanyMatch(BaseModel):
    """Company match in incentive results"""
    id: int
    name: str
    cae_classification: Optional[str] = None
    activities: Optional[str] = None
    website: Optional[str] = None
    location_address: Optional[str] = None
    rank: Optional[int] = None
    company_score: Optional[float] = None
    semantic_score: Optional[float] = None
    score_components: Optional[Dict[str, Any]] = None


class IncentiveResult(BaseModel):
    """Incentive result with matched companies"""
    incentive_id: str
    title: str
    description: Optional[str] = None
    ai_description: Optional[str] = None
    eligibility_criteria: Optional[str] = None
    sector: Optional[str] = None
    geo_requirement: Optional[str] = None
    eligible_actions: Optional[str] = None
    funding_rate: Optional[str] = None
    investment_eur: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    total_budget: Optional[float] = None
    source_link: Optional[str] = None
    matched_companies: List[CompanyMatch] = []


# Response models - Incentive

class IncentiveMatch(BaseModel):
    """Incentive match in company results"""
    incentive_id: str
    title: str
    description: Optional[str] = None
    ai_description: Optional[str] = None
    sector: Optional[str] = None
    geo_requirement: Optional[str] = None
    eligible_actions: Optional[str] = None
    funding_rate: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    source_link: Optional[str] = None
    rank: Optional[int] = None
    company_score: Optional[float] = None


class CompanyResult(BaseModel):
    """Company result with eligible incentives"""
    company_id: int
    company_name: str
    cae_classification: Optional[str] = None
    activities: Optional[str] = None
    website: Optional[str] = None
    location_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    eligible_incentives: List[IncentiveMatch] = []


# Main query response

class QueryResponse(BaseModel):
    """Response model for query endpoint"""
    query_type: Literal["COMPANY_NAME", "COMPANY_TYPE", "INCENTIVE_NAME", "INCENTIVE_TYPE"]
    query: str
    cleaned_query: str  # The extracted/cleaned search terms
    results: List[Any]  # Will be List[IncentiveResult] or List[CompanyResult]
    result_count: int
    processing_time: float
    confidence: Optional[str] = None


# Error response

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    status_code: int
