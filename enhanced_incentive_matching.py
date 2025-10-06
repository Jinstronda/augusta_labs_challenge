"""
Enhanced Incentive-Company Matching with Geographic Filtering

This system extends the basic semantic matching with geographic eligibility checking.
The core challenge is that companies must not only be semantically relevant to an
incentive, but also be located in the right geographic area.

The system uses a three-stage pipeline:
1. Semantic matching (vector search + reranking)
2. Geographic enrichment (Google Maps API + caching)
3. Geographic filtering (GPT-5-mini analysis)

If fewer than 5 companies meet both semantic and geographic criteria, the system
automatically expands the search from 20 to 30 candidates and repeats the process.

Architecture:
    Incentive -> Semantic Search -> Location Enrichment -> Geographic Analysis -> Results

Key Components:
- LocationService: Manages Google Maps API calls and database caching
- GeographicAnalyzer: Uses GPT-5-mini to determine geographic eligibility
- EnhancedMatchingPipeline: Orchestrates the complete flow with iterative logic
- DatabaseManager: Handles all database operations including result storage

The system is designed to be robust against API failures, rate limits, and
ambiguous geographic requirements while maintaining high matching quality.
"""

import os
import json
import time
import requests
import psycopg2
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from FlagEmbedding import FlagReranker
from openai import OpenAI
import torch

# Load environment variables
load_dotenv('config.env')

# Configuration
DB_NAME = os.getenv("DB_NAME", "incentives_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

GOOGLE_MAPS_API_KEY = "AIzaSyAKWaDFzEYZKxhuwumj1fmv-IHmz_pAGw8"
OPENAI_API_KEY = os.getenv("OPEN_AI")

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY)
device = "cuda" if torch.cuda.is_available() else "cpu"

print(f"[SYSTEM] Using device: {device}")


@dataclass
class CompanyLocation:
    """Represents a company's geographic location with metadata."""
    company_id: int
    latitude: Optional[float]
    longitude: Optional[float]
    formatted_address: Optional[str]
    api_status: str  # 'success', 'not_found', 'api_error', 'cached'
    updated_at: Optional[datetime]


@dataclass
class MatchingResult:
    """Represents the final matching result for an incentive."""
    incentive_id: int
    companies: List[Dict]
    total_candidates_searched: int
    geographic_eligible_count: int
    processing_time: float
    created_at: datetime


