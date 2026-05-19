""" DEI Language Auditor Tool """

import re
import asyncio
from agents.JD_Arcitecture_agent.tools.Bias_Guardian_agent import BiasGuardianAgent


class DEILanguage:
    """Tool to audit job descriptions for DEI (Diversity, Equity, Inclusion) language."""
    def __init__(self):
        """
        Initialize DEI Language Auditor.
        
        Args:
            escalation_handler: Optional callable to handle escalation when bias_score exceeds threshold.
                               Should accept (job_description, bias_score, flagged_terms, suggestions)
        """
        self.escalation_handler = BiasGuardianAgent().handle_escalation
        self.flagged_terms = {
            'aggressive': "assertive" ,
            'ninja': "expert",
            'rockstar': "highly skilled",
            'guru': "expert",
            'manpower': "workforce",
            'salesman': "salesperson",
            'chairman': "chairperson",
            'mankind': "humankind",
            'guys': "everyone" ,
            'he': "they",
            'she': "they",
            'him': "them",
            'her': "them",
            'his': "their",
            'hers': "their",
            "strong": "proficient / dependable",
            "dominant": "leading / market-established",
            "supportive": "collaborative",
            "understanding": "empathetic / inclusive",
            "nurturing": "supportive / developmental",
            "waiter" : "server", 
            "waitress": "server",
            "actor": "performer", "actress": "performer",
            "salesman": "salesperson", "saleswoman": "salesperson",
            "policeman": "police officer", "policewoman": "police officer",

        }
        
    async def _arunc(self, job_description: str, threshold: float) -> dict:
        """Asynchronous method to evaluate the job description for DEI language."""
        return await self.evaluate_jd(job_description, threshold)
    
    async def evaluate_jd(self, job_description: str, threshold: float) -> dict:
        """Evaluate the job description for DEI language and return a report."""
        # Run CPU-bound work in a thread pool to avoid blocking the event loop
        return await asyncio.to_thread(self._evaluate_jd_sync, job_description, threshold)
    
    def _evaluate_jd_sync(self, job_description: str, threshold: float) -> dict:
        """Synchronous helper method that performs the actual DEI language evaluation."""
        words = re.findall(r'\b\w+\b', job_description.lower())
        total_words = len(words) if len(words) > 0 else 1  # Avoid division by zero

        flagged_words = []
        replacement_suggestions = []
        match_count = 0
        for word in words:
            if word in self.flagged_terms:
                flagged_words.append(word)
                replacement_suggestions.append(self.flagged_terms[word])
                match_count += 1
        
        density_ratio = match_count / total_words
        bias_score = density_ratio * 100 

        result = {
                "flagged_words": flagged_words,
                "replacement_suggestions": replacement_suggestions,
                "bias_score": bias_score,
                "recommendation": "The job description is relatively inclusive, but consider reviewing the flagged terms for improvement.",
                "escalated": False,
                "escalation_details": None
            }
        
        if bias_score >= threshold:
            result["recommendation"] = "Revise the job description to use more inclusive language."
            
            if self.escalation_handler:
                result["escalated"] = True
                result["escalation_details"] = self.escalation_handler(
                    job_description=job_description,
                    bias_score=bias_score,
                    threshold=threshold,
                    flagged_words=flagged_words,
                    replacement_suggestions=replacement_suggestions
                )
                
        return result