    """
semantic search for companies and incentives

uses qdrant for vector search and postgresql for keyword search
"""

import logging
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
import psycopg2

from app.config import settings

logger = logging.getLogger(__name__)


class SemanticSearchService:
    """
    searches companies and incentives using embeddings
    
    models are loaded once at startup and reused
    """
    
    def __init__(self, embedding_model: SentenceTransformer, qdrant_client: QdrantClient):
        """
        takes pre-loaded models to avoid loading them on every request
        """
        self.embedding_model = embedding_model
        self.qdrant_client = qdrant_client
        self.companies_collection = settings.QDRANT_COLLECTION
        self.incentives_collection = "incentives"  # New collection for incentives
        
        logger.info(f"SemanticSearchService initialized")
        logger.info(f"  Companies collection: {self.companies_collection}")
        logger.info(f"  Incentives collection: {self.incentives_collection}")
    
    def search_companies(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        find companies using vector similarity
        
        embeds the query and searches 250k companies in qdrant
        """
        logger.info(f"Searching companies for query: {query[:100]}...")
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query, convert_to_tensor=False)
            
            # Convert to list if numpy array
            if hasattr(query_embedding, 'tolist'):
                query_embedding = query_embedding.tolist()
            
            # Search in Qdrant companies collection
            search_results = self.qdrant_client.search(
                collection_name=self.companies_collection,
                query_vector=query_embedding,
                limit=limit * 2,  # Get more results for filtering
                with_payload=True
            )
            
            # Format results
            companies = []
            for result in search_results[:limit]:
                payload = result.payload
                
                # Company ID is stored as the point ID in Qdrant, not in payload
                companies.append({
                    'id': result.id,  # Use point ID as company ID
                    'name': payload.get('company_name'),
                    'cae_classification': payload.get('cae_primary_label'),
                    'activities': payload.get('trade_description_native'),
                    'website': payload.get('website'),
                    'score': float(result.score),
                    'confidence': self._calculate_confidence(result.score)
                })
            
            logger.info(f"Found {len(companies)} companies")
            return companies
            
        except Exception as e:
            logger.error(f"Error searching companies: {e}")
            raise
    
    def search_incentives_semantic(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        find incentives using vector similarity
        
        better than keyword search for understanding what the user wants
        """
        logger.info(f"Searching incentives semantically for query: {query[:100]}...")
        
        try:
            # Check if incentives collection exists
            collections = self.qdrant_client.get_collections().collections
            has_incentives = any(c.name == self.incentives_collection for c in collections)
            
            if not has_incentives:
                logger.warning(f"Incentives collection '{self.incentives_collection}' not found, falling back to keyword search")
                return self.search_incentives(query, limit)
            
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query, convert_to_tensor=False)
            
            # Convert to list if numpy array
            if hasattr(query_embedding, 'tolist'):
                query_embedding = query_embedding.tolist()
            
            # Search in Qdrant incentives collection
            search_results = self.qdrant_client.search(
                collection_name=self.incentives_collection,
                query_vector=query_embedding,
                limit=limit,
                with_payload=True
            )
            
            # Format results
            incentives = []
            for result in search_results:
                payload = result.payload
                
                incentives.append({
                    'incentive_id': payload.get('incentive_id'),
                    'title': payload.get('title'),
                    'description': None,  # Not in payload
                    'ai_description': payload.get('ai_description'),
                    'sector': payload.get('sector'),
                    'geo_requirement': payload.get('geo_requirement'),
                    'eligible_actions': payload.get('eligible_actions'),
                    'funding_rate': None,  # Not in payload
                    'investment_eur': None,  # Not in payload
                    'start_date': None,  # Not in payload
                    'end_date': None,  # Not in payload
                    'total_budget': None,  # Not in payload
                    'source_link': None,  # Not in payload
                    'relevance_score': float(result.score),
                    'confidence': self._calculate_confidence(result.score)
                })
            
            logger.info(f"Found {len(incentives)} incentives via semantic search")
            return incentives
            
        except Exception as e:
            logger.error(f"Error in semantic incentive search: {e}, falling back to keyword search")
            return self.search_incentives(query, limit)
    
    def search_incentives(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        find incentives using keyword matching in postgresql
        
        simple and fast for 300 incentives
        """
        logger.info(f"Searching incentives for query: {query[:100]}...")
        
        try:
            # Connect to database
            conn = psycopg2.connect(
                dbname=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                host=settings.DB_HOST,
                port=settings.DB_PORT
            )
            cursor = conn.cursor()
            
            # Prepare search query with keyword matching
            # Use ILIKE for case-insensitive search
            search_pattern = f"%{query}%"
            
            cursor.execute("""
                SELECT 
                    incentive_id,
                    title,
                    description,
                    ai_description,
                    sector,
                    geo_requirement,
                    eligible_actions,
                    funding_rate,
                    investment_eur,
                    start_date,
                    end_date,
                    total_budget,
                    source_link,
                    -- Calculate relevance score based on matches
                    (
                        CASE WHEN title ILIKE %s THEN 10 ELSE 0 END +
                        CASE WHEN sector ILIKE %s THEN 5 ELSE 0 END +
                        CASE WHEN eligible_actions ILIKE %s THEN 3 ELSE 0 END +
                        CASE WHEN description ILIKE %s THEN 1 ELSE 0 END
                    ) as relevance_score
                FROM incentives
                WHERE 
                    title ILIKE %s OR
                    description ILIKE %s OR
                    ai_description ILIKE %s OR
                    sector ILIKE %s OR
                    eligible_actions ILIKE %s
                ORDER BY relevance_score DESC, title
                LIMIT %s
            """, (
                search_pattern, search_pattern, search_pattern, search_pattern,  # For score calculation
                search_pattern, search_pattern, search_pattern, search_pattern, search_pattern,  # For WHERE clause
                limit
            ))
            
            results = cursor.fetchall()
            
            # Format results
            incentives = []
            for row in results:
                (
                    incentive_id, title, description, ai_description, sector,
                    geo_requirement, eligible_actions, funding_rate, investment_eur,
                    start_date, end_date, total_budget, source_link, relevance_score
                ) = row
                
                incentives.append({
                    'incentive_id': incentive_id,
                    'title': title,
                    'description': description,
                    'ai_description': ai_description,
                    'sector': sector,
                    'geo_requirement': geo_requirement,
                    'eligible_actions': eligible_actions,
                    'funding_rate': funding_rate,
                    'investment_eur': investment_eur,
                    'start_date': start_date.isoformat() if start_date else None,
                    'end_date': end_date.isoformat() if end_date else None,
                    'total_budget': float(total_budget) if total_budget else None,
                    'source_link': source_link,
                    'relevance_score': relevance_score,
                    'confidence': self._calculate_confidence(relevance_score / 10.0)  # Normalize to 0-1
                })
            
            cursor.close()
            conn.close()
            
            logger.info(f"Found {len(incentives)} incentives")
            return incentives
            
        except Exception as e:
            logger.error(f"Error searching incentives: {e}")
            raise
    
    def _calculate_confidence(self, score: float) -> str:
        """
        turn score into high/medium/low confidence
        """
        # Normalize score to 0-1 range if needed
        if score > 1.0:
            score = min(score / 10.0, 1.0)
        
        if score >= 0.7:
            return "high"
        elif score >= 0.4:
            return "medium"
        else:
            return "low"
