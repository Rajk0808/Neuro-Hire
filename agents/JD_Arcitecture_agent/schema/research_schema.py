from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional, Union

class SalaryBenchMarkerArgs(BaseModel):
    """Input schema for salary benchmarking tool."""
    role : str = Field(..., description="The job title or role for which to benchmark the salary.")
    specialization : Optional[str] = Field(None, description="The specialization or field within the role, if applicable.")
    location : Optional[str] = Field(None, description="The geographic location for which to benchmark the salary.")
    experience_years : Optional[str] = Field(None, description="The number of years of experience for which to benchmark the salary.")
    percentile_range : Optional[List[int]] = Field(default=[25,50,75,100], description="The percentile range for which to benchmark the salary (e.g., 25th, 50th, 75th).")

class SalaryBenchMarkerOutput(BaseModel):   
    '''Output schema for salary benchmarking results.'''
    min_salary: float
    max_salary: float
    median_salary: float
    min_base_salary: float
    max_base_salary: float
    median_base_salary: float
    market_note: Optional[str] = Field(None, description="Additional notes about the salary market for the specified role and location.")
    competing_titles: Optional[List[str]] = Field(None, description="List of competing job titles that are similar to the specified role and may have similar salary ranges.")

class SkillExtractorArgs(BaseModel):
    '''Input schema for skill extraction tool.'''
    role: str = Field(..., description="The job title or role for which to extract skills.")
    domain: str = Field(..., description="The domain or industry related to the job role.")
    source: str = Field(..., description="The source text from which to extract skills.")

class SkillExtractorOutput(BaseModel):
    '''Output schema for skill extraction results.'''
    must_have_skills : Union[List[str], dict] = Field(..., description="List of must-have skills extracted from the source text.")
    good_to_have_skills : Union[List[str], dict] = Field(..., description="List of good-to-have skills extracted from the source text.")
    anti_pattern_skills : Union[List[str], dict] = Field(..., description="List of anti-pattern skills that are not relevant or desirable for the specified role and domain.")
    emerging_skills : Union[List[str], dict] = Field(..., description="List of emerging skills that are gaining traction in the industry and may be relevant for the specified role and domain.")
    github_skills : Union[List[str], dict] = Field(..., description="List of skills extracted from relevant GitHub repositories that are associated with the specified role and domain.")

class CompetitorJDAnalysisArgs(BaseModel):
    '''Input schema for competitor JD analysis tool.'''
    companies: List[str] = Field(..., description="List of competitor companies for which to analyze job descriptions.")
    role: str = Field(..., description="The job title or role for which to analyze competitor JDs.")
    seniority: str = Field(..., description="The seniority level (e.g., Junior, Mid, Senior) for which to analyze competitor JDs.")

class CompetitorJDAnalysisOutput(BaseModel):
    '''Returns structural patterns (sections used, language style, differentiators), and gaps in competitor JDs that can be exploited.'''
    companies_analyzed : int
    individual_analyses: Dict[str, Dict]
    structural_patterns: Dict[str, List[str]]
    identified_gaps: List[str]
    competitive_opportunities: List[str]
    generated_parser_code: str
    timestamp : str

class LegalRequirementsCheckerArgs(BaseModel):
    """Input schema for legal requirements checker tool."""
    jurisdiction: str = Field(
        ..., 
        description="State (e.g., 'Maharashtra', 'Karnataka') or country (e.g., 'United States', 'United Kingdom') for which to check legal requirements. Supports 40 Indian states and 30 countries."
    )
    role_type: str = Field(
        ..., 
        description="Type of role - either 'technical_role' (software engineer, developer, architect) or 'managerial_role' (manager, director, executive)."
    )
    checks: List[str] = Field(
        default=["required_disclosures", "prohibited_language", "mandatory_policies"],
        description="List of checks to perform: 'required_disclosures' (mandatory information to disclose), 'prohibited_language' (language that violates employment law), 'mandatory_policies' (required policies and compliance)."
    )

class LegalRequirementsCheckerOutput(BaseModel):
    """Output schema for legal requirements checker results."""
    status: str = Field(..., description="Status of the request: 'success' or 'error'")
    jurisdiction: str = Field(..., description="The jurisdiction checked")
    role_type: Optional[str] = Field(None, description="The role type checked")
    requirements: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Dictionary containing requested requirements: required_disclosures, prohibited_language, and/or mandatory_policies"
    )
    timestamp: str = Field(..., description="Timestamp of when the check was performed")
    data_source: Optional[str] = Field(None, description="Source of the legal requirements data (e.g., specific labor law databases or government gazettes)")
    last_updated: Optional[str] = Field(None, description="When the legal database was last updated - Monthly from official gazette sources")

class DEILanguageArgs(BaseModel):
    '''Input schema for DEI language auditor tool.'''
    job_description: str = Field(..., description="The text of the job description to be audited for DEI language.")
    threshold: float = Field(0.5, description="The bias score threshold above which the tool will trigger an escalation to the Bias Guardian Agent for further review and recommendations.")

class DEILanguageOutput(BaseModel):
    '''Output schema for DEI language audit results.'''
    flagged_words: List[str] = Field(..., description="List of potentially biased terms found in the job description.")
    replacement_suggestions: List[str] = Field(..., description="List of suggested more inclusive alternatives corresponding to the flagged terms.")
    bias_score: float = Field(..., description="A score representing the level of bias in the job description, calculated based on the number and severity of flagged terms relative to the total word count.")
    recommendation: Optional[str] = Field(None, description="A recommendation for whether the job description should be revised based on the bias score and threshold.")
    escalated : bool = Field(False, description="Indicates whether the issue was escalated to the Bias Guardian Agent for further review and recommendations.")
    escalation_details: Optional[Dict] = Field(None, description="Details of the escalation to the Bias Guardian Agent, including any additional findings or recommendations provided by the agent.")


class JDPosterArgs(BaseModel):
    '''Input schema for JD formatting and posting tool.'''
    title: str = Field(..., description="The job title for the position being posted.")
    description: str = Field(..., description="The full text of the job description to be formatted and posted.")
    location: Optional[str] = Field(None, description="The geographic location of the job (e.g., city, state, country).")
    employment_status: Optional[str] = Field(default='FULL_TIME', description="The employment status for the position (e.g., FULL_TIME, PART_TIME, CONTRACT).")
    workplace_types: Optional[List[str]] = Field(default=['ONSITE'], description="The workplace types for the position (e.g., ONSITE, REMOTE, HYBRID).")
    external_id: Optional[str] = Field(None, description="An optional external identifier for the job posting to help track it across platforms.")

class JDPosterOutput(BaseModel):
    '''Output schema for JD formatting and posting results.'''
    linkedin: Dict[str, Any] = Field(..., description="Results from posting to LinkedIn.")
    naukri: Dict[str, Any] = Field(..., description="Results from posting to Naukri.")
    ats: Dict[str, Any] = Field(..., description="Results from posting to ATS platforms.")