class DatabaseManager:
    """
    Handles all database operations for the enhanced matching system.
    
    Manages company locations, matching results, and schema updates.
    Provides connection pooling and transaction management.
    """
    
    def __init__(self):
        self.connection_params = {
            'dbname': DB_NAME,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'host': DB_HOST,
            'port': DB_PORT
        }
    
    def get_connection(self):
        """Get a database connection."""
        return psycopg2.connect(**self.connection_params)
    
    def ensure_schema(self):
        """
        Create necessary database schema for location and matching data.
        
        Adds location columns to companies table and creates results table.
        Uses IF NOT EXISTS to avoid errors on repeated runs.
        """
        print("[DB] Ensuring database schema...")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Add metadata columns for location caching
            # Note: location_lat, location_lon, location_address already exist
            cursor.execute("""
                ALTER TABLE companies 
                ADD COLUMN IF NOT EXISTS location_updated_at TIMESTAMP,
                ADD COLUMN IF NOT EXISTS location_api_status VARCHAR(20)
            """)
            
            # Add top_5_companies column to incentives table
            cursor.execute("""
                ALTER TABLE incentives 
                ADD COLUMN IF NOT EXISTS top_5_companies JSONB
            """)
            
            # Add top_5_companies_scored column for LLM-scored results
            cursor.execute("""
                ALTER TABLE incentives 
                ADD COLUMN IF NOT EXISTS top_5_companies_scored JSONB
            """)
            
            # Migrate existing results from incentive_company_matches to incentives.top_5_companies
            cursor.execute("""
                SELECT table_name FROM information_schema.tables 
                WHERE table_name = 'incentive_company_matches'
            """)
            
            if cursor.fetchone():  # Table exists, migrate data
                print("[DB] Migrating existing results to incentives.top_5_companies...")
                
                # Get all incentives with matches
                cursor.execute("""
                    SELECT DISTINCT incentive_id FROM incentive_company_matches
                """)
                
                incentive_ids = [row[0] for row in cursor.fetchall()]
                
                for incentive_id in incentive_ids:
                    # Get top 5 companies for this incentive
                    cursor.execute("""
                        SELECT icm.company_id, icm.match_rank, icm.semantic_score, 
                               c.company_name, c.cae_primary_label, c.website,
                               icm.total_candidates_searched, icm.processing_time, icm.created_at
                        FROM incentive_company_matches icm
                        JOIN companies c ON icm.company_id = c.company_id
                        WHERE icm.incentive_id = %s
                        ORDER BY icm.match_rank
                        LIMIT 5
                    """, (incentive_id,))
                    
                    matches = cursor.fetchall()
                    
                    if matches:
                        # Build JSON structure
                        companies_data = []
                        for match in matches:
                            companies_data.append({
                                "id": match[0],
                                "rank": match[1],
                                "semantic_score": float(match[2]) if match[2] else 0,
                                "name": match[3],
                                "cae_classification": match[4],
                                "website": match[5]
                            })
                        
                        result_json = {
                            "companies": companies_data,
                            "total_candidates_searched": matches[0][6] if matches[0][6] else 20,
                            "processing_time": float(matches[0][7]) if matches[0][7] else 0,
                            "processed_at": matches[0][8].isoformat() if matches[0][8] else None,
                            "migrated_from_table": True
                        }
                        
                        # Update incentives table
                        cursor.execute("""
                            UPDATE incentives 
                            SET top_5_companies = %s 
                            WHERE incentive_id = %s
                        """, (json.dumps(result_json), incentive_id))
                
                print(f"[DB] Migrated {len(incentive_ids)} incentives with existing results")
                
                # Optionally drop the old table (commented out for safety)
                # cursor.execute("DROP TABLE IF EXISTS incentive_company_matches")
                # print("[DB] Dropped old incentive_company_matches table")
            
            # First, let's check the actual data type of incentive_id
            cursor.execute("""
                SELECT data_type 
                FROM information_schema.columns 
                WHERE table_name = 'incentives' AND column_name = 'incentive_id'
            """)
            
            incentive_id_type = cursor.fetchone()
            if incentive_id_type and incentive_id_type[0] == 'character varying':
                incentive_id_sql_type = "VARCHAR"
            else:
                incentive_id_sql_type = "INTEGER"
            
            print(f"[DB] Detected incentive_id type: {incentive_id_sql_type}")
            
            # Note: We now store results directly in incentives.top_5_companies column
            # No separate table needed
            
            conn.commit()
            print("[DB] Schema updated successfully")
    
    def get_company_location(self, company_id: int) -> Optional[CompanyLocation]:
        """
        Retrieve cached location for a company.
        
        Returns None if no location is cached, otherwise returns CompanyLocation
        with all available data including API status.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT company_id, location_lat, location_lon, location_address, 
                       location_api_status, location_updated_at
                FROM companies 
                WHERE company_id = %s AND (location_api_status IS NOT NULL OR location_lat IS NOT NULL)
            """, (company_id,))
            
            result = cursor.fetchone()
            if result:
                return CompanyLocation(
                    company_id=result[0],
                    latitude=float(result[1]) if result[1] is not None else None,
                    longitude=float(result[2]) if result[2] is not None else None,
                    formatted_address=result[3],
                    api_status=result[4] or 'success' if result[1] is not None else 'unknown',
                    updated_at=result[5]
                )
            return None
    
    def save_company_location(self, location: CompanyLocation):
        """
        Save or update company location in database.
        
        Updates the companies table with location data and metadata.
        Uses existing location columns (location_lat, location_lon, location_address).
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE companies 
                SET location_lat = %s, location_lon = %s, location_address = %s,
                    location_api_status = %s, location_updated_at = %s
                WHERE company_id = %s
            """, (
                location.latitude, location.longitude, location.formatted_address,
                location.api_status, datetime.now(), location.company_id
            ))
            conn.commit()
    
    def save_matching_results(self, result: MatchingResult):
        """
        Save matching results directly to incentives.top_5_companies column.
        
        Stores the complete matching result as JSON including all matched companies,
        their ranks, scores, and processing metadata.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build JSON structure
            companies_data = []
            for rank, company in enumerate(result.companies, 1):
                companies_data.append({
                    "id": company['id'],
                    "rank": rank,
                    "semantic_score": company.get('rerank_score', 0),
                    "name": company['name'],
                    "cae_classification": company.get('cae'),
                    "website": company.get('website'),
                    "location_address": company.get('location_address'),
                    "activities": company.get('activities', '')[:200] if company.get('activities') else None  # Truncate for JSON
                })
            
            result_json = {
                "companies": companies_data,
                "total_candidates_searched": result.total_candidates_searched,
                "processing_time": result.processing_time,
                "processed_at": result.created_at.isoformat(),
                "geographic_eligible_count": result.geographic_eligible_count
            }
            
            # Update incentives table with JSON results
            cursor.execute("""
                UPDATE incentives 
                SET top_5_companies = %s 
                WHERE incentive_id = %s
            """, (json.dumps(result_json), result.incentive_id))
            
            conn.commit()
            print(f"[DB] Saved {len(result.companies)} matching results to incentives.top_5_companies for incentive {result.incentive_id}")
    
    def save_scored_results(self, incentive_id: int, scored_companies: List[Dict], processing_time: float):
        """
        Save scored results to incentives.top_5_companies_scored column.
        
        Stores companies ranked by the Universal Company Match Formula score.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Build JSON structure with scored companies
            companies_data = []
            for rank, company in enumerate(scored_companies, 1):
                companies_data.append({
                    "id": company['id'],
                    "rank": rank,
                    "company_score": company.get('company_score', 0),
                    "semantic_score": company.get('rerank_score', 0),
                    "score_components": company.get('score_components', {}),
                    "name": company['name'],
                    "cae_classification": company.get('cae'),
                    "website": company.get('website'),
                    "location_address": company.get('location_address'),
                    "activities": company.get('activities', '')[:200] if company.get('activities') else None
                })
            
            result_json = {
                "companies": companies_data,
                "processing_time": processing_time,
                "processed_at": datetime.now().isoformat(),
                "scoring_formula": "0.50S + 0.20M + 0.10G + 0.15O' + 0.05W"
            }
            
            # Update incentives table with scored results
            cursor.execute("""
                UPDATE incentives 
                SET top_5_companies_scored = %s 
                WHERE incentive_id = %s
            """, (json.dumps(result_json), incentive_id))
            
            conn.commit()
            print(f"[DB] Saved {len(scored_companies)} scored results to incentives.top_5_companies_scored for incentive {incentive_id}")


