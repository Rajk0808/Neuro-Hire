"""
Neo4j Retrieval Service
"""
from CustomException import CustomException
from agents.Resume_Intelligence_agent.database.clients import neo4j_client
from agents.Resume_Intelligence_agent.services.retrival_services.extractor.extract import extractor
import logging
logger = logging.getLogger(__name__)

class Neo4jRetrieval:
    def __init__(self):
        self.client = neo4j_client

    def run_query(self, query: str):
        "Runs query on Neo4j database using the provided driver."
        try:
            result = self.client.execute_query(query, database="neo4j")
            return result
        except Exception as e:
            logger.error(f"Error running query: {e}")
            raise CustomException(f"Error running query: {e}")
    

    def built_query(self, **kwargs):
        "Builds a Cypher query based on the provided information."

        query = "MATCH "
        nodes = []

        # Check for Nodes
        if 'jobreq_id' in kwargs:
            nodes.append('(c:Candidate)-[:APPLIED_TO]->(j:JobReq)')
        if 'skill_name' in kwargs:
            nodes.append('(c:Candidate)-[:HAS_SKILL]->(s:Skill)')
        if 'company_name' in kwargs:
            nodes.append('(c:Candidate)-[:WORKED_AT]->(co:Company)')
        if 'education_name' in kwargs:
            nodes.append('(c:Candidate)-[:HAS_EDUCATION]->(e:Education)')
        if 'industry_name' in kwargs:
            nodes.append('(c:Candidate)-[:WORKED_AT]->(co:Company)-[:IN_INDUSTRY]->(i:Industry)')
        if 'job_title' in kwargs:
            nodes.append('(c:Candidate)-[:HELD_ROLE]->(r:Role)')
        
        query += ', '.join(nodes)
        query += " WHERE "
        conditions = []
        if 'jobreq_id' in kwargs:
            conditions.append(f"j.id = '{kwargs['jobreq_id']}'")
        
        # Candidate conditions
        if 'candidate' in kwargs:
            if isinstance(kwargs['candidate'], dict):
                if isinstance(kwargs['candidate']['location'], list):
                    conditions.append(f"c.location IN {kwargs['candidate']['location']}")
                else:
                    conditions.append(f"c.location = '{kwargs['candidate']['location']}'")

        # Skill conditions 
        if 'skill' in kwargs:
            if isinstance(kwargs['skill'], dict):
                if isinstance(kwargs['skill']['name'], list):
                    conditions.append(f"s.name IN {kwargs['skill']['name']}")
                else:
                    conditions.append(f"s.name = '{kwargs['skill']['name']}'")
                if 'proficiency' in kwargs['skill']:
                    if isinstance(kwargs['skill']['proficiency'], list):
                        conditions.append(f"s.proficiency IN {kwargs['skill']['proficiency']}")
                    else:
                        conditions.append(f"s.proficiency = '{kwargs['skill']['proficiency']}'")
                
                if 'category' in kwargs['skill']:
                    if isinstance(kwargs['skill']['category'], list):
                        conditions.append(f"s.category IN {kwargs['skill']['category']}")
                    else:
                        conditions.append(f"s.category = '{kwargs['skill']['category']}'")

        # Company conditions
        if 'company' in kwargs:
            if isinstance(kwargs['company']['name'], list):
                conditions.append(f"co.name IN {kwargs['company']['name']}")
            else:
                conditions.append(f"co.name = '{kwargs['company']['name']}'")
            if 'sector' in kwargs['company']:
                if isinstance(kwargs['company']['sector'], list):
                    conditions.append(f"co.sector IN {kwargs['company']['sector']}")
                else:
                    conditions.append(f"co.sector = '{kwargs['company']['sector']}'")
            if 'size' in kwargs['company']:
                if isinstance(kwargs['company']['size'], list):
                    conditions.append(f"co.size IN {kwargs['company']['size']}")
                else:
                    conditions.append(f"co.size = '{kwargs['company']['size']}'")
            if 'stage' in kwargs['company']:
                if isinstance(kwargs['company']['stage'], list):
                    conditions.append(f"co.stage IN {kwargs['company']['stage']}")
                else:
                    conditions.append(f"co.stage = '{kwargs['company']['stage']}'")
            
        # Educational conditions
        if 'education' in kwargs:
            if isinstance(kwargs['education']['name'], list):
                conditions.append(f"e.name IN {kwargs['education']['name']}")
            else:
                conditions.append(f"e.name = '{kwargs['education']['name']}'")
            if 'degree' in kwargs['education']:
                if isinstance(kwargs['education']['degree'], list):
                    conditions.append(f"e.degree IN {kwargs['education']['degree']}")
                else:
                    conditions.append(f"e.degree = '{kwargs['education']['degree']}'")
            if 'year' in kwargs['education']:
                if isinstance(kwargs['education']['year'], list):
                    conditions.append(f"e.year IN {kwargs['education']['year']}")
                else:
                    conditions.append(f"e.year >= '{kwargs['education']['year']}'")
            if 'gpa' in kwargs['education']:
                if isinstance(kwargs['education']['gpa'], list):
                    conditions.append(f"e.gpa IN {kwargs['education']['gpa']}")
                else:
                    conditions.append(f"e.gpa >= '{kwargs['education']['gpa']}'")
        
        # Industry conditions
        if 'industry' in kwargs:
            if 'industry_name' in kwargs['industry']:
                if isinstance(kwargs['industry']['industry_name'], list):
                    conditions.append(f"i.name IN {kwargs['industry']['industry_name']}")
                else:
                    conditions.append(f"i.name = '{kwargs['industry']['industry_name']}'")
            if 'subsector' in kwargs['industry']:
                if isinstance(kwargs['industry']['subsector'], list):
                    conditions.append(f"i.subsector IN {kwargs['industry']['subsector']}")
                else:
                    conditions.append(f"i.subsector = '{kwargs['industry']['subsector']}'")
            if 'regulation' in kwargs['industry']:
                if isinstance(kwargs['industry']['regulation'], list):
                    conditions.append(f"i.regulation IN {kwargs['industry']['regulation']}")
                else:
                    conditions.append(f"i.regulation = '{kwargs['industry']['regulation']}'")
    
        # Role Based conditions
        if 'role' in kwargs:
            if 'title' in kwargs['role']:
                if isinstance(kwargs['role']['title'], list):
                    conditions.append(f"r.title IN {kwargs['role']['title']}")
                else:
                    conditions.append(f"r.title = '{kwargs['role']['title']}'")
            if 'domain' in kwargs['role']:
                if isinstance(kwargs['role']['domain'], list):
                    conditions.append(f"r.domain IN {kwargs['role']['domain']}")
                else:
                    conditions.append(f"r.domain = '{kwargs['role']['domain']}'")   
            
        if 0 < len(conditions):
            query += " AND ".join(conditions)
        else:
            query = query.replace(" WHERE ", "")

        if 'limit' in kwargs:
            query += f" LIMIT {kwargs['limit']}"
        
        query += " RETURN c"

        if 'order_by' in kwargs:
            query += f" ORDER BY {kwargs['order_by']}"

        return query
    
    def built_retrieval_query(self, query, job_req_id=None, n_results=10):
        "Builds a Cypher query based on the provided information and runs it on the Neo4j database."
        try:
            kwargs = extractor(query)
            if job_req_id:
                kwargs['jobreq_id'] = job_req_id
            kwargs['limit'] = n_results
            query = self.built_query(**kwargs)
        except Exception as e:
            logger.error(f"Error building retrieval query: {e}")
            raise CustomException(f"Error building retrieval query: {e}")
   
    def retrieve(self, query, job_req_id=None, n_results=10):
        "Builds a Cypher query based on the provided information and runs it on the Neo4j database."
        try:
            retrieval_query = self.built_retrieval_query(query, job_req_id, n_results)
            result = self.run_query(retrieval_query)
            return result
        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            raise CustomException(f"Error retrieving data: {e}")