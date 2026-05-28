from pydantic import BaseModel, Field

class JobReq_node(BaseModel):
    id : str | None = Field(default='', description="Unique identifier for the job requirement")
    status : bool | None = Field(default=True, description="Status of the job requirement, e.g., active or inactive")
    posted_date : str | None = Field(default='', description="Date when the job requirement was posted")
    title : str | None = Field(default='', description="Title of the job requirement")
    description : str | None = Field(default='', description="Detailed description of the job requirement")

class Candidate_node(BaseModel):
    id : str | None = Field(default='', description="Unique identifier for the candidate")
    name : str | None = Field(default='', description="Name of the candidate")
    contact_info : list[str | list | None] = Field(default=[], description="Contact information for the candidate, e.g., email or phone")
    status : bool | None = Field(default=True, description="Status of the candidate, e.g., active or inactive")
    location : str | None = Field(default='', description="Location of the candidate")

class Skill_node(BaseModel):
    name : str | None = Field(default='', description="Name of the skill")
    category : str | None = Field(default='', description="Category of the skill, e.g., technical, soft skill")
    proficiency : str | None = Field(default='', description="Proficiency level of the skill, e.g., beginner, intermediate, expert")

class Role_node(BaseModel):
    title : str | None = Field(default='', description="Title of the role")
    seniority : str | None = Field(default='', description="Seniority level of the role, e.g., junior, mid-level, senior")
    domain : str | None = Field(default='', description="Domain of the role, e.g., software engineering, data science")

class Company_node(BaseModel):
    name : str | None = Field(default='', description="Name of the company")
    sector : str | None = Field(default='', description="Sector of the company, e.g., technology, finance")
    stage : str | None = Field(default='', description="Stage of the company, e.g., startup, growth, established")
    size : str | None = Field(default='', description="Size of the company, e.g., startup, mid-size, enterprise")
    industry : str | None = Field(default='', description="Industry of the company, e.g., software, healthcare")
    regulation : str | None = Field(default='', description="Regulation level of the company, e.g., high, medium, low")

class Education_node(BaseModel):
    degree : str | None = Field(default='', description="Degree obtained by the candidate")
    institution : str | None = Field(default='', description="Institution where the degree was obtained")
    year : str | None = Field(default='', description="Year when the degree was obtained")
    gpa : str | None = Field(default='', description="GPA achieved by the candidate, if applicable")
    
class Industry_node(BaseModel):
    name : str | None = Field(default='', description="Name of the industry")
    subsector : str | None = Field(default='', description="Sector of the industry, e.g., technology, healthcare")
    regulation : str | None = Field(default='', description="Regulation level of the industry, e.g., high, medium, low")

class Candidate_data(BaseModel):
    id : str | None = Field(default='', description="Unique identifier for the candidate")
    name : str | None = Field(default='', description="Name of the candidate")
    contact_info : list[str | list | None] = Field(default=[], description="Contact information for the candidate, e.g., email or phone")
    status : bool | None = Field(default=True, description="Status of the candidate, e.g., active or inactive")
    location : str | None = Field(default='', description="Location of the candidate")
    skills : list[Skill_node] = Field(default=[], description="List of skills possessed by the candidate")
    roles : list[Role_node] = Field(default=[], description="List of roles held by the candidate")
    companies : list[Company_node] = Field(default=[], description="List of companies the candidate has worked at")
    education : list[Education_node] = Field(default=[], description="List of educational qualifications of the candidate")