class LocationService:
    """
    Manages company location data using Google Maps Places API.
    
    Provides intelligent caching to minimize API calls and costs.
    Handles API errors gracefully and maintains location data quality.
    
    The service uses a multi-level caching strategy:
    1. Database cache (persistent)
    2. Memory cache (session-level)
    3. API status tracking (avoid repeated failures)
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.api_key = GOOGLE_MAPS_API_KEY
        self.memory_cache = {}  # Session-level cache
        self.api_call_count = 0  # For monitoring only
    
    def get_company_location(self, company_id: int, company_name: str, 
                           existing_address: Optional[str] = None) -> CompanyLocation:
        """
        Get location for a company with intelligent caching.
        
        Checks multiple cache levels before making API calls:
        1. Memory cache (fastest)
        2. Database cache (persistent)
        3. Google Maps API (slowest, costs money)
        
        Args:
            company_id: Database ID of the company
            company_name: Company name for API search
            existing_address: Any existing address info to improve search
            
        Returns:
            CompanyLocation with all available data
        """
        # Check memory cache first
        if company_id in self.memory_cache:
            return self.memory_cache[company_id]
        
        # Check database cache
        cached_location = self.db_manager.get_company_location(company_id)
        if cached_location:
            self.memory_cache[company_id] = cached_location
            cached_location.api_status = 'cached'
            return cached_location
        
        # Call Google Maps API
        # Note: Google Maps has rate limits per minute (not per session)
        # The API will return rate limit errors if exceeded, which we handle gracefully
        location = self._call_google_maps_api(company_id, company_name, existing_address)
        
        # Cache the result
        self.memory_cache[company_id] = location
        self.db_manager.save_company_location(location)
        
        return location
    
    def _call_google_maps_api(self, company_id: int, company_name: str, 
                             existing_address: Optional[str] = None) -> CompanyLocation:
        """
        Call Google Maps Places API to get company location.
        
        Uses Text Search API to find the company by name and address.
        Includes Portugal-specific biasing to improve accuracy.
        
        Args:
            company_id: Database ID of the company
            company_name: Company name to search for
            existing_address: Optional existing address to improve search
            
        Returns:
            CompanyLocation with API results or error status
        """
        print(f"[MAPS API] Looking up location for: {company_name}")
        
        # Build search query
        search_query = company_name
        if existing_address:
            search_query += f" {existing_address}"
        search_query += " Portugal"  # Ensure we search in Portugal
        
        # API request parameters
        url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
        params = {
            'query': search_query,
            'key': self.api_key,
            'region': 'pt',  # Bias towards Portugal
            'language': 'pt',  # Portuguese language
            'type': 'establishment'  # Focus on businesses
        }
        
        try:
            response = requests.get(url, params=params, timeout=100)
            response.raise_for_status()
            data = response.json()
            
            self.api_call_count += 1
            
            # Check for rate limiting or quota issues
            if data['status'] == 'OVER_QUERY_LIMIT':
                print(f"[MAPS API] Rate limit exceeded! Waiting 60 seconds...")
                import time
                time.sleep(60)
                return CompanyLocation(
                    company_id=company_id,
                    latitude=None,
                    longitude=None,
                    formatted_address=None,
                    api_status='rate_limited',
                    updated_at=datetime.now()
                )
            
            if data['status'] == 'REQUEST_DENIED':
                print(f"[MAPS API] Request denied! Check API key. Response: {data}")
                return CompanyLocation(
                    company_id=company_id,
                    latitude=None,
                    longitude=None,
                    formatted_address=None,
                    api_status='api_error',
                    updated_at=datetime.now()
                )
            
            if data['status'] == 'OK' and data['results']:
                place = data['results'][0]  # Take first result
                
                # Log what fields are available
                available_fields = list(place.keys())
                
                # Get formatted_address with fallback
                formatted_address = place.get('formatted_address')
                if not formatted_address:
                    # Fallback: construct from available fields
                    formatted_address = place.get('name', company_name)
                    print(f"[MAPS API] No formatted_address, using fallback. Available fields: {available_fields}")
                
                # Get coordinates with error handling
                try:
                    lat = place['geometry']['location']['lat']
                    lng = place['geometry']['location']['lng']
                except KeyError as e:
                    print(f"[MAPS API] Missing geometry data: {e}. Place data: {place}")
                    return CompanyLocation(
                        company_id=company_id,
                        latitude=None,
                        longitude=None,
                        formatted_address=formatted_address,
                        api_status='incomplete_data',
                        updated_at=datetime.now()
                    )
                
                location = CompanyLocation(
                    company_id=company_id,
                    latitude=lat,
                    longitude=lng,
                    formatted_address=formatted_address,
                    api_status='success',
                    updated_at=datetime.now()
                )
                print(f"[MAPS API] Found: {location.formatted_address}")
                return location
            
            else:
                print(f"[MAPS API] No results found for: {company_name}")
                return CompanyLocation(
                    company_id=company_id,
                    latitude=None,
                    longitude=None,
                    formatted_address=None,
                    api_status='not_found',
                    updated_at=datetime.now()
                )
        
        except KeyError as e:
            print(f"[MAPS API] Missing field in response for {company_name}: {e}")
            return CompanyLocation(
                company_id=company_id,
                latitude=None,
                longitude=None,
                formatted_address=None,
                api_status='api_error',
                updated_at=datetime.now()
            )
        
        except requests.RequestException as e:
            print(f"[MAPS API] Request error for {company_name}: {e}")
            return CompanyLocation(
                company_id=company_id,
                latitude=None,
                longitude=None,
                formatted_address=None,
                api_status='api_error',
                updated_at=datetime.now()
            )


class GeographicAnalyzer:
    """
    Analyzes geographic eligibility using GPT-5-mini.
    
    Determines whether companies meet the geographic requirements of incentives
    by understanding Portuguese administrative divisions and geographic terms.
    
    The analyzer is designed to handle:
    - NUTS regions (Norte, Centro, Lisboa, etc.)
    - Municipal boundaries
    - National vs regional requirements
    - Ambiguous geographic terms
    """
    
    def __init__(self):
        self.client = openai_client
    
    def analyze_eligibility(self, companies_with_locations: List[Dict], 
                          geo_requirement: str) -> Dict[int, bool]:
        """
        Determine geographic eligibility for a list of companies.
        
        Uses GPT-5-mini to analyze whether each company's location meets
        the incentive's geographic requirement. The model understands
        Portuguese geography and administrative divisions.
        
        Args:
            companies_with_locations: List of companies with location data
            geo_requirement: Geographic requirement from incentive
            
        Returns:
            Dict mapping company_id to boolean eligibility
        """
        print(f"[GEO ANALYSIS] Analyzing {len(companies_with_locations)} companies")
        print(f"[GEO ANALYSIS] Requirement: {geo_requirement}")
        
        # Filter companies that have location data
        companies_with_valid_locations = [
            c for c in companies_with_locations 
            if (c.get('formatted_address') or c.get('location_address')) and c.get('location_api_status') == 'success'
        ]
        
        if not companies_with_valid_locations:
            print("[GEO ANALYSIS] No companies with valid locations found")
            return {c['id']: False for c in companies_with_locations}
        
        # Prepare data for GPT
        company_data = []
        for company in companies_with_valid_locations:
            address = company.get('formatted_address') or company.get('location_address')
            company_data.append({
                "company_id": company['id'],
                "name": company['name'],
                "address": address
            })
        
        # Create the prompt
        prompt = self._create_analysis_prompt(company_data, geo_requirement)
        
        print(f"[GEO ANALYSIS] Prompt length: {len(prompt)} characters")
        print(f"[GEO ANALYSIS] First 200 chars: {prompt[:200]}...")
        print(f"[GEO ANALYSIS] Last 200 chars: ...{prompt[-200:]}")
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=16000
                # Note: GPT-5-mini only supports temperature=1 (default)
            )
            
            # Parse JSON response
            result_text = response.choices[0].message.content.strip()
            print(f"[GEO ANALYSIS] GPT Response: '{result_text}'")
            print(f"[GEO ANALYSIS] Response length: {len(result_text)}")
            
            if not result_text:
                print("[GEO ANALYSIS] Empty response from GPT!")
                raise ValueError("Empty response from GPT")
            
            # Extract JSON from response (handle cases where GPT adds explanation)
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            print(f"[GEO ANALYSIS] JSON extraction: start={json_start}, end={json_end}")
            
            if json_start >= 0 and json_end > json_start:
                json_text = result_text[json_start:json_end]
                print(f"[GEO ANALYSIS] Extracted JSON: '{json_text}'")
                eligibility_results = json.loads(json_text)
            else:
                print(f"[GEO ANALYSIS] No JSON found in response: '{result_text}'")
                raise ValueError("No JSON found in GPT response")
            
            # Convert string keys to integers and ensure all companies are included
            final_results = {}
            for company in companies_with_locations:
                company_id = company['id']
                # Check if GPT provided a result for this company
                gpt_result = eligibility_results.get(str(company_id), False)
                # If company had no valid location, mark as ineligible
                if company.get('location_api_status') != 'success':
                    final_results[company_id] = False
                else:
                    final_results[company_id] = bool(gpt_result)
            
            eligible_count = sum(final_results.values())
            print(f"[GEO ANALYSIS] {eligible_count}/{len(companies_with_locations)} companies eligible")
            
            return final_results
            
        except Exception as e:
            print(f"[GEO ANALYSIS] Error: {e}")
            # Conservative fallback: mark all as ineligible
            return {c['id']: False for c in companies_with_locations}
    
    def _create_analysis_prompt(self, company_data: List[Dict], geo_requirement: str) -> str:
        """
        Create a simplified prompt for GPT-5-mini geographic analysis.
        
        Uses a shorter, more direct format to avoid token limits and ensure
        consistent responses from GPT-5-mini.
        """
        # Create a simpler company list format
        company_list = []
        for company in company_data:
            company_list.append(f"Company {company['company_id']}: {company['address']}")
        
        companies_text = "\n".join(company_list)
        
        return f"""Analyze if companies are in {geo_requirement} region of Portugal.

