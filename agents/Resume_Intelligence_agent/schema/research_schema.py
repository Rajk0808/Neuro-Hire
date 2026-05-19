from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class SalaryBenchMarkerArgs(BaseModel):
    """Input schema for salary benchmarking tool."""
    role : str = Field(..., description="The job title or role for which to benchmark the salary.")
    specialization : Optional[str] = Field(None, description="The specialization or field within the role, if applicable.")
    location : Optional[str] = Field(None, description="The geographic location for which to benchmark the salary.")
    experience_years : Optional[str] = Field(None, description="The number of years of experience for which to benchmark the salary.")
    percentile_range : Optional[List[int]] = Field([25,50,75,100], description="The percentile range for which to benchmark the salary (e.g., 25th, 50th, 75th).")

class SalaryBenchMarkerOutput(BaseModel):   
    '''Output schema for salary benchmarking results.'''
    min_salary: float
    max_salary: float
    median_salary: float
    min_base_salary: float
    max_base_salary: float
    median_base_salary: float
    market_note: Optional[str] | None  = Field(None, description="Additional notes about the salary market for the specified role and location.")
    competing_titles: Optional[List[str]] | None = Field(None, description="List of competing job titles that are similar to the specified role and may have similar salary ranges.")

class SkillExtractorArgs(BaseModel):
    '''Input schema for skill extraction tool.'''
    role: str = Field('', description="The job title or role for which to extract skills.")
    domain: str = Field('', description="The domain or industry related to the job role.")
    source: str = Field('', description="The source text from which to extract skills.")

class SkillExtractorOutput(BaseModel):
    '''Output schema for skill extraction results.'''
    must_have_skills : List[str] = Field(..., description="List of must-have skills extracted from the source text.")
    good_to_have_skills : List[str] = Field(..., description="List of good-to-have skills extracted from the source text.")
    anti_pattern_skills : List[str] = Field(..., description="List of anti-pattern skills that are not relevant or desirable for the specified role and domain.")
    emerging_skills : List[str] = Field(..., description="List of emerging skills that are gaining traction in the industry and may be relevant for the specified role and domain.")

class CompetitorJDAnalysisArgs(BaseModel):
    '''Input schema for competitor JD analysis tool.'''
    role: str = Field('', description="The job title or role for which to analyze competitor JDs.")
    seniority_level: str = Field('', description="The seniority level (e.g., Junior, Mid, Senior) for which to analyze competitor JDs.")

class CompetitorJDAnalysisOutput(BaseModel):
    '''Returns structural patterns (sections used, language style, differentiators), and gaps in competitor JDs that can be exploited.'''
    companies_analyzed : int
    individual_analyses: Dict[str, Dict]
    structural_patterns: Dict[str, List[str]]
    identified_gaps: List[str]
    competitive_opportunities: List[str]
    generated_parser_code: str
    timestamp : str
    