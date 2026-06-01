import os
import requests
from typing import Type
from pydantic import ConfigDict
from crewai.tools import BaseTool
from apps.backend.app.agents.JD_Arcitecture_agent.schema.research_schema import (
    SalaryBenchMarkerArgs, 
    SalaryBenchMarkerOutput, 
)
# Research Tool: Salary Benchmarking    
class SalaryBenchMarkerTool(BaseTool):

    name: str = "SalaryBenchMarkerTool"
    description: str = (
        "Use this tool to fetch salary benchmarking data for a given job role, specialization, location, and experience level. "
        "The tool returns market salary ranges, base salary ranges, median salaries, and notes on market trends. "
        "This information helps ensure that job descriptions offer competitive and compliant compensation packages."
    )
    args_schema: Type[SalaryBenchMarkerArgs] = SalaryBenchMarkerArgs
    output_schema: Type[SalaryBenchMarkerOutput] = SalaryBenchMarkerOutput
    
    model_config = ConfigDict(arbitrary_types_allowed=True, extra='allow')
    
    def _run(self, role: str, specialization: str = None, location: str = None, experience_years: str = None, percentile_range: list = None) -> SalaryBenchMarkerOutput:
        url = "https://job-salary-data.p.rapidapi.com/job-salary"
        querystring = {
            "role": role,
            "specialization": specialization or "",
            "location": location or "",
            "experience_years": experience_years or "",
            "percentile_range": ",".join(map(str, percentile_range)) if percentile_range else ""
        }
        
        headers = {
            "x-rapidapi-key": os.getenv("X_RAPIDAPI_KEY"),
            "x-rapidapi-host": os.getenv("X_RAPIDAPI_HOST") 
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring)
    
            if response.status_code == 200:
                data = response.json()
                return {
                    "min_salary": data.get("min_salary", 0.0),
                    "max_salary": data.get("max_salary", 0.0),
                    "median_salary": data.get("median_salary", 0.0),
                    "min_base_salary": data.get("min_base_salary", 0.0),
                    "max_base_salary": data.get("max_base_salary", 0.0),
                    "median_base_salary": data.get("median_base_salary", 0.0),
                    "market_note": data.get("market_note", ''),
                    "competing_titles": data.get("competing_titles", [])
                }
            else:
                print(f"Failed to fetch data. Status code: {response.status_code}")
                print(response.text)
                return {}
        except requests.RequestException as e:
            print(f"Error occurred while fetching salary data: {e}")
            raise Exception("Failed to fetch salary data from the API.")