NUTS II regions: Norte, Centro, Lisboa, Alentejo, Algarve, Açores, Madeira
"Nacional" = anywhere in Portugal

Companies:
{companies_text}

Return JSON only: {{"company_id": true/false, ...}}

JSON:"""


class CompanyScorer:
    """
    Calculates comprehensive company match scores using the Universal Company Match Formula.
    
    Formula: FINAL SCORE = 0.50S + 0.20M + 0.10G + 0.15O′ + 0.05W
    
    Where:
    - S: Semantic Similarity (0-1)
    - M: CAE/Activity Overlap (0-1)
    - G: Geographic Fit (0, 0.5, or 1)
    - O′: Contextual Organizational Fit (0-1)
    - W: Website Presence (0 or 1)
    
    Uses GPT-5-mini to compute the final score based on the formula.
    """
    
    def __init__(self):
        self.client = openai_client
    
    def score_companies(self, companies: List[Dict], incentive: Dict, 
                       semantic_scores: List[float]) -> List[Dict]:
        """
        Score companies using the Universal Company Match Formula.
        
        Args:
            companies: List of company dictionaries with all data
            incentive: Incentive dictionary with context
            semantic_scores: List of semantic similarity scores from reranker
            
        Returns:
            List of companies with added 'company_score' field
        """
        print(f"\n[SCORING] Calculating company scores for {len(companies)} companies...")
        
        # Normalize semantic scores to [0, 1]
        s_scores = self._normalize_scores(semantic_scores)
        
        # Prepare scoring data for each company
        scoring_data = []
        for i, company in enumerate(companies):
            data = {
                'company_id': company['id'],
                's': s_scores[i],
                'm': self._calculate_cae_overlap(company, incentive),
                'g': self._calculate_geographic_fit(company),
                'o': self._calculate_org_capacity(company),
                'org_direction': self._determine_org_direction(incentive),
                'w': 1 if company.get('website') and company['website'] != 'N/A' else 0
            }
            scoring_data.append(data)
        
        # Call GPT-5-mini to compute final scores
        final_scores = self._compute_scores_with_llm(scoring_data)
        
        # Add scores to companies
        for i, company in enumerate(companies):
            company['company_score'] = final_scores.get(company['id'], 0.0)
            company['score_components'] = scoring_data[i]
        
        print(f"[SCORING] Completed scoring for {len(companies)} companies")
        return companies
    
    def _normalize_scores(self, scores: List[float]) -> List[float]:
        """Normalize scores to [0, 1] range."""
        if not scores or len(scores) == 1:
            return [1.0] * len(scores)
        
        min_score = min(scores)
        max_score = max(scores)
        
        if max_score == min_score:
            return [1.0] * len(scores)
        
        return [(s - min_score) / (max_score - min_score) for s in scores]
    
    def _calculate_cae_overlap(self, company: Dict, incentive: Dict) -> float:
        """
        Calculate Jaccard similarity between incentive keywords and company CAE/activities.
        """
        # Extract keywords from incentive
        incentive_text = f"{incentive.get('sector', '')} {incentive.get('eligible_actions', '')}"
        incentive_keywords = set(incentive_text.lower().split())
        
        # Extract keywords from company
        company_text = f"{company.get('cae_label', '')} {company.get('activities', '')}"
        company_keywords = set(company_text.lower().split())
        
        # Remove common stop words
        stop_words = {'de', 'da', 'do', 'e', 'a', 'o', 'para', 'com', 'em', 'por', 'the', 'and', 'or', 'of', 'to', 'in'}
        incentive_keywords -= stop_words
        company_keywords -= stop_words
        
        # Calculate Jaccard similarity
        if not incentive_keywords or not company_keywords:
            return 0.0
        
        intersection = len(incentive_keywords & company_keywords)
        union = len(incentive_keywords | company_keywords)
        
        return intersection / union if union > 0 else 0.0
    
    def _calculate_geographic_fit(self, company: Dict) -> float:
        """
        Calculate geographic fit based on location status.
        """
        # Check if company passed geographic eligibility
        if company.get('geo_eligible'):
            return 1.0
        elif company.get('location_api_status') == 'success':
            return 0.0  # Has location but not eligible
        else:
            return 0.5  # Unknown location
    
    def _calculate_org_capacity(self, company: Dict) -> float:
        """
        Calculate organizational capacity based on legal form.
        """
        name = company.get('name', '').upper()
        
        # Check for different legal forms
        if 'S.A.' in name or 'SA ' in name:
            return 1.00
        elif any(term in name for term in ['COOPERATIVA', 'ASSOCIAÇÃO', 'FUNDAÇÃO', 'MISERICÓRDIA', 'CENTRO SOCIAL']):
            return 1.00
        elif 'SGPS' in name:
            return 0.60
        elif 'UNIPESSOAL' in name:
            return 0.40
        elif 'LDA' in name or 'LTD' in name:
            return 0.70
        else:
            return 0.50  # Unknown
    
    def _determine_org_direction(self, incentive: Dict) -> int:
        """
        Determine organizational direction preference from incentive.
        
        Returns:
            +1: Prefers large/institutional companies
            -1: Prefers small/startups
             0: Prefers social/nonprofit
        """
        # Analyze incentive text for clues
        text = f"{incentive.get('title', '')} {incentive.get('sector', '')} {incentive.get('eligible_actions', '')}".lower()
        
        # Check for social/nonprofit indicators
        social_keywords = ['associação', 'cooperativa', 'social', 'nonprofit', 'terceiro setor', 'ipss']
        if any(keyword in text for keyword in social_keywords):
            return 0
        
        # Check for small business indicators
        small_keywords = ['pme', 'pequena', 'micro', 'startup', 'empreendedor']
        if any(keyword in text for keyword in small_keywords):
            return -1
        
        # Check for large company indicators
        large_keywords = ['grande empresa', 'multinacional', 'corporação', 's.a.']
        if any(keyword in text for keyword in large_keywords):
            return 1
        
        # Default: neutral (slightly favor large companies for institutional incentives)
        if 'administração pública' in text or 'governo' in text:
            return 1
        
        return 0  # Neutral default
    
    def _compute_scores_with_llm(self, scoring_data: List[Dict]) -> Dict[int, float]:
        """
        Use GPT-5-mini to compute final scores using the formula.
        """
        print(f"[SCORING] Computing final scores with GPT-5-mini...")
        
        # Create prompt
        prompt = self._create_scoring_prompt(scoring_data)
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=4000
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            json_start = result_text.find('{')
            json_end = result_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = result_text[json_start:json_end]
                scores = json.loads(json_text)
                
                # Convert string keys to integers
                return {int(k): float(v) for k, v in scores.items()}
            else:
                print(f"[SCORING] No JSON found in response")
                return {}
                
        except Exception as e:
            print(f"[SCORING] Error computing scores: {e}")
            return {}
    
    def _create_scoring_prompt(self, scoring_data: List[Dict]) -> str:
        """
        Create prompt for GPT-5-mini to compute scores.
        """
        companies_json = json.dumps(scoring_data, indent=2)
        
        return f"""Calculate final company match scores using this formula:

