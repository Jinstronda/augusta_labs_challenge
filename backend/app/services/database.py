"""
Database service for accessing incentives and companies data

Provides methods to fetch incentives with their matched companies and
companies with their eligible incentives from PostgreSQL.
"""

import json
import psycopg2
from psycopg2 import pool
from typing import Optional, Dict, List, Any
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class DatabaseService:
    """
    Service for database operations with connection pooling.
    
    Uses psycopg2 connection pool for efficient connection management.
    """
    
    def __init__(self):
        """Initialize database connection pool"""
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                minconn=1,
                maxconn=10,
                dbname=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                host=settings.DB_HOST,
                port=settings.DB_PORT
            )
            logger.info("Database connection pool initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise
    
    def get_connection(self):
        """Get a connection from the pool"""
        return self.connection_pool.getconn()
    
    def return_connection(self, conn):
        """Return a connection to the pool"""
        self.connection_pool.putconn(conn)
    
    def get_incentive_with_companies(self, incentive_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch an incentive with its top 5 matched companies.
        
        Retrieves incentive metadata and parses the top_5_companies_scored JSON
        to get the matched companies with their scores and ranks.
        
        Args:
            incentive_id: The incentive ID to fetch
            
        Returns:
            Dict with incentive data and matched companies, or None if not found
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Fetch incentive with scored companies
            cursor.execute("""
                SELECT 
                    i.incentive_id,
                    i.title,
                    i.description,
                    i.ai_description,
                    i.eligibility_criteria,
                    i.sector,
                    i.geo_requirement,
                    i.eligible_actions,
                    i.funding_rate,
                    i.investment_eur,
                    i.start_date,
                    i.end_date,
                    i.total_budget,
                    i.source_link,
                    i.top_5_companies_scored
                FROM incentives i
                WHERE i.incentive_id = %s
            """, (incentive_id,))
            
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Incentive {incentive_id} not found")
                return None
            
            # Parse result
            (
                inc_id, title, description, ai_description, eligibility_criteria,
                sector, geo_requirement, eligible_actions, funding_rate, investment_eur,
                start_date, end_date, total_budget, source_link, scored_json
            ) = result
            
            # Parse top_5_companies_scored JSON
            companies = []
            if scored_json:
                try:
                    scored_data = json.loads(scored_json) if isinstance(scored_json, str) else scored_json
                    companies_data = scored_data.get('companies', [])
                    
                    # Fetch full company details for each matched company
                    for company_data in companies_data:
                        company_id = company_data.get('id')
                        
                        if company_id:
                            cursor.execute("""
                                SELECT 
                                    company_id,
                                    company_name,
                                    cae_primary_label,
                                    trade_description_native,
                                    website,
                                    location_address
                                FROM companies
                                WHERE company_id = %s
                            """, (company_id,))
                            
                            company_row = cursor.fetchone()
                            
                            if company_row:
                                companies.append({
                                    'id': company_row[0],
                                    'name': company_row[1],
                                    'cae_classification': company_row[2],
                                    'activities': company_row[3],
                                    'website': company_row[4],
                                    'location_address': company_row[5],
                                    'rank': company_data.get('rank'),
                                    'company_score': company_data.get('company_score'),
                                    'semantic_score': company_data.get('semantic_score'),
                                    'score_components': company_data.get('score_components', {})
                                })
                
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing top_5_companies_scored JSON: {e}")
            
            # Build response
            incentive_data = {
                'incentive_id': inc_id,
                'title': title,
                'description': description,
                'ai_description': ai_description,
                'eligibility_criteria': eligibility_criteria,
                'sector': sector,
                'geo_requirement': geo_requirement,
                'eligible_actions': eligible_actions,
                'funding_rate': funding_rate,
                'investment_eur': investment_eur,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'total_budget': float(total_budget) if total_budget else None,
                'source_link': source_link,
                'matched_companies': companies
            }
            
            logger.info(f"Fetched incentive {incentive_id} with {len(companies)} companies")
            return incentive_data
            
        except Exception as e:
            logger.error(f"Error fetching incentive {incentive_id}: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                self.return_connection(conn)
    
    def get_company_with_incentives(self, company_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch a company with its eligible incentives.
        
        Retrieves company metadata and parses the eligible_incentives JSON
        to get the matched incentives with their scores and ranks.
        
        Args:
            company_id: The company ID to fetch
            
        Returns:
            Dict with company data and eligible incentives, or None if not found
        """
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Fetch company with eligible incentives
            cursor.execute("""
                SELECT 
                    c.company_id,
                    c.company_name,
                    c.cae_primary_label,
                    c.trade_description_native,
                    c.website,
                    c.location_address,
                    c.location_lat,
                    c.location_lon,
                    c.eligible_incentives
                FROM companies c
                WHERE c.company_id = %s
            """, (company_id,))
            
            result = cursor.fetchone()
            
            if not result:
                logger.warning(f"Company {company_id} not found")
                return None
            
            # Parse result
            (
                comp_id, company_name, cae_label, activities, website,
                location_address, location_lat, location_lon, incentives_json
            ) = result
            
            # Parse eligible_incentives JSON
            incentives = []
            if incentives_json:
                try:
                    incentives_data = json.loads(incentives_json) if isinstance(incentives_json, str) else incentives_json
                    
                    # Fetch full incentive details for each eligible incentive
                    for incentive_data in incentives_data:
                        incentive_id = incentive_data.get('incentive_id')
                        
                        if incentive_id:
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
                                    start_date,
                                    end_date,
                                    source_link
                                FROM incentives
                                WHERE incentive_id = %s
                            """, (incentive_id,))
                            
                            incentive_row = cursor.fetchone()
                            
                            if incentive_row:
                                incentives.append({
                                    'incentive_id': incentive_row[0],
                                    'title': incentive_row[1],
                                    'description': incentive_row[2],
                                    'ai_description': incentive_row[3],
                                    'sector': incentive_row[4],
                                    'geo_requirement': incentive_row[5],
                                    'eligible_actions': incentive_row[6],
                                    'funding_rate': incentive_row[7],
                                    'start_date': incentive_row[8].isoformat() if incentive_row[8] else None,
                                    'end_date': incentive_row[9].isoformat() if incentive_row[9] else None,
                                    'source_link': incentive_row[10],
                                    'rank': incentive_data.get('rank'),
                                    'company_score': incentive_data.get('company_score')
                                })
                
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing eligible_incentives JSON: {e}")
            
            # Build response
            company_data = {
                'company_id': comp_id,
                'company_name': company_name,
                'cae_classification': cae_label,
                'activities': activities,
                'website': website,
                'location_address': location_address,
                'location_lat': float(location_lat) if location_lat else None,
                'location_lon': float(location_lon) if location_lon else None,
                'eligible_incentives': incentives
            }
            
            logger.info(f"Fetched company {company_id} with {len(incentives)} incentives")
            return company_data
            
        except Exception as e:
            logger.error(f"Error fetching company {company_id}: {e}")
            raise
        finally:
            if conn:
                cursor.close()
                self.return_connection(conn)
    
    def close(self):
        """Close all connections in the pool"""
        if self.connection_pool:
            self.connection_pool.closeall()
            logger.info("Database connection pool closed")
