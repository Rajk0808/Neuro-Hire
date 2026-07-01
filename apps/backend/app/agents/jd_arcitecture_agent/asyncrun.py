from agents.jd_arcitecture_agent import *
from crewai import Agent, Task, Crew
from services.pg_db_service import execute_query

# ==========================================
# 1. DEFINE AGENTS & CREWS
# ==========================================
jd_creator = Agent(
    role="Senior HR Architect and Copywriter",
    goal="Extract skills, benchmark salaries, check legal compliance, and write an inclusive Job Description.",
    backstory="You are an expert recruiter who utilizes data tools to optimize job profiles.",
    tools=[LegalRequirementsCheckerTool(), SkillsExtractorTool(), CompetitorJDAnalyzerTool(), SalaryBenchMarkerTool(), DEILanguageTool()],
    verbose=True
)

jd_publisher = Agent(
    role="Talent Acquisition Publisher",
    goal="Post finalized and approved job descriptions to corporate job boards.",
    backstory="A precise execution agent responsible for publicizing approved job listings.",
    tools=[JDPosterTool()],
    verbose=True
)

# ==========================================
# 2. FLOW 1: ASYNC GENERATION / REWRITE
# ==========================================
async def generate_or_edit_jd(session_id: str, raw_text: str):
    """Runs the initial creation or editing loop as a non-blocking background task."""
    execute_query("UPDATE sessions SET status = 'processing' WHERE id = %s", (session_id,))

    # Define a focused drafting task
    draft_task = Task(
        description=f"Draft or refine a comprehensive, inclusive Job Description based on this input: {raw_text}",
        expected_output="A polished, complete Job Description text draft.",
        agent=jd_creator
    )
    
    crew = Crew(agents=[jd_creator], tasks=[draft_task], verbose=True)
    
    # 💡 Crucial: Use kickoff_async() to release the Python event loop thread
    crew_output = await crew.kickoff_async()
    
    # Update our state database with the result
    execute_query("UPDATE sessions SET status = 'awaiting_human_review', current_draft = %s WHERE id = %s", (crew_output.raw, session_id))
    print(f"🎯 [Session {session_id}] Draft generation complete. Paused for human approval.")

# ==========================================
# 3. FLOW 2: ASYNC POSTING EXECUTOR
# ==========================================
async def publish_approved_jd(session_id: str, final_jd: str):
    """Runs the posting tool asynchronously once the human confirms approval."""
    execute_query("UPDATE sessions SET status = 'posting' WHERE id = %s", (session_id,))

    post_task = Task(
        description="Take this approved job description and publish it directly to the boards.",
        expected_output="A confirmation log or deployment string.",
        agent=jd_publisher,
        inputs={"approved_jd": final_jd}
    )
    
    crew = Crew(agents=[jd_publisher], tasks=[post_task], verbose=True)
    crew_output = await crew.kickoff_async()
    
    execute_query("UPDATE sessions SET status = 'completed', posting_result = %s WHERE id = %s", (crew_output.raw, session_id))
    print(f"🎉 [Session {session_id}] Successfully posted job description!")