FINAL SCORE = 0.50*S + 0.20*M + 0.10*G + 0.15*O' + 0.05*W

Where O' (contextual org fit) is calculated as:
- If org_direction = +1: O' = O
- If org_direction = -1: O' = 1 - O  
- If org_direction = 0: O' = 1 if O >= 0.9, else 0.5

Input data:
{companies_json}

Return JSON only with company_id as key and final_score as value:
{{"company_id": final_score, ...}}

JSON:"""


# Import existing functions from test_incentive_matching.py
def get_random_incentive():
    """Get a random incentive for testing."""
    print("\n[DB] Fetching random incentive...")
    
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT incentive_id, title, sector, geo_requirement, 
               eligible_actions, funding_rate, investment_eur
        FROM incentives
        WHERE sector IS NOT NULL AND eligible_actions IS NOT NULL 
        AND geo_requirement IS NOT NULL
        ORDER BY RANDOM() LIMIT 1
    """)
    
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if not result:
        print("[ERROR] No processed incentives found!")
        return None
    
    incentive = {
        'id': result[0], 'title': result[1], 'sector': result[2],
        'geo_requirement': result[3], 'eligible_actions': result[4],
        'funding_rate': result[5], 'investment_eur': result[6]
    }

    print(f"\n[OK] SELECTED INCENTIVE:")
    print(f"=" * 80)
    print(f"ID: {incentive['id']}")
    print(f"Title: {incentive['title']}")
    print(f"Sector: {incentive['sector']}")
    print(f"Geographic Requirement: {incentive['geo_requirement']}")
    print(f"Eligible Actions: {incentive['eligible_actions']}")
    print(f"=" * 80)
    return incentive


