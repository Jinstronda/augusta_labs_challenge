"""
Query classification service using GPT-5-mini

Classifies user queries as either INCENTIVE or COMPANY queries to route
them to the appropriate search service.
"""

import json
import logging
from typing import Literal
from openai import OpenAI

from app.config import settings

logger = logging.getLogger(__name__)

QueryType = Literal["SPECIFIC_COMPANY", "COMPANY_GROUP", "SPECIFIC_INCENTIVE", "INCENTIVE_GROUP"]


class QueryClassifier:
    """
    Classifies queries using GPT-5-mini with fallback to keyword-based classification.
    
    Supports 4 query types:
    1. SPECIFIC_COMPANY - User asks for a specific company by name
    2. COMPANY_GROUP - User asks for companies in a market/sector/group
    3. SPECIFIC_INCENTIVE - User asks for a specific incentive by name/ID
    4. INCENTIVE_GROUP - User asks for a group of incentives (funding type, sector, etc.)
    
    Uses the same pattern as the existing codebase for GPT-5-mini integration.
    """
    
    def __init__(self):
        """Initialize OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def classify(self, query: str) -> QueryType:
        """
        Classify a query into one of 4 types.
        
        Uses GPT-5-mini to understand the user's intent and classify the query.
        Falls back to keyword-based classification if GPT fails.
        
        Args:
            query: User's natural language query
            
        Returns:
            One of: "SPECIFIC_COMPANY", "COMPANY_GROUP", "SPECIFIC_INCENTIVE", "INCENTIVE_GROUP"
        """
        logger.info(f"Classifying query: {query[:100]}...")
        
        try:
            # Try GPT-5-mini classification first
            result = self._classify_with_gpt(query)
            logger.info(f"GPT classification: {result}")
            return result
            
        except Exception as e:
            logger.warning(f"GPT classification failed: {e}, using fallback")
            # Fallback to keyword-based classification
            result = self._classify_with_keywords(query)
            logger.info(f"Keyword classification: {result}")
            return result
    
    def _classify_with_gpt(self, query: str) -> QueryType:
        """
        Use GPT-5-mini to classify the query.
        
        Follows the exact pattern from enhanced_incentive_matching.py
        """
        prompt = self._create_classification_prompt(query)
        
        logger.debug(f"GPT prompt length: {len(prompt)} characters")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=100
                # Note: GPT-5-mini only supports temperature=1 (default)
            )
            
            # Parse response
            result_text = response.choices[0].message.content.strip()
            logger.debug(f"GPT response: '{result_text}'")
            
            if not result_text:
                raise ValueError("Empty response from GPT")
            
            # Extract JSON from response (handle cases where GPT adds explanation)
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = result_text[json_start:json_end]
                logger.debug(f"Extracted JSON: '{json_text}'")
                result_data = json.loads(json_text)
                
                # Get classification from JSON
                classification = result_data.get('type', '').upper()
                
                valid_types = ['SPECIFIC_COMPANY', 'COMPANY_GROUP', 'SPECIFIC_INCENTIVE', 'INCENTIVE_GROUP']
                if classification in valid_types:
                    return classification
                else:
                    raise ValueError(f"Invalid classification: {classification}")
            else:
                # Try to parse the whole response as JSON
                result_data = json.loads(result_text)
                classification = result_data.get('type', '').upper()
                
                valid_types = ['SPECIFIC_COMPANY', 'COMPANY_GROUP', 'SPECIFIC_INCENTIVE', 'INCENTIVE_GROUP']
                if classification in valid_types:
                    return classification
                else:
                    raise ValueError(f"Invalid classification: {classification}")
                    
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ValueError(f"Failed to parse GPT response as JSON: {result_text}")
        except Exception as e:
            logger.error(f"GPT classification error: {e}")
            raise
    
    def _create_classification_prompt(self, query: str) -> str:
        """
        Create prompt for GPT-5-mini classification.
        
        Uses a simple, direct format similar to the geographic analysis prompt.
        """
        return f"""Classify this query into ONE of these 4 types:

1. SPECIFIC_COMPANY - User asks for a specific company by name
   Examples: "Show me Microsoft", "Find Galp Energia", "Information about Tesla"

2. COMPANY_GROUP - User asks for companies in a market/sector/category
   Examples: "Companies in renewable energy", "Tech startups in Lisbon", "Manufacturing companies"

3. SPECIFIC_INCENTIVE - User asks for a specific incentive by name or ID
   Examples: "Show me Digital Innovation Fund", "Incentive 1288", "PRR funding details"

4. INCENTIVE_GROUP - User asks for a group/category of incentives
   Examples: "Green energy incentives", "R&D funding programs", "Startup grants"

Query: "{query}"

Return JSON only with the type: {{"type": "SPECIFIC_COMPANY"}} or {{"type": "COMPANY_GROUP"}} or {{"type": "SPECIFIC_INCENTIVE"}} or {{"type": "INCENTIVE_GROUP"}}

JSON:"""
    
    def _classify_with_keywords(self, query: str) -> QueryType:
        """
        Fallback keyword-based classification.
        
        Uses simple keyword matching when GPT is unavailable.
        """
        query_lower = query.lower()
        
        # Check for specific company indicators (proper names, specific company terms)
        specific_company_indicators = ['lda', 'sa', 'unipessoal', 'ltd', 'inc', 'corp']
        has_specific_company = any(ind in query_lower for ind in specific_company_indicators)
        
        # Keywords that suggest INCENTIVE query
        incentive_keywords = [
            'incentivo', 'incentivos', 'apoio', 'apoios', 'financiamento',
            'fundo', 'fundos', 'subsídio', 'subsídios', 'grant', 'grants',
            'funding', 'programa', 'programas', 'candidatura', 'candidaturas',
            'concurso', 'concursos', 'aviso', 'avisos'
        ]
        
        # Keywords that suggest COMPANY query
        company_keywords = [
            'empresa', 'empresas', 'company', 'companies', 'negócio', 'negócios',
            'companhia', 'companhias', 'sociedade', 'sociedades',
            'business', 'businesses'
        ]
        
        # Keywords that suggest GROUP query (multiple results)
        group_keywords = [
            'empresas', 'companies', 'incentivos', 'grants', 'programas',
            'sector', 'setor', 'mercado', 'market', 'indústria', 'industry'
        ]
        
        # Count keyword matches
        incentive_score = sum(1 for kw in incentive_keywords if kw in query_lower)
        company_score = sum(1 for kw in company_keywords if kw in query_lower)
        is_group = any(kw in query_lower for kw in group_keywords)
        
        logger.debug(f"Keyword scores - Incentive: {incentive_score}, Company: {company_score}, Group: {is_group}")
        
        # Determine classification
        if company_score > incentive_score:
            if has_specific_company or not is_group:
                return "SPECIFIC_COMPANY"
            else:
                return "COMPANY_GROUP"
        else:
            if is_group:
                return "INCENTIVE_GROUP"
            else:
                return "SPECIFIC_INCENTIVE"
