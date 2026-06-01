"""
Reformats the synthesized JD into platform-specific schemas (LinkedIn uses JSON-LD, Naukri uses XML, ATS platforms use their own API formats) and posts via authenticated API connections. Returns posting URLs, estimated reach, and time-to-first-applicant prediction.

"""
import datetime
import os 
from typing import Type
from dotenv import load_dotenv
import requests
from pydantic import ConfigDict
from crewai.tools import BaseTool
from apps.backend.app.agents.JD_Arcitecture_agent.schema.research_schema import JDPosterArgs, JDPosterOutput

class JDPosterTool(BaseTool):
    """Tool for formatting and posting job descriptions to various platforms."""
     
    name: str = "JDPosterTool"
    description: str = ("Use this tool to post the finalized job description to platforms like LinkedIn and Naukri. "
                   "Provide the job title, description, location, employment status, workplace types, and an optional external ID for tracking. "
                   "The tool will return the posting URLs and status for each platform.")
    args_schema: Type[JDPosterArgs] = JDPosterArgs
    output_schema: Type[JDPosterOutput] = JDPosterOutput
    
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')
    
    def __init__(self):
        """Initialize JD Poster Tool with API credentials from environment variables."""
        super().__init__()
        load_dotenv()
        self.linkedin_api_key = os.getenv('LINKEDIN_API_KEY')
        self.naukri_api_key = os.getenv('NAUKRI_API_KEY')
        self.ats_api_key = os.getenv('ATS_API_KEY')

    async def post_to_linkedin(self, jd_data: dict) -> dict:
        """Format JD data to LinkedIn's JSON-LD schema and post via API."""
        linkedin_payload = self.format_for_linkedin(jd_data)
        headers = {'Authorization': f'Bearer {self.linkedin_api_key}', 'Content-Type': 'application/json'}
        response = requests.post('https://api.linkedin.com/rest/simpleJobPostings', json=linkedin_payload, headers=headers)
        if response.status_code == 201:
            return {'status': 'success', 'platform': 'LinkedIn', 'posting_url': response.json().get('url')}
        else:
            return {'status': 'error', 'platform': 'LinkedIn', 'message': response.text}
    

    async def format_for_linkedin(self, jd_data: dict) -> dict:
        """Convert JD data into LinkedIn's JSON-LD format."""
        return {
            'elements': [
                {
                    "company": f"urn:li:company:{os.getenv('LINKEDIN_COMPANY_ID')}",
                    "companyApplyUrl": "http://linkedin.com",
                    "description": jd_data.get('description', ''),
                    "employmentStatus": jd_data.get('employment_status', 'FULL_TIME'),
                    "externalJobPostingId": jd_data.get('external_id', ''),
                    "listedAt": datetime.datetime.now(datetime.timezone.utc).isoformat() + 'Z',
                    "jobPostingOperationType": "CREATE",
                    "title": jd_data.get('title', ''),
                    "location": jd_data.get('location', 'India'),
                    "workplaceTypes": jd_data.get('workplace_types', ['ONSITE'])
                }
        ]
        }
    
    def _run(self, title: str, description: str, location: str = None, employment_status: str = 'FULL_TIME', workplace_types: list = None, external_id: str = None) -> JDPosterOutput:
        """Main method to post JD to all platforms and aggregate results."""
        jd_data = {
            'title': title,
            'description': description,
            'location': location,
            'employment_status': employment_status,
            'workplace_types': workplace_types or ['ONSITE'],
            'external_id': external_id
        }
        linkedin_result = self.post_to_linkedin(jd_data)
        # Placeholder for Naukri and ATS posting methods
        return {
            "linkedin": linkedin_result,
            "naukri": {"status": "not_implemented"},
            "ats": {"status": "not_implemented"}
        }