def create_search_query(incentive):
    """
    Create search query from incentive data.
    
    Combines sector, ai_description, and eligible_actions to match
    the semantic richness of company embeddings (name + CAE + description).
    
    This SOTA-backed approach uses full descriptions rather than just keywords,
    providing better semantic matching between incentives and companies.
    """
    # Build query with all semantic information
    query_parts = []
    
    if incentive.get('sector'):
        query_parts.append(incentive['sector'])
    
    if incentive.get('ai_description'):
        query_parts.append(incentive['ai_description'])
    
    if incentive.get('eligible_actions'):
        query_parts.append(incentive['eligible_actions'])
    
    query = " ".join(query_parts)
    
    print(f"\n[QUERY] Search query components:")
    print(f"  - Sector: {incentive.get('sector', 'N/A')}")
    print(f"  - AI Description: {incentive.get('ai_description', 'N/A')[:100]}...")
    print(f"  - Eligible Actions: {incentive.get('eligible_actions', 'N/A')[:100]}...")
    print(f"  - Total query length: {len(query)} characters")
    
    return [query]


def load_embedding_model():
    """Load the embedding model."""
    print("\n[MODEL] Loading embedding model...")
    try:
        model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', device=device)
        print("[OK] Multilingual model loaded")
        return model
    except:
        model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
        print("[OK] Fallback model loaded")
        return model


def load_reranker():
    """Load the reranker model."""
    print("\n[RERANKER] Loading BGE Reranker v2-m3...")
    try:
        reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
        print("[OK] BGE Reranker v2-m3 loaded successfully")
        return reranker
    except Exception as e:
        print(f"[ERROR] Failed to load reranker: {e}")
        return None


