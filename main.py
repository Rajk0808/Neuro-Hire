from agents.JD_Arcitecture_agent import __tools__
from crewai import Agent, Crew, Task
from dotenv import load_dotenv
from custom_llm.CustomLLM import CustomLLM
import json
load_dotenv()

"""agent = Agent(
    name="JD Architecture Agent",
    role="An agent that synthesizes job descriptions, checks legal compliance, extracts skills, analyzes competitors, benchmarks salaries, audits for DEI language, and posts to job platforms.",
    goal = "Create comprehensive and compliant job descriptions that attract top talent while ensuring legal adherence and competitive positioning.",
    backstory = "As the JD Architecture Agent, you are responsible for creating detailed and compliant job descriptions. You will research legal requirements based on jurisdiction and role type, extract relevant skills, analyze competitor job descriptions, benchmark salaries, audit for DEI language, and post the finalized job description to platforms like LinkedIn and Naukri. Your work ensures that job descriptions are not only attractive to potential candidates but also adhere to legal standards and industry best practices.",
    escalation_handler=None,
    llm=CustomLLM(model="gpt-oss-20b", temperature=0.7),
    tools = __tools__

)"""

competitor_analysis_agent = Agent(
    name="Competitor JD Analysis Agent",
    role="An agent that analyzes competitor job descriptions to identify structural patterns, language style, differentiators, and gaps that can be exploited.",
    goal = "Provide insights into competitor job descriptions to help create more effective and competitive job postings.",
    backstory = "As the Competitor JD Analysis Agent, you will analyze job descriptions from specified competitor companies for a given role and seniority level. Your analysis will identify structural patterns such as common sections used, language style, differentiators that set competitors apart, and gaps in their job descriptions that can be exploited to make our job postings more attractive to potential candidates.",
    escalation_handler=None,
    llm=CustomLLM(model="gpt-oss-20b", temperature=0.7),
    tools = [__tools__[3]]
)

dei_audit_agent = Agent(
    name="DEI Language Audit Agent",
    role="An agent that audits job descriptions for biased language and provides recommendations for more inclusive alternatives.",
    goal = "Ensure that job descriptions are free of biased language and promote diversity, equity, and inclusion.",
    backstory = "As the DEI Language Audit Agent, you will review the text of job descriptions to identify any biased language that may deter diverse candidates from applying. You will provide specific recommendations for more inclusive alternatives to ensure that our job postings promote diversity, equity, and inclusion.",
    escalation_handler=None,
    llm=CustomLLM(model="gpt-oss-20b", temperature=0.7),
    tools = [__tools__[5]]
)

legal_compliance_agent = Agent(
    name="Legal Compliance Checker Agent",
    role="An agent that checks job descriptions for legal compliance based on jurisdiction and role type.",
    goal = "Ensure that job descriptions adhere to legal requirements to avoid potential legal issues and ensure fair hiring practices.",
    backstory = "As the Legal Compliance Checker Agent, you will review job descriptions to ensure they comply with legal requirements based on the specified jurisdiction (state or country) and role type (technical or managerial). You will check for required disclosures, prohibited language, and mandatory policies to ensure that our job postings are legally compliant.",
    escalation_handler=None,
    llm=CustomLLM(model="gpt-oss-20b", temperature=0.7),
    tools = [__tools__[0]]
)

salary_benchmark_agent = Agent(
    name="Salary Benchmarking Agent",
    role="An agent that benchmarks salaries for specific roles and locations to ensure competitive compensation packages.",
    goal = "Provide accurate salary benchmarks to help create competitive compensation packages that attract top talent.",
    backstory = "As the Salary Benchmarking Agent, you will research and provide salary benchmarks for specific job roles and locations. Your insights will help ensure that our compensation packages are competitive within the industry and attractive to potential candidates.",
    escalation_handler=None,
    llm=CustomLLM(model="gpt-oss-20b", temperature=0.7),
    tools = [__tools__[4]]
)

skill_extraction_agent = Agent(
    name="Skill Extraction Agent",
    role="An agent that extracts must-have, good-to-have, anti-pattern, emerging, and GitHub-associated skills for specific roles and domains.",
    goal = "Identify relevant skills to include in job descriptions that accurately reflect the requirements of the role and domain.",
    backstory = "As the Skill Extraction Agent, you will analyze source text to extract relevant skills for specific job roles and domains. You will categorize these skills into must-have, good-to-have, anti-pattern (not relevant or desirable), emerging (gaining traction in the industry), and GitHub-associated skills (extracted from relevant repositories). Your insights will help ensure that our job descriptions accurately reflect the skills required for the role.",
    escalation_handler=None,
    llm=CustomLLM(model="gpt-oss-20b", temperature=0.7),
    tools = [__tools__[2]]
)

task = Task(
    name="Create a Job Description",
    description="Given a job role and domain, create a comprehensive job description, ensure legal compliance, extract relevant skills, analyze competitor JDs, benchmark salaries and audit for DEI language, do not mention this things in final output.",
    expected_output="A detailed job description for a Mid-Level Software Engineer role in the Technology domain, located in Bangalore, India. The description should include sections such as Job Title, Location, Job Summary, Responsibilities, Required Skills, Preferred Skills, Qualifications, Benefits, and Company Overview. It should be compliant with legal requirements for the specified jurisdiction and role type, free of biased language, and optimized for posting on platforms like LinkedIn and Naukri.",
    agent=legal_compliance_agent
)

crew = Crew(agents=[legal_compliance_agent, salary_benchmark_agent, skill_extraction_agent, competitor_analysis_agent, dei_audit_agent], tasks=[task])
result = crew.kickoff()

print("*"*70,"\n")
print("Result type:", type(result),"\n")
print('*'*70,"\n")

# Access the task output correctly
if hasattr(result, 'raw'):
    #print("Raw output:", result.raw)
    try:
        res = json.loads(result.raw)
        print("Parsed JSON:")
        print(res['content'])
        print('*'*70,"\n")
        print("Tools used:")
        if 'tools_used' in res:
            for tool in res['tools_used']:
                print(tool)
        else:
            print("No tools used or 'tools_used' key not found.")
    except:
        print("Output is not JSON:", result.raw)
elif hasattr(result, 'tasks_output'):
    print("Task outputs:", result.tasks_output)
    if result.tasks_output:
        for output in result.tasks_output:
            print(output)
else:
    print("Result:", result)

print("*"*70,"\n")
