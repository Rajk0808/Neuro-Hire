""" DEI Language Auditor Tool """

import re
import asyncio
from typing import Type
from pydantic import ConfigDict
from apps.backend.app.agents.JD_Arcitecture_agent.tools.Bias_Guardian_agent import BiasGuardianAgent
from crewai.tools import BaseTool
from pydantic import BaseModel
from apps.backend.app.agents.JD_Arcitecture_agent.schema.research_schema import DEILanguageArgs, DEILanguageOutput

class DEILanguageTool(BaseTool):
    """Tool to audit job descriptions for DEI (Diversity, Equity, Inclusion) language."""
    name: str = 'dei_language_auditor'
    description: str = ("use this tool to audit job descriptions for DEI (Diversity, Equity, Inclusion) language. "
                   "It identifies potentially biased terms, calculates a bias score based on the density of such terms, "
                   "and provides suggestions for more inclusive alternatives. If the bias score exceeds a specified threshold, "
                   "it can trigger an escalation to the Bias Guardian Agent for further review and action.")
    args_schema: Type[DEILanguageArgs] = DEILanguageArgs
    output_schema: Type[DEILanguageOutput] = DEILanguageOutput
    
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')

    def __init__(self):
        """
        Initialize DEI Language Auditor.
        
        Args:
            escalation_handler: Optional callable to handle escalation when bias_score exceeds threshold.
                               Should accept (job_description, bias_score, flagged_terms, suggestions)
        """
        super().__init__()
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
    
    def _run(self, job_description: str, threshold: float = 5.0) -> DEILanguageOutput:
        """Synchronous wrapper for CrewAI compatibility."""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(self._arunc(DEILanguageArgs(job_description=job_description, threshold=threshold)))
        return result
        
    async def _arunc(self, args : DEILanguageArgs) -> DEILanguageOutput:
        """Asynchronous method to evaluate the job description for DEI language."""
        result = await self.evaluate_jd(args.job_description, args.threshold)
        return DEILanguageOutput(**result)
    
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