def search_companies_qdrant(queries, model, top_k=20):
    """Search for companies using vector similarity."""
    print(f"\n[QDRANT] Searching for top {top_k} companies...")

    client = QdrantClient(path="./qdrant_storage")
    collection_name = "companies"

    try:
        collection_info = client.get_collection(collection_name)
        print(f"[OK] Connected: {collection_info.points_count:,} companies")
    except Exception as e:
        print(f"[ERROR] Qdrant collection not found: {e}")
        return []

    # Since we only have one query, just use cosine similarity directly
    query = queries[0]  # Take the first (and only) query
    print(f"[SEARCHING] Query: {query}")
    
    query_vector = model.encode(query).tolist()

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k
    ).points

    # Convert to our expected format, keeping the original cosine scores
    companies = []
    for result in results:
        companies.append({
            'id': result.id,
            'score': result.score,  # Use actual cosine similarity score
            'payload': result.payload
        })

    print(f"[OK] Found {len(companies)} companies using cosine similarity")
    return companies


def enrich_with_postgres(company_ids):
    """Fetch full company details from PostgreSQL."""
    print(f"\n[DB] Enriching {len(company_ids)} companies...")

    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
        host=DB_HOST, port=DB_PORT
    )
    cursor = conn.cursor()

    cursor.execute("""
        SELECT company_id, company_name, cae_primary_label,
               trade_description_native, website
        FROM companies WHERE company_id = ANY(%s)
    """, (company_ids,))

    companies = {}
    for row in cursor.fetchall():
        companies[row[0]] = {
            'id': row[0], 'name': row[1], 'cae': row[2],
            'activities': row[3], 'website': row[4]
        }

    cursor.close()
    conn.close()

    print(f"[OK] Enriched {len(companies)} companies")
    return companies


def rerank_companies(query, companies, reranker, top_k=None):
    """Rerank companies using BGE Reranker v2-m3."""
    if top_k is None:
        top_k = len(companies)
    
    print(f"\n[RERANKING] Reranking {len(companies)} companies...")

    if not reranker:
        print("[WARNING] Reranker not available, returning original order")
        return companies[:top_k]

    # Prepare query-document pairs for reranking
    pairs = []
    for company in companies:
        company_text = f"{company['name']} {company['cae'] or ''} {company['activities'] or ''}"
        pairs.append([query, company_text])

    # Get reranking scores
    scores = reranker.compute_score(pairs, normalize=True)

    # Add scores to companies and sort
    for i, company in enumerate(companies):
        company['rerank_score'] = scores[i] if isinstance(scores, list) else scores

    # Sort by rerank score and get top_k
    reranked = sorted(companies, key=lambda x: x['rerank_score'], reverse=True)[:top_k]

    print(f"[OK] Reranking complete! Top {len(reranked)} companies selected")
    return reranked


