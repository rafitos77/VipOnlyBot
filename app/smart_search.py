"""
Smart Search Module
Implements fuzzy matching for model names
"""

import logging
from typing import List, Dict, Any
from rapidfuzz import process, fuzz

logger = logging.getLogger(__name__)

class SmartSearch:
    """Handles fuzzy searching for creators"""
    
    @staticmethod
    def find_similar(query: str, creators: List[Dict[str, Any]], limit: int = 8, threshold: float = 60.0) -> List[Dict[str, Any]]:
        """
        Find creators with names similar to the query
        
        Args:
            query: User search term
            creators: List of creator dicts from API
            limit: Max results to return
            threshold: Minimum similarity score (0-100)
            
        Returns:
            List of matching creator dicts
        """
        if not creators:
            return []
            
        # Extract names for matching
        names = [c.get('name', '') for c in creators]
        
        # Use RapidFuzz to find best matches
        # token_sort_ratio is good for "belle delphine" vs "delphine belle"
        matches = process.extract(
            query, 
            names, 
            scorer=fuzz.token_sort_ratio, 
            limit=limit,
            score_cutoff=threshold
        )
        
        results = []
        for name, score, index in matches:
            creator = creators[index].copy()
            creator['match_score'] = score
            results.append(creator)
            
        return results

# Global instance
smart_search = SmartSearch()
