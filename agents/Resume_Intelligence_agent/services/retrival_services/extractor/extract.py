
from dotenv import load_dotenv
from agents.Resume_Intelligence_agent.database.schemas.neo4j_schema import *
load_dotenv()  
from langchain_openrouter import ChatOpenRouter
from langchain_core.output_parsers import JsonOutputParser
import os

def _make_client():
    """Test connection to local Ollama server"""
    model = ChatOpenRouter(
            model="openai/gpt-oss-120b:free",
            temperature=0.8,
            api_key= os.getenv("OPENROUTER_API_KEY")
        )
    return model
    
llm = _make_client()    
from langchain_core.prompts import ChatPromptTemplate

SYSTEM_PROMPT = ChatPromptTemplate.from_template("""
You are a helpful assistant for extracting structured information from unstructured text.
so that it can be easily stored in a database and queried later.

output should be in JSON format with the following fields:
- candidate : {candidate_schema}
- education : {education_schema}
- skills : {skills_schema}
- company : {company_schema}
- industry : {industry_schema}
- role : {role_schema}

fill None in None format not in string format for any field that is not present in the input text.
example output:
{{
    "candidate": {{
        "name": "John Doe",
        "contact_info": "john.doe@example.com",
        "location": ["New York, USA"]
    }},
    "education": [{{
        "degree": "Master's degree",
        "field": "Computer Science",
        "university": "XYZ University"
    }}],
    "skills": [
        {{"name": "Python",
         "proficiency": "Expert"}},
        {{"name": "R",
         "proficiency": "Intermediate"}}
    ],
    "company": [{{
        "name": "ABC Company",
        "sector": "Technology",
        "stage": "Series A",
        "size": "50-200 employees"
    }}],
    "industry": [{{
        "name": "Technology",
        "sector": "Software Development",
        "regulation": "NA"
    }}],
    "role": [{{
        "title": "Data Scientist",
        "domain": "Machine Learning"
    }}]
}}
                                   
extract the above information from the following text:

{input_text}
                                                
""")

# Apply partial variables with schema information
SYSTEM_PROMPT = SYSTEM_PROMPT.partial(
    candidate_schema=Candidate_node.model_json_schema(),
    education_schema=Education_node.model_json_schema(),
    skills_schema=Skill_node.model_json_schema(),
    company_schema=Company_node.model_json_schema(),
    industry_schema=Industry_node.model_json_schema(),
    role_schema=Role_node.model_json_schema()
)

def extract_structured_info(input_text: str) -> dict:
    """Extract structured information from unstructured text using the defined system prompt."""
    prompt = SYSTEM_PROMPT.format(input_text=input_text)
    response = llm.invoke(prompt)
    return response

def extractor(query: str) -> dict:
    parser = JsonOutputParser()
    structured_info = extract_structured_info(query)
    result = parser.parse(structured_info.content)
    return result
