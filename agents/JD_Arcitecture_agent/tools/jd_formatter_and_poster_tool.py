"""
Reformats the synthesized JD into platform-specific schemas (LinkedIn uses JSON-LD, Naukri uses XML, ATS platforms use their own API formats) and posts via authenticated API connections. Returns posting URLs, estimated reach, and time-to-first-applicant prediction.

"""
import datetime
import os 
from dotenv import load_dotenv
import requests

class JDPosterTool:
    """Tool for formatting and posting job descriptions to various platforms."""
     
    def __init__(self):
        """Initialize JD Poster Tool with API credentials from environment variables."""
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
    
    async def post_to_naukri(self, jd_data: dict) -> dict:
        """Format JD data to Naukri's XML schema and post via API."""
        naukri_payload = self.format_for_naukri(jd_data)
        headers = {'Authorization': f'Bearer {self.naukri_api_key}', 'Content-Type': 'application/xml'}
        
        
    async def format_for_naukri(self, jd_data: dict) -> str:
        """Convert JD data into Naukri's XML format."""
        xml_payload = f"""
        <job>
            <title>{jd_data.get('title', '')}</title>
            <description>{jd_data.get('description', '')}</description>
            <location>{jd_data.get('location', 'India')}</location>
            <employmentStatus>{jd_data.get('employment_status', 'FULL_TIME')}</employmentStatus>
            <externalJobPostingId>{jd_data.get('external_id', '')}</externalJobPostingId>
            <workplaceTypes>{','.join(jd_data.get('workplace_types', ['ONSITE']))}</workplaceTypes>
        </job>
        """
        return xml_payload.strip()