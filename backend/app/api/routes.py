"""
API routes for the Incentive Query API
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
    """Dependency to get initialized services"""
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
    Main query endpoint for searching incentives or companies.
    
    Classifies the query, performs semantic search, and returns formatted results.
    """
    start_time = time.time()
    
    logger.info(f"Received query: {request.query}")
    
    try:
        # Get services
        classifier, search_service, db_service = get_services()
        
        # Step 1: Classify query
        query_type = classifier.classify(request.query)
        logger.info(f"Query classified as: {query_type}")
        
        # Step 2: Route based on classification
        if query_type == "SPECIFIC_COMPANY":
            results = await _handle_specific_company_query(request.query, search_service, db_service)
            confidence = results[0].get('confidence', 'medium') if results else None
        elif query_type == "COMPANY_GROUP":
            results = await _handle_company_group_query(request.query, search_service, db_service)
            confidence = results[0].get('confidence', 'medium') if results else None
        elif query_type == "SPECIFIC_INCENTIVE":
            results = await _handle_specific_incentive_query(request.query, search_service, db_service)
            confidence = results[0].get('confidence', 'medium') if results else None
        else:  # INCENTIVE_GROUP
            results = await _handle_incentive_group_query(request.query, search_service, db_service)
            confidence = results[0].get('confidence', 'medium') if results else None
        
        # Step 3: Calculate processing time
        processing_time = time.time() - start_time
        
        logger.info(f"Query completed in {processing_time:.2f}s with {len(results)} results")
        
        return QueryResponse(
            query_type=query_type,
            query=request.query,
            results=results,
            result_count=len(results),
            processing_time=processing_time,
            confidence=confidence
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _handle_specific_company_query(query: str, search_service: SemanticSearchService,
                                        db_service: DatabaseService) -> List[dict]:
    """
    Handle SPECIFIC_COMPANY query: search for ONE specific company and return with top 5 incentives.
    """
    logger.info("Handling SPECIFIC_COMPANY query")
    
    # Search for the specific company (limit=1 to get best match)
    company_matches = search_service.search_companies(query, limit=1)
    
    if not company_matches:
        return []
    
    # Get the top match
    company_id = company_matches[0]['id']
    
    # Get full company data with eligible incentives
    company_data = db_service.get_company_with_incentives(company_id)
    
    if company_data:
        # Add search metadata
        company_data['confidence'] = company_matches[0].get('confidence')
        company_data['search_score'] = company_matches[0].get('score')
        return [company_data]
    
    return []


async def _handle_company_group_query(query: str, search_service: SemanticSearchService,
                                      db_service: DatabaseService) -> List[dict]:
    """
    Handle COMPANY_GROUP query: search for top 5 companies in a market/sector.
    Returns simplified company details without full incentive lists.
    """
    logger.info("Handling COMPANY_GROUP query")
    
    # Search for companies
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


async def _handle_specific_incentive_query(query: str, search_service: SemanticSearchService,
                                          db_service: DatabaseService) -> List[dict]:
    """
    Handle SPECIFIC_INCENTIVE query: search for ONE specific incentive and return with top 5 companies.
    """
    logger.info("Handling SPECIFIC_INCENTIVE query")
    
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
        incentive_data['confidence'] = incentive_matches[0].get('confidence')
        incentive_data['relevance_score'] = incentive_matches[0].get('relevance_score')
        return [incentive_data]
    
    return []


async def _handle_incentive_group_query(query: str, search_service: SemanticSearchService,
                                       db_service: DatabaseService) -> List[dict]:
    """
    Handle INCENTIVE_GROUP query: search for multiple incentives matching criteria.
    Returns top 5 incentives with their matched companies.
    """
    logger.info("Handling INCENTIVE_GROUP query")
    
    # Search for incentives
    incentive_matches = search_service.search_incentives(query, limit=5)
    
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
