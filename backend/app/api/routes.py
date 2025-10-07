"""
api routes for the query system
"""

import time
import logging
from fastapi import APIRouter, HTTPException, Depends
from typing import List

from app.models import (
    QueryRequest, QueryResponse, IncentiveResult, CompanyResult,
    CompanyMatch, IncentiveMatch, ErrorResponse
)
from app.services.classifier import QueryClassifier
from app.services.search import SemanticSearchService
from app.services.database import DatabaseService

logger = logging.getLogger(__name__)

router = APIRouter()


def get_services():
    """load the services with singleton models"""
    # Import here to avoid circular import
    from app.main import get_app_state
    app_state = get_app_state()
    
    # Initialize services with singleton models
    classifier = QueryClassifier()
    search_service = SemanticSearchService(
        embedding_model=app_state['embedding_model'],
        qdrant_client=app_state['qdrant_client']
    )
    db_service = DatabaseService()
    
    return classifier, search_service, db_service


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """
    main endpoint - classifies query and returns results
    """
    start_time = time.time()
    
    logger.info(f"Received query: {request.query}")
    
    try:
        # Get services
        classifier, search_service, db_service = get_services()
        
        # Step 1: Classify query and extract search terms
        query_type, cleaned_query = classifier.classify(request.query)
        logger.info(f"Query classified as: {query_type}, cleaned: {cleaned_query}")
        
        # Step 2: Route based on classification
        if query_type == "COMPANY_NAME":
            results = await _handle_company_name_query(cleaned_query, db_service)
            confidence = results[0].get('confidence', 'high') if results else None
        elif query_type == "COMPANY_TYPE":
            results = await _handle_company_type_query(cleaned_query, search_service, db_service)
            confidence = results[0].get('confidence', 'medium') if results else None
        elif query_type == "INCENTIVE_NAME":
            results = await _handle_incentive_name_query(cleaned_query, search_service, db_service)
            confidence = results[0].get('confidence', 'high') if results else None
        else:  # INCENTIVE_TYPE
            results = await _handle_incentive_type_query(cleaned_query, search_service, db_service)
            confidence = results[0].get('confidence', 'medium') if results else None
        
        # Step 3: Calculate processing time
        processing_time = time.time() - start_time
        
        logger.info(f"Query completed in {processing_time:.2f}s with {len(results)} results")
        
        return QueryResponse(
            query_type=query_type,
            query=request.query,
            cleaned_query=cleaned_query,
            results=results,
            result_count=len(results),
            processing_time=processing_time,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _handle_company_name_query(query: str, db_service: DatabaseService) -> List[dict]:
    """
    find one company by exact name match
    """
    logger.info(f"Handling COMPANY_NAME query: {query}")
    
    # Search PostgreSQL for company by name
    company_data = db_service.search_company_by_name(query)
    
    if company_data:
        company_data['confidence'] = 'high'  # Direct name match
        return [company_data]
    
    return []


async def _handle_company_type_query(query: str, search_service: SemanticSearchService,
                                     db_service: DatabaseService) -> List[dict]:
    """
    Handle COMPANY_TYPE query: search for top 5 companies in a market/sector using semantic search.
    Returns simplified company details without full incentive lists.
    """
    logger.info(f"Handling COMPANY_TYPE query: {query}")
    
    # Search for companies using semantic search
    company_matches = search_service.search_companies(query, limit=5)
    
    # Return simplified company data (without fetching all incentives for performance)
    results = []
    for match in company_matches:
        company_id = match['id']
        
        # Get basic company data
        company_data = db_service.get_company_basic(company_id)
        
        if company_data:
            # Add search metadata
            company_data['confidence'] = match.get('confidence')
            company_data['search_score'] = match.get('score')
            results.append(company_data)
    
    return results


async def _handle_incentive_name_query(query: str, search_service: SemanticSearchService,
                                       db_service: DatabaseService) -> List[dict]:
    """
    Handle INCENTIVE_NAME query: search for ONE specific incentive by name.
    Returns the incentive with its top 5 matched companies.
    """
    logger.info(f"Handling INCENTIVE_NAME query: {query}")
    
    # Search for the specific incentive (limit=1 to get best match)
    incentive_matches = search_service.search_incentives(query, limit=1)
    
    if not incentive_matches:
        return []
    
    # Get the top match
    incentive_id = incentive_matches[0]['incentive_id']
    
    # Get full incentive data with matched companies
    incentive_data = db_service.get_incentive_with_companies(incentive_id)
    
    if incentive_data:
        # Add search metadata
        incentive_data['confidence'] = 'high'  # Specific name search
        incentive_data['relevance_score'] = incentive_matches[0].get('relevance_score')
        return [incentive_data]
    
    return []


async def _handle_incentive_type_query(query: str, search_service: SemanticSearchService,
                                      db_service: DatabaseService) -> List[dict]:
    """
    Handle INCENTIVE_TYPE query: search for multiple incentives matching criteria.
    Uses semantic search (Qdrant) if available, falls back to keyword search.
    Returns top 5 incentives with their matched companies.
    """
    logger.info(f"Handling INCENTIVE_TYPE query: {query}")
    
    # Get matches from semantic search
    incentive_matches = search_service.search_incentives_semantic(query, limit=5)
    
    if not incentive_matches:
        logger.info("No incentive matches found")
        return []
    
    # For each incentive, get full details with matched companies
    results = []
    for match in incentive_matches:
        incentive_id = match['incentive_id']
        
        # Get full incentive data with companies
        incentive_data = db_service.get_incentive_with_companies(incentive_id)
        
        if incentive_data:
            # Add search metadata
            incentive_data['confidence'] = match.get('confidence')
            incentive_data['relevance_score'] = match.get('relevance_score')
            results.append(incentive_data)
    
    return results


@router.get("/incentive/{incentive_id}")
async def get_incentive_detail(incentive_id: str):
    """
    Get detailed information about a specific incentive with its matched companies.
    
    Args:
        incentive_id: The incentive ID to fetch
        
    Returns:
        Incentive data with matched companies
    """
    logger.info(f"Fetching incentive detail: {incentive_id}")
    
    try:
        # Create database service (doesn't need app_state)
        db_service = DatabaseService()
        
        # Fetch incentive with companies
        incentive_data = db_service.get_incentive_with_companies(incentive_id)
        
        if not incentive_data:
            raise HTTPException(status_code=404, detail=f"Incentive {incentive_id} not found")
        
        logger.info(f"Incentive {incentive_id} fetched successfully")
        return incentive_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching incentive {incentive_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/company/{company_id}")
async def get_company_detail(company_id: int):
    """
    Get detailed information about a specific company with its eligible incentives.
    
    Args:
        company_id: The company ID to fetch
        
    Returns:
        Company data with eligible incentives
    """
    logger.info(f"Fetching company detail: {company_id}")
    
    try:
        # Create database service (doesn't need app_state)
        db_service = DatabaseService()
        
        # Fetch company with incentives
        company_data = db_service.get_company_with_incentives(company_id)
        
        if not company_data:
            raise HTTPException(status_code=404, detail=f"Company {company_id} not found")
        
        logger.info(f"Company {company_id} fetched successfully")
        return company_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching company {company_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify backend is ready.
    
    Returns:
        Status information about the backend services
    """
    try:
        from app.main import get_app_state
        app_state = get_app_state()
        
        return {
            "status": "healthy",
            "services": {
                "embedding_model": app_state['embedding_model'] is not None,
                "qdrant_client": app_state['qdrant_client'] is not None,
            },
            "message": "Backend is ready"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Backend not ready")
