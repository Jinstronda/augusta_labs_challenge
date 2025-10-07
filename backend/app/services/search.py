"""
Semantic search service for companies and incentives

Provides vector search for companies using Qdrant and keyword search
for incentives using PostgreSQL.
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
    Service for semantic search of companies and incentives.
    
    Uses singleton models loaded at app startup for optimal performance.
    """
    
    def __init__(self, embedding_model: SentenceTransformer, qdrant_client: QdrantClient):
        """
        Initialize search service with pre-loaded models.
        
        Args:
            embedding_model: Pre-loaded sentence transformer model
            qdrant_client: Pre-initialized Qdrant client
        """
        self.embedding_model = embedding_model
        self.qdrant_client = qdrant_client
        self.collection_name = settings.QDRANT_COLLECTION
        
        logger.info(f"SemanticSearchService initialized with collection: {self.collection_name}")
    
    def search_companies(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for companies using semantic vector search.
        
        Uses the existing Qdrant vector DB with 250k company records.
        Generates query embedding and performs similarity search.
        
        Args:
            query: Natural language query
            limit: Maximum number of results (default 5)
            
        Returns:
            List of company matches with scores and metadata
        """
        logger.info(f"Searching companies for query: {query[:100]}...")
        
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query, convert_to_tensor=False)
            
            # Convert to list if numpy array
            if hasattr(query_embedding, 'tolist'):
                query_embedding = query_embedding.tolist()
            
            # Search in Qdrant
            search_results = self.qdrant_client.search(
                collection_name=self.collection_name,
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
    
    def search_incentives(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search for incentives using PostgreSQL keyword search.
        
        Uses simple keyword matching since the incentive dataset is small (~300 records).
        Searches in title, description, sector, and eligible_actions fields.
        
        Args:
            query: Natural language query
            limit: Maximum number of results (default 5)
            
        Returns:
            List of incentive matches with metadata
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
        Calculate confidence level from similarity score.
        
        Args:
            score: Similarity score (0-1 for vector search, 0-10+ for keyword search)
            
        Returns:
            Confidence level: "high", "medium", or "low"
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
