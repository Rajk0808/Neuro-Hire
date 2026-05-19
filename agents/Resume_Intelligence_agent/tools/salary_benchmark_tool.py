import os
import requests
from crewai.tools import BaseTool
from agents.Resume_Intelligence_agent.schema.research_schema import (
    SalaryBenchMarkerArgs, 
    SalaryBenchMarkerOutput, 
)
# Research Tool: Salary Benchmarking    
class SalaryBenchMarkerTool(BaseTool):

    name : str = "SalaryBenchMarkerTool"
    description : str = "A tool to benchmark salaries for specific roles, specializations, locations, and experience levels."

    def _run(self, args : SalaryBenchMarkerArgs) -> SalaryBenchMarkerOutput:
        url = "https://job-salary-data.p.rapidapi.com/job-salary"
        querystring = {
            "role": args.role,
            "specialization": args.specialization or "",
            "location": args.location or "",
            "experience_years": args.experience_years or "",
            "percentile_range": ",".join(map(str, args.percentile_range)) if args.percentile_range else ""
        }
        
        headers = {
            "x-rapidapi-key": os.getenv("X_RAPIDAPI_KEY"),
            "x-rapidapi-host": os.getenv("X_RAPIDAPI_HOST") 
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring)
    
            if response.status_code == 200:
                data = response.json()
                return SalaryBenchMarkerOutput(
                    min_salary=data.get("min_salary", 0.0),
                    max_salary=data.get("max_salary", 0.0),
                    median_salary=data.get("median_salary", 0.0),
                    min_base_salary=data.get("min_base_salary", 0.0),
                    max_base_salary=data.get("max_base_salary", 0.0),
                    median_base_salary=data.get("median_base_salary", 0.0),
                    market_note=data.get("market_note", ''),
                    competing_titles=data.get("competing_titles", [])
                )
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}")
                print(response.text)
                return {}
        except requests.RequestException as e:
            print(f"Error occurred while fetching salary data: {e}")
            raise Exception("Failed to fetch salary data from the API.")

