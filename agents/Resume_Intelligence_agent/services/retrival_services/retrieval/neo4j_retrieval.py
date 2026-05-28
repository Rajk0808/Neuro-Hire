"""
Neo4j Retrieval Service
"""
from CustomException import CustomException
from agents.Resume_Intelligence_agent.database.clients import neo4j_client
import logging
logger = logging.getLogger(__name__)

class Retriever():

    def __init__(self):
        self.driver = neo4j_client()

    def run_query(self, query: str):
        "Runs query on Neo4j database using the provided driver."
        with self.driver.session() as session:
            result = session.run(query)
            return result
    
    def retrieve_by_education(self,job_requirement_id : str | None = None, degree : str | None = None, institue_name : str | None = None, year : str | None = None, gpa : str | None = None , n_results : int = 5):
        query = "MATCH (j:JobReq)-[APPLIED_TO]->(p:Person)-[:STUDIED_AT]->(e:Education) WHERE "
        where_clauses = []
        if job_requirement_id:
            where_clauses.append(f"j.id = '{job_requirement_id}'")
        if degree:
            where_clauses.append(f"e.degree = '{degree}'")
        if institue_name:
            where_clauses.append(f"e.institute_name = '{institue_name}'")
        if year:
            where_clauses.append(f"e.year = '{year}'")
        if gpa:
            where_clauses.append(f"e.gpa = '{gpa}'")
        if where_clauses:
            query += " AND ".join(where_clauses)
        query += f" RETURN p.name AS name, e.degree AS degree, e.institute_name AS institute_name, e.year AS year, e.gpa AS gpa LIMIT {n_results}"
        try:
            logger.info(f"Running query by Education: {query}")
            result = self.run_query(query)
            return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error retrieving by education: {e}")
            raise CustomException(f"Error retrieving by education: {e}")
    
    def retrieve_by_experience(self,job_requirement_id : str | None = None, title : str | None = None, company : str | None = None, years : str | None = None, n_results : int = 5):
        query = "MATCH (j:JobReq)-[APPLIED_TO]->(sp:Person)-[:WORKED_AT]->(e:Experience) WHERE "
        where_clauses = []
        if job_requirement_id:
            where_clauses.append(f"j.id = '{job_requirement_id}'")
        if title:
            where_clauses.append(f"e.title = '{title}'")
        if company:
            where_clauses.append(f"e.company = '{company}'")
        if years:
            where_clauses.append(f"e.years = '{years}'")
        if where_clauses:
            if len(where_clauses) > 1:
                query += " AND ".join(where_clauses) 
            else:
                query += where_clauses[0]
        query += f" RETURN p.name AS name, e.title AS title, e.company AS company, e.years AS years LIMIT {n_results}"
        try:
            logger.info(f"Running query by Experience: {query}")
            result = self.run_query(query)
            return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error retrieving by experience: {e}")
            raise CustomException(f"Error retrieving by experience: {e}")
    
    def retrieve_by_skill(self, skill_name : str, job_requirement_id : str | None = None, n_results : int = 5):
        query = f"MATCH (j:JobReq)-[APPLIED_TO]->(p:Person)-[:HAS_SKILL]->(s:Skill) WHERE j.id = '{job_requirement_id}' AND s.name = '{skill_name}' RETURN p.name AS name, s.name AS skill LIMIT {n_results}"
        try:
            logger.info(f"Running query by Skill: {query}")
            result = self.run_query(query)
            return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error retrieving by skill: {e}")
            raise CustomException(f"Error retrieving by skill: {e}")
        
    def retrieve_by_industry(self, industry_name : str, job_requirement_id : str | None = None, n_results : int = 5):
        query = f"MATCH (j:JobReq)-[APPLIED_TO]->(p:Person)-[:WORKED_AT]->(e:Experience)->[:IN_INDUSTRY] WHERE j.id = '{job_requirement_id}' AND i.name = '{industry_name}'  RETURN p.name AS name, e.industry AS industry ORDER BY e.stage LIMIT {n_results}"
        try:
            logger.info(f"Running query by Industry: {query}")
            result = self.run_query(query)
            return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error retrieving by industry: {e}")
            raise CustomException(f"Error retrieving by industry: {e}")
    
    def retrieve_by_role(self, role_name : str, job_requirement_id : str | None = None, n_results : int = 5):
        query = f"MATCH (j:JobReq)-[APPLIED_TO]->(p:Person)-[:HELD_ROLE]->(r:Role) WHERE r.title = '{role_name}'"
        if job_requirement_id:
            query += f" AND j.id = '{job_requirement_id}'"
        query += f" RETURN p.name AS name, r.title AS role LIMIT {n_results}"
        try:
            logger.info(f"Running query by Role: {query}")
            result = self.run_query(query)
            return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error retrieving by role: {e}")
            raise CustomException(f"Error retrieving by role: {e}")
    
def neo4j_retrieval(query, job_requirement_id : str | None = None, n_results : int =5):
    """
    Retrieves relevant information from Neo4j based on the query and index name.

    Args:
        query (str): The search query.
        job_requirement_id (str | None): The ID of the job requirement.
        n_results (int): The number of results to retrieve."""
    retriever = Retriever()
    
    function_mapping = {
        "education": retriever.retrieve_by_education,
        "experience": retriever.retrieve_by_experience,
        "skill": retriever.retrieve_by_skill,
        "industry": retriever.retrieve_by_industry,
        "role": retriever.retrieve_by_role
    }

    pass
