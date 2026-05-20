from agents.JD_Arcitecture_agent import __tools__
from crewai import Agent, Crew, Task
from dotenv import load_dotenv
from custom_llm.CustomLLM import CustomLLM
import json
load_dotenv()

agent = Agent(
    name="JD Architecture Agent",
    role="An agent that synthesizes job descriptions, checks legal compliance, extracts skills, analyzes competitors, benchmarks salaries, audits for DEI language, and posts to job platforms.",
    goal = "Create comprehensive and compliant job descriptions that attract top talent while ensuring legal adherence and competitive positioning.",
    backstory = "As the JD Architecture Agent, you are responsible for creating detailed and compliant job descriptions. You will research legal requirements based on jurisdiction and role type, extract relevant skills, analyze competitor job descriptions, benchmark salaries, audit for DEI language, and post the finalized job description to platforms like LinkedIn and Naukri. Your work ensures that job descriptions are not only attractive to potential candidates but also adhere to legal standards and industry best practices.",
    escalation_handler=None,
    llm=CustomLLM(model="gpt-oss-20b", temperature=0.7, tools=__tools__)

)

task = Task(
    name="Create a Job Description",
    description="Given a job role and domain, create a comprehensive job description, ensure legal compliance, extract relevant skills, analyze competitor JDs, benchmark salaries and audit for DEI language.",
    expected_output="A detailed job description for a Mid-Level Software Engineer role in the Technology domain, located in Bangalore, India. The description should include sections such as Job Title, Location, Job Summary, Responsibilities, Required Skills, Preferred Skills, Qualifications, Benefits, and Company Overview. It should be compliant with legal requirements for the specified jurisdiction and role type, free of biased language, and optimized for posting on platforms like LinkedIn and Naukri.",
    agent=agent,
    tools=__tools__
)

crew = Crew(agents=[agent], tasks=[task])
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
