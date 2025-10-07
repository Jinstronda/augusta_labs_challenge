"""
query classifier using gemini 2.5 flash

figures out what the user wants and routes to the right search
"""

import json
import logging
from typing import Literal, Tuple
from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)

QueryType = Literal["COMPANY_NAME", "COMPANY_TYPE", "INCENTIVE_NAME", "INCENTIVE_TYPE"]


class QueryClassifier:
    """
    uses gemini to classify queries, falls back to keywords if needed
    
    four types:
    - company_name: "find microsoft"
    - company_type: "tech companies in lisbon"
    - incentive_name: "digital innovation fund"
    - incentive_type: "green energy incentives"
    
    returns the type and a cleaned search term
    """
    
    def __init__(self):
        """load gemini client"""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    def classify(self, query: str) -> Tuple[QueryType, str]:
        """
        figure out what type of query this is and clean it up
        
        returns (query_type, cleaned_query)
        """
        logger.info(f"Classifying query: {query[:100]}...")
        
        try:
            # Try Gemini classification first
            query_type, cleaned_query = self._classify_with_gemini(query)
            logger.info(f"Gemini classification: {query_type}, cleaned: {cleaned_query}")
            return query_type, cleaned_query
            
        except Exception as e:
            logger.warning(f"Gemini classification failed: {e}, using fallback")
            # Fallback to keyword-based classification
            query_type, cleaned_query = self._classify_with_keywords(query)
            logger.info(f"Keyword classification: {query_type}, cleaned: {cleaned_query}")
            return query_type, cleaned_query
    
    def _classify_with_gemini(self, query: str) -> Tuple[QueryType, str]:
        """ask gemini to classify"""
        prompt = self._create_classification_prompt(query)
        
        logger.debug(f"Gemini prompt length: {len(prompt)} characters")
        
        try:
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=1000,
                    response_mime_type='application/json'
                )
            )
            
            # Check if response has text
            if not response or not response.text:
                raise ValueError("Empty or None response from Gemini")
            
            result_text = response.text.strip()
            logger.debug(f"Gemini response: '{result_text}'")
            
            if not result_text:
                raise ValueError("Empty response text from Gemini")
            
            result_data = json.loads(result_text)
            classification = result_data.get('type', '').upper()
            cleaned_query = result_data.get('query', '').strip()
            
            valid_types = ['COMPANY_NAME', 'COMPANY_TYPE', 'INCENTIVE_NAME', 'INCENTIVE_TYPE']
            if classification in valid_types and cleaned_query:
                return classification, cleaned_query
            else:
                raise ValueError(f"Invalid classification: {classification} or empty query")
                    
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ValueError(f"Failed to parse Gemini response as JSON: {result_text}")
        except Exception as e:
            logger.error(f"Gemini classification error: {e}")
            raise
    
    def _create_classification_prompt(self, query: str) -> str:
        """build the prompt"""
        return f"""Classify this query and extract the search terms.

Types:
1. COMPANY_NAME - User asks for a specific company by name
   Extract: Just the company name
   Example: "I want company named joao" → {{"type": "COMPANY_NAME", "query": "joao"}}
   Example: "Show me Microsoft" → {{"type": "COMPANY_NAME", "query": "Microsoft"}}

2. COMPANY_TYPE - User asks for companies in a market/sector/category
   Extract: The sector/category terms
   Example: "I want electrical companies" → {{"type": "COMPANY_TYPE", "query": "electrical companies"}}
   Example: "Tech startups in Lisbon" → {{"type": "COMPANY_TYPE", "query": "tech startups lisbon"}}

3. INCENTIVE_NAME - User asks for a specific incentive by name or ID
   Extract: Just the incentive name/ID
   Example: "Show me Digital Innovation Fund" → {{"type": "INCENTIVE_NAME", "query": "Digital Innovation Fund"}}
   Example: "Incentive 1288" → {{"type": "INCENTIVE_NAME", "query": "1288"}}

4. INCENTIVE_TYPE - User asks for a group/category of incentives
   Extract: The category/type terms
   Example: "Green energy incentives" → {{"type": "INCENTIVE_TYPE", "query": "green energy"}}
   Example: "R&D funding programs" → {{"type": "INCENTIVE_TYPE", "query": "R&D funding"}}

User Query: "{query}"

Return JSON with type and cleaned query: {{"type": "COMPANY_NAME", "query": "extracted terms"}}

JSON:"""
    
    def _classify_with_keywords(self, query: str) -> Tuple[QueryType, str]:
        """fallback if gemini fails"""
        query_lower = query.lower()
        
        # Strong indicators for specific company (legal entity suffixes)
        specific_company_indicators = ['lda', 'sa', 'unipessoal', 'ltd', 'inc', 'corp']
        has_specific_company = any(ind in query_lower for ind in specific_company_indicators)
        
        # Explicit company keywords (high priority)
        explicit_company_keywords = ['company', 'empresa', 'companhia', 'named', 'called']
        has_explicit_company = any(kw in query_lower for kw in explicit_company_keywords)
        
        incentive_keywords = [
            'incentivo', 'incentivos', 'apoio', 'apoios', 'financiamento',
            'fundo', 'fundos', 'subsídio', 'subsídios', 'grant', 'grants',
            'funding', 'programa', 'programas', 'candidatura', 'candidaturas',
            'concurso', 'concursos', 'aviso', 'avisos'
        ]
        
        company_keywords = [
            'empresa', 'empresas', 'company', 'companies', 'negócio', 'negócios',
            'companhia', 'companhias', 'sociedade', 'sociedades',
            'business', 'businesses'
        ]
        
        type_keywords = [
            'empresas', 'companies', 'incentivos', 'grants', 'programas',
            'sector', 'setor', 'mercado', 'market', 'indústria', 'industry',
            'type', 'tipo', 'category', 'categoria'
        ]
        
        incentive_score = sum(1 for kw in incentive_keywords if kw in query_lower)
        company_score = sum(1 for kw in company_keywords if kw in query_lower)
        is_type = any(kw in query_lower for kw in type_keywords)
        
        logger.debug(f"Keyword scores - Incentive: {incentive_score}, Company: {company_score}, Type: {is_type}, HasCompanyIndicator: {has_specific_company}, ExplicitCompany: {has_explicit_company}")
        
        # If explicit company keyword is present, it's definitely a company query
        if has_explicit_company or (has_specific_company and company_score > 0):
            if is_type and not has_specific_company:
                return "COMPANY_TYPE", query
            else:
                return "COMPANY_NAME", query
        
        # Otherwise use score-based classification
        if company_score > incentive_score:
            if has_specific_company or not is_type:
                return "COMPANY_NAME", query
            else:
                return "COMPANY_TYPE", query
        else:
            if is_type:
                return "INCENTIVE_TYPE", query
            else:
                return "INCENTIVE_NAME", query