class EnhancedMatchingPipeline:
    """
    Orchestrates the complete enhanced matching pipeline.
    
    Manages the iterative search process, coordinates all services,
    and handles the complex logic of expanding search when needed.
    
    The pipeline implements the following algorithm:
    1. Start with 20 candidates from semantic search
    2. Enrich all candidates with locations
    3. Filter by geographic eligibility
    4. If ≤5 eligible companies, return them (or expand to 30 if <5)
    5. If >5 eligible companies, return top 5 by semantic score
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.location_service = LocationService(self.db_manager)
        self.geo_analyzer = GeographicAnalyzer()
        self.company_scorer = CompanyScorer()
        
        # Load models
        self.embedding_model = load_embedding_model()
        self.reranker = load_reranker()
        
        # Ensure database schema
        self.db_manager.ensure_schema()
    
    def find_matching_companies(self, incentive: Dict, max_candidates: int = 50) -> MatchingResult:
        """
        Find companies that match both semantic and geographic criteria.
        
        Implements the iterative search algorithm with automatic expansion
        when insufficient eligible companies are found.
        
        Args:
            incentive: Incentive data including geo_requirement
            max_candidates: Maximum number of candidates to search
            
        Returns:
            MatchingResult with final matched companies and metadata
        """
        start_time = time.time()
        print(f"\n{'='*80}")
        print(f"ENHANCED MATCHING PIPELINE")
        print(f"Incentive: {incentive['title']}")
        print(f"Geographic Requirement: {incentive['geo_requirement']}")
        print(f"{'='*80}")
        
        # Create search query
        queries = create_search_query(incentive)
        query = queries[0]
        
        # Start with 10 candidates, then increment by 10 up to max_candidates
        candidates_to_try = 10
        
        while candidates_to_try <= max_candidates:
            print(f"\n[PIPELINE] Searching with {candidates_to_try} candidates...")
            
            # Stage 1: Semantic search and ranking
            vector_results = search_companies_qdrant(queries, self.embedding_model, top_k=candidates_to_try)
            
            if not vector_results:
                print("[ERROR] No vector search results found")
                break
            
            # Enrich with PostgreSQL data
            company_ids = [r['id'] for r in vector_results]
            company_details = enrich_with_postgres(company_ids)
            
            # Combine vector results with company details
            companies_for_reranking = []
            for result in vector_results:
                if result['id'] in company_details:
                    company = company_details[result['id']]
                    company['fusion_score'] = result['score']
                    companies_for_reranking.append(company)
            
            # Stage 2: Semantic reranking
            reranked_companies = rerank_companies(query, companies_for_reranking, self.reranker)
            
            # Stage 3: Location enrichment
            companies_with_locations = self._enrich_with_locations(reranked_companies)
            
            # Stage 4: Geographic filtering
            eligibility_results = self.geo_analyzer.analyze_eligibility(
                companies_with_locations, incentive['geo_requirement']
            )
            
            # Filter to only eligible companies
            eligible_companies = [
                company for company in companies_with_locations
                if eligibility_results.get(company['id'], False)
            ]
            
            eligible_count = len(eligible_companies)
            print(f"\n[PIPELINE] {eligible_count} companies meet geographic requirements")
            
            # Decision logic
            if eligible_count >= 5:
                # We have 5 or more eligible companies, take top 5 by rerank score
                final_companies = sorted(
                    eligible_companies, 
                    key=lambda x: x['rerank_score'], 
                    reverse=True
                )[:5]
                break
            elif candidates_to_try >= max_candidates:
                # We've reached the maximum, return what we have (even if < 5)
                final_companies = eligible_companies
                break
            else:
                # Too few eligible companies, expand search by 10
                print(f"[PIPELINE] Only {eligible_count} eligible companies found, expanding by 10...")
                candidates_to_try += 10
                continue
        
        # Stage 5: Calculate company scores using Universal Formula
        print(f"\n[PIPELINE] Calculating comprehensive company scores...")
        
        # Get semantic scores for scoring
        semantic_scores = [c['rerank_score'] for c in final_companies]
        
        # Add geo_eligible flag for scoring
        for company in final_companies:
            company['geo_eligible'] = True  # All final companies are geo-eligible
        
        # Score companies
        scored_companies = self.company_scorer.score_companies(final_companies, incentive, semantic_scores)
        
        # Sort by company_score for the scored results
        scored_companies_sorted = sorted(
            scored_companies,
            key=lambda x: x.get('company_score', 0),
            reverse=True
        )
        
        # Create result object (with original semantic ranking)
        processing_time = time.time() - start_time
        result = MatchingResult(
            incentive_id=incentive['id'],
            companies=final_companies,  # Keep original semantic ranking
            total_candidates_searched=candidates_to_try,
            geographic_eligible_count=len(final_companies),
            processing_time=processing_time,
            created_at=datetime.now()
        )
        
        # Save both results to database
        self.db_manager.save_matching_results(result)
        self.db_manager.save_scored_results(incentive['id'], scored_companies_sorted, processing_time)
        
        print(f"\n[PIPELINE] Matching completed in {processing_time:.2f} seconds")
        print(f"[PIPELINE] Final result: {len(final_companies)} companies")
        
        return result
    
    def _enrich_with_locations(self, companies: List[Dict]) -> List[Dict]:
        """
        Enrich companies with location data using caching.
        
        For each company, attempts to get location from cache or API.
        Updates company dict with location fields for downstream processing.
        """
        print(f"\n[LOCATION] Enriching {len(companies)} companies with location data...")
        
        enriched_companies = []
        
        for company in companies:
            # Get location (from cache or API)
            location = self.location_service.get_company_location(
                company['id'], 
                company['name'],
                existing_address=None  # Could use website or other info
            )
            
            # Add location data to company dict
            company_with_location = company.copy()
            company_with_location.update({
                'location_lat': location.latitude,
                'location_lon': location.longitude,
                'location_address': location.formatted_address,
                'formatted_address': location.formatted_address,  # For compatibility
                'location_api_status': location.api_status,
                'location_updated_at': location.updated_at
            })
            
            enriched_companies.append(company_with_location)
        
        successful_locations = sum(1 for c in enriched_companies if c['location_api_status'] == 'success')
        print(f"[LOCATION] {successful_locations}/{len(companies)} companies have valid locations")
        
        return enriched_companies
    
    def display_results(self, result: MatchingResult):
        """Display the final matching results."""
        print(f"\n{'='*80}")
        print(f"FINAL RESULTS: {len(result.companies)} COMPANIES")
        print(f"Total candidates searched: {result.total_candidates_searched}")
        print(f"Processing time: {result.processing_time:.2f} seconds")
        print(f"{'='*80}")

        for idx, company in enumerate(result.companies, 1):
            print(f"\n{'='*80}")
            print(f"COMPANY #{idx}")
            print(f"{'='*80}")
            print(f"Name: {company['name']}")
            print(f"Semantic Score: {company.get('rerank_score', 0):.4f}")
            print(f"Location: {company.get('formatted_address', 'N/A')}")
            print(f"CAE Classification: {company.get('cae', 'N/A')}")
            print(f"Website: {company.get('website', 'N/A')}")
            if company.get('activities'):
                activities = company['activities'][:200] + "..." if len(company['activities']) > 200 else company['activities']
                print(f"Activities: {activities}")


def main():
    """
    Main function to test the enhanced matching pipeline.
    
    Demonstrates the complete flow from incentive selection to final results
    with geographic filtering and iterative search logic.
    """
    print("=" * 80)
    print("ENHANCED INCENTIVE-COMPANY MATCHING")
    print("Semantic Search + Geographic Filtering + Iterative Logic")
    print("=" * 80)

    # Get a random incentive
    incentive = get_random_incentive()
    if not incentive:
        return

    # Initialize and run the enhanced pipeline
    pipeline = EnhancedMatchingPipeline()
    result = pipeline.find_matching_companies(incentive)
    
    # Display results
    pipeline.display_results(result)
    
    print(f"\n{'='*80}")
    print("[SUCCESS] Enhanced matching completed!")
    print(f"Results saved to database for incentive {incentive['id']}")
    print("=" * 80)


if __name__ == "__main__":
    main()