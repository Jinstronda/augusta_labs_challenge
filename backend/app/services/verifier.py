"""
Incentive Verification Service using Gemini 2.5 Flash

Verifies that incentives returned by semantic search actually match the user's criteria.
Acts as a quality filter to remove false positives from vector search.

Example:
- Query: "incentives in Algarve"
- Semantic search returns 5 incentives
- Verifier checks each one: Does it actually require/target Algarve?
- Filters out incentives that don't match
"""

import json
import logging
from typing import List, Dict, Any
from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)


class IncentiveVerifier:
    """
    Verifies incentive matches using Gemini 2.5 Flash.
    
    Uses LLM to check if an incentive actually matches the user's query criteria.
    This catches semantic search false positives.
    """
    
    def __init__(self):
        """Initialize Gemini client"""
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
    
    def verify_incentives(self, query: str, incentives: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Verify that incentives match the query criteria.
        
        Args:
            query: User's original query (e.g., "green energy incentives in Algarve")
            incentives: List of incentive matches from semantic search
            
        Returns:
            Filtered list of incentives that actually match
        """
        if not incentives:
            return []
        
        logger.info(f"🔍 AI Verification: Checking {len(incentives)} incentives for query: '{query}'")
        
        verified = []
        rejected = []
        
        for idx, incentive in enumerate(incentives, 1):
            title = incentive.get('title', 'N/A')
            try:
                is_match, reason = self._verify_single_incentive(query, incentive)
                
                if is_match:
                    verified.append(incentive)
                    logger.info(f"  [{idx}/{len(incentives)}] ✓ PASS: {title[:60]}")
                    logger.debug(f"    Reason: {reason}")
                else:
                    rejected.append({'title': title, 'reason': reason})
                    logger.info(f"  [{idx}/{len(incentives)}] ✗ FAIL: {title[:60]}")
                    logger.debug(f"    Reason: {reason}")
                    
            except Exception as e:
                logger.warning(f"  [{idx}/{len(incentives)}] ⚠ ERROR: {title[:60]} - {e}")
                # If verification fails, keep the incentive (fail-safe)
                verified.append(incentive)
        
        logger.info(f"✅ Verification complete: {len(verified)}/{len(incentives)} passed ({len(rejected)} filtered out)")
        
        if rejected:
            logger.debug(f"Rejected incentives: {[r['title'][:40] for r in rejected]}")
        
        return verified
    
    def _verify_single_incentive(self, query: str, incentive: Dict[str, Any]) -> tuple[bool, str]:
        """
        Verify a single incentive matches the query criteria.
        
        Args:
            query: User's query
            incentive: Incentive data dict
            
        Returns:
            Tuple of (matches: bool, reason: str)
        """
        prompt = self._create_verification_prompt(query, incentive)
        
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
            
            if not response or not response.text:
                logger.warning("Empty response from Gemini verifier")
                return True, "Verification failed - kept as fail-safe"
            
            result_text = response.text.strip()
            result_data = json.loads(result_text)
            
            # Get match decision
            matches = result_data.get('matches', True)  # Default to True if unclear
            reason = result_data.get('reason', 'No reason provided')
            
            return matches, reason
            
        except Exception as e:
            logger.error(f"Verification error: {e}")
            return True, f"Verification error: {str(e)}"  # Fail-safe: keep incentive if verification fails
    
    def _create_verification_prompt(self, query: str, incentive: Dict[str, Any]) -> str:
        """
        Create prompt for Gemini to verify incentive match.
        
        Args:
            query: User's query
            incentive: Incentive data
            
        Returns:
            Verification prompt
        """
        title = incentive.get('title', 'N/A')
        ai_desc = incentive.get('ai_description', 'N/A')
        sector = incentive.get('sector', 'N/A')
        geo = incentive.get('geo_requirement', 'N/A')
        actions = incentive.get('eligible_actions', 'N/A')
        
        return f"""Verify if this incentive matches the user's query criteria.

User Query: "{query}"

Incentive Details:
- Title: {title}
- Description: {ai_desc}
- Sector: {sector}
- Geographic Requirement: {geo}
- Eligible Actions: {actions}

Does this incentive actually match what the user is looking for?

Consider:
1. Geographic match - If user specifies location (e.g., "Algarve"), does the incentive target that location?
2. Sector match - If user specifies sector (e.g., "green energy"), is the incentive for that sector?
3. Type match - If user specifies type (e.g., "R&D"), does the incentive support that?
4. General relevance - Does the incentive align with the user's intent?

Rules:
- If query mentions a location, incentive MUST match that location (or be national/no restriction)
- If query mentions a sector, incentive MUST be relevant to that sector
- If query is general (e.g., "funding programs"), be more lenient
- When in doubt, return true (better to show than hide)

Return JSON: {{"matches": true, "reason": "explanation"}} or {{"matches": false, "reason": "explanation"}}

JSON:"""
    
    def batch_verify_incentives(self, query: str, incentives: List[Dict[str, Any]], 
                                batch_size: int = 5) -> List[Dict[str, Any]]:
        """
        Verify incentives in batches for better performance.
        
        For now, processes one at a time. Can be optimized later with parallel calls.
        
        Args:
            query: User's query
            incentives: List of incentives to verify
            batch_size: Number to process at once (future optimization)
            
        Returns:
            Filtered list of verified incentives
        """
        return self.verify_incentives(query, incentives)
