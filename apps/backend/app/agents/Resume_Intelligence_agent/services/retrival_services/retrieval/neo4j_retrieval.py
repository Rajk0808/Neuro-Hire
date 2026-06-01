"""
Neo4j Retrieval Service
"""
from CustomException import CustomException
from apps.backend.app.agents.Resume_Intelligence_agent.database.clients import neo4j_client
from apps.backend.app.agents.Resume_Intelligence_agent.services.retrival_services.extractor.extract import extractor
from apps.backend.app.agents.Resume_Intelligence_agent.services.vector_similarity_queries import get_vector_queries
from typing import List, Dict
import json
import logging
logger = logging.getLogger(__name__)

class Neo4jRetrieval:
    def __init__(self):
        self.client = neo4j_client
    def built_vector_query(
        self,
        query_text: str,
        entity_type: str = "Candidate",
        limit: int = 10,
        threshold: float = 0.7,
        metadata_filters: dict = None
    ) -> List[Dict]:
        """
        Build and execute a vector similarity query.
        
        Args:
            query_text (str): Semantic query (e.g., "Senior Python developer")
            entity_type (str): Type of entity ("Candidate", "Skill", "Role", "Company")
            limit (int): Maximum results
            threshold (float): Similarity threshold
            metadata_filters (dict): Optional metadata filters (e.g., {"location": "NYC"})
            
        Returns:
            List of results with similarity scores
            
        Example:
            >>> results = retrieval.built_vector_query(
            >>>     "Senior backend engineer",
            >>>     entity_type="Candidate",
            >>>     limit=10
            >>> )
        """
        try:
            queries = get_vector_queries(similarity_threshold=threshold)
            
            if entity_type == "Candidate":
                if metadata_filters:
                    # Use hybrid search with filters
                    return queries.hybrid_search_candidates(
                        query_text,
                        location=metadata_filters.get("location"),
                        status=metadata_filters.get("status"),
                        limit=limit,
                        threshold=threshold
                    )
                else:
                    # Use semantic search only
                    return queries.find_similar_candidates(
                        query_text,
                        limit=limit,
                        threshold=threshold
                    )
            elif entity_type == "Skill":
                return queries.find_similar_skills(
                    query_text,
                    limit=limit,
                    threshold=threshold
                )
            elif entity_type == "Role":
                return queries.find_similar_roles(
                    query_text,
                    limit=limit,
                    threshold=threshold
                )
            elif entity_type == "Company":
                return queries.find_similar_companies(
                    query_text,
                    limit=limit,
                    threshold=threshold
                )
            else:
                logger.error(f"Unknown entity type: {entity_type}")
                return []
            
        except Exception as e:
            logger.error(f"Error in built_vector_query: {e}")
            return []
        
    def get_candidates_for_job_semantic(
        self,
        job_id: str,
        limit: int = 20,
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Get candidates that semantically match a job requirement.
        Uses vector similarity and skill matching.
        
        Args:
            job_id (str): Job requirement ID
            limit (int): Maximum candidates
            threshold (float): Similarity threshold
            
        Returns:
            List of candidates ranked by match score
            
        Example:
            >>> candidates = retrieval.get_candidates_for_job_semantic("job_123", limit=20)
            >>> for candidate in candidates:
            >>>     print(f"{candidate['name']}: {candidate['match_score']}")
        """
        try:
            queries = get_vector_queries(similarity_threshold=threshold)
            results = queries.semantic_job_match(job_id, limit=limit, threshold=threshold)
            
            logger.info(f"Found {len(results)} semantic matches for job {job_id}")
            return results
            
        except Exception as e:
            logger.error(f"Error getting semantic candidates for job {job_id}: {e}")
            return []
        
    def find_similar_candidates_by_description(
        self,
        description: str,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Find candidates similar to a text description.
        Useful for natural language queries.
        
        Args:
            description (str): Candidate description/query
            limit (int): Maximum results
            threshold (float): Similarity threshold
            
        Returns:
            List of candidates with similarity scores
            
        Example:
            >>> candidates = retrieval.find_similar_candidates_by_description(
            >>>     "Looking for Python developers with 5 years experience in San Francisco",
            >>>     limit=10
            >>> )
        """
        try:
            queries = get_vector_queries(similarity_threshold=threshold)
            results = queries.find_similar_candidates(
                description,
                limit=limit,
                threshold=threshold
            )
            
            logger.info(f"Found {len(results)} similar candidates for description")
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar candidates: {e}")
            return [] 
        
    def get_top_candidate_matches(
        self,
        job_id: str,
        query_text: str = None,
        limit: int = 20,
        vector_weight: float = 0.7,
        skill_weight: float = 0.3
    ) -> List[Dict]:
        """
        Get top candidate matches using combined vector + semantic + skill scoring.
        
        Args:
            job_id (str): Job requirement ID
            query_text (str): Optional additional query text
            limit (int): Maximum results
            vector_weight (float): Weight for vector similarity (0-1)
            skill_weight (float): Weight for skill matching (0-1)
            
        Returns:
            Ranked list of candidates with combined scores
            
        Example:
            >>> top_candidates = retrieval.get_top_candidate_matches(
            >>>     "job_123",
            >>>     limit=10,
            >>>     vector_weight=0.7,
            >>>     skill_weight=0.3
            >>> )
        """
        try:
            queries = get_vector_queries()
            
            # Get semantic matches
            semantic_results = queries.semantic_job_match(job_id, limit=limit*2)
            
            # If additional query text provided, also search for similar candidates
            if query_text:
                description_results = queries.find_similar_candidates(
                    query_text,
                    limit=limit*2,
                    threshold=0.5
                )
                
                # Merge and deduplicate by candidate_id
                results_map = {}
                for result in semantic_results:
                    cand_id = result.get('candidate_id')
                    if cand_id:
                        results_map[cand_id] = result
                
                for result in description_results:
                    cand_id = result.get('candidate_id')
                    if cand_id and cand_id not in results_map:
                        results_map[cand_id] = result
                
                # Convert back to list and sort
                combined_results = list(results_map.values())
            else:
                combined_results = semantic_results
            
            # Sort by score and return top limit
            sorted_results = sorted(
                combined_results,
                key=lambda x: x.get('match_score', x.get('similarity', 0)),
                reverse=True
            )
            
            logger.info(f"Got {len(sorted_results)} top matches for job {job_id}")
            return sorted_results[:limit]
            
        except Exception as e:
            logger.error(f"Error getting top candidate matches: {e}")
            return []  
             
    def search_candidates_hybrid(
        self,
        query_text: str,
        location: str = None,
        status: str = None,
        limit: int = 10,
        threshold: float = 0.7
    ) -> List[Dict]:
        """
        Hybrid search combining vector similarity with metadata filters.
        
        Args:
            query_text (str): Semantic query
            location (str): Filter by location
            status (str): Filter by status
            limit (int): Maximum results
            threshold (float): Similarity threshold
            
        Returns:
            Candidates matching both vector and metadata criteria
            
        Example:
            >>> candidates = retrieval.search_candidates_hybrid(
            >>>     "Python developer",
            >>>     location="San Francisco",
            >>>     status="active",
            >>>     limit=10
            >>> )
        """
        try:
            queries = get_vector_queries(similarity_threshold=threshold)
            
            results = queries.hybrid_search_candidates(
                query_text,
                location=location,
                status=status,
                limit=limit,
                threshold=threshold
            )
            
            logger.info(f"Hybrid search found {len(results)} candidates")
            return results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
        

    def get_candidates_by_required_skills(
        self,
        skill_names: List[str],
        match_percentage: float = 0.8,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find candidates with required skills.
        
        Args:
            skill_names (List[str]): Required skills
            match_percentage (float): Required match percentage (0-1)
            limit (int): Maximum results
            
        Returns:
            Candidates with matching skills
            
        Example:
            >>> candidates = retrieval.get_candidates_by_required_skills(
            >>>     ["Python", "JavaScript", "React"],
            >>>     match_percentage=0.8,
            >>>     limit=10
            >>> )
        """
        try:
            queries = get_vector_queries()
            
            results = queries.find_candidates_by_skills(
                skill_names,
                match_percentage=match_percentage,
                limit=limit
            )
            
            logger.info(f"Found {len(results)} candidates with required skills")
            return results
            
        except Exception as e:
            logger.error(f"Error getting candidates by skills: {e}")
            return []


            
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
        if 'jobreq_id' in kwargs and kwargs['jobreq_id'] is not None:
            nodes.append('(c:Candidate)-[:APPLIED_FOR]->(j:JobReq)')
        if 'skills' in kwargs and kwargs['skills'] is not None:
            nodes.append('(c:Candidate)-[:HAS_SKILL]->(s:Skill)')
        if 'company' in kwargs and kwargs['company'] is not None:
            nodes.append('(c:Candidate)-[:WORKED_AT]->(co:Company)')
        if 'education' in kwargs and kwargs['education'] is not None:
            nodes.append('(c:Candidate)-[:HAS_EDUCATION]->(e:Education)')
        if 'industry' in kwargs and kwargs['industry'] is not None:
            nodes.append('(c:Candidate)-[:WORKED_AT]->(co:Company)-[:IN_INDUSTRY]->(i:Industry)')
        if 'role' in kwargs and kwargs['role'] is not None:
            nodes.append('(c:Candidate)-[:HELD_ROLE]->(r:Role)')
        
        query += ', '.join(nodes)
        query += " WHERE "
        conditions = []
        if 'jobreq_id' in kwargs and kwargs['jobreq_id'] is not None:
            conditions.append(f"j.id = '{kwargs['jobreq_id']}'")
        
        # Candidate conditions
        if 'candidate' in kwargs and kwargs['candidate'] is not None:
            if isinstance(kwargs['candidate'], dict):
                if 'name' in kwargs['candidate']:
                    if isinstance(kwargs['candidate']['name'], list):
                        conditions.append(f"c.name IN {kwargs['candidate']['name']}")
                    else:
                        conditions.append(f"c.name = '{kwargs['candidate']['name']}'")
                if 'location' in kwargs['candidate']:
                    if isinstance(kwargs['candidate']['location'], list):
                        conditions.append(f"c.location IN {kwargs['candidate']['location']}")
                    else:
                        conditions.append(f"c.location = '{kwargs['candidate']['location']}'")

        # Skill conditions 
        if 'skills' in kwargs and kwargs['skills'] is not None:
            if isinstance(kwargs['skills'], list):
                skills_conditions = []
                for skill in kwargs['skills']:
                    if isinstance(skill, dict) and skill['name']:
                        skills_conditions.append(f"s.name = '{skill['name']}'")
                if skills_conditions:
                    conditions.append(f"({' OR '.join(skills_conditions)})")
            
            elif isinstance(kwargs['skills'], dict):
                if isinstance(kwargs['skills']['name'], list):
                    conditions.append(f"s.name IN {kwargs['skills']['name']}")
                else:
                    conditions.append(f"s.name = '{kwargs['skills']['name']}'")
                if 'proficiency' in kwargs['skills']:
                    if isinstance(kwargs['skills']['proficiency'], list):
                        conditions.append(f"s.proficiency IN {kwargs['skills']['proficiency']}")
                    else:
                        conditions.append(f"s.proficiency = '{kwargs['skills']['proficiency']}'")
                
                if 'category' in kwargs['skills']:
                    if isinstance(kwargs['skills']['category'], list):
                        conditions.append(f"s.category IN {kwargs['skills']['category']}")
                    else:
                        conditions.append(f"s.category = '{kwargs['skills']['category']}'")

        # Company conditions
        if 'company' in kwargs and kwargs['company'] is not None:
            if isinstance(kwargs['company'], list):
                company_conditions = []
                for company in kwargs['company']:
                    if isinstance(company, dict) and company['name']:
                        company_conditions.append(f"co.name = '{company['name']}'")
                    if isinstance(company, dict) and company['sector']:
                        company_conditions.append(f"co.sector = '{company['sector']}'")
                    if isinstance(company, dict) and company['size']:
                        company_conditions.append(f"co.size = '{company['size']}'")
                    if isinstance(company, dict) and company['stage']:
                        company_conditions.append(f"co.stage = '{company['stage']}'")
                if company_conditions:
                    conditions.append(f"({' OR '.join(company_conditions)})")

            elif isinstance(kwargs['company'], dict):
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
        if 'education' in kwargs and kwargs['education'] is not None:
            if isinstance(kwargs['education'], list):   
                education_conditions = []
                for education in kwargs['education']:
                    if isinstance(education, dict) and education['name']:
                        education_conditions.append(f"e.name = '{education['name']}'")
                    if isinstance(education, dict) and education['degree']:
                        education_conditions.append(f"e.degree = '{education['degree']}'")
                    if isinstance(education, dict) and education['year']:
                        education_conditions.append(f"e.year >= '{education['year']}'")
                    if isinstance(education, dict) and education['gpa']:
                        education_conditions.append(f"e.gpa >= '{education['gpa']}'")
                if education_conditions:
                    conditions.append(f"({' OR '.join(education_conditions)})")

            elif isinstance(kwargs['education']['name'], list):
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
        if 'industry' in kwargs and kwargs['industry'] is not None:
            if isinstance(kwargs['industry'], list):
                industry_conditions = []
                for industry in kwargs['industry']:
                    if isinstance(industry, dict) and industry['industry_name']:
                        industry_conditions.append(f"i.name = '{industry['industry_name']}'")
                    if isinstance(industry, dict) and industry['subsector']:
                        industry_conditions.append(f"i.subsector = '{industry['subsector']}'")
                    if isinstance(industry, dict) and industry['regulation']:
                        industry_conditions.append(f"i.regulation = '{industry['regulation']}'")
                if industry_conditions:
                    conditions.append(f"({' OR '.join(industry_conditions)})")
            elif isinstance(kwargs['industry'], dict):
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
        if 'role' in kwargs and  kwargs['role'] is not None:
            if isinstance(kwargs['role'], list):
                role_conditions = []
                for role in kwargs['role']:
                    if isinstance(role, dict) and role['title']:
                        role_conditions.append(f"r.title = '{role['title']}'")
                    if isinstance(role, dict) and role['domain']:
                        role_conditions.append(f"r.domain = '{role['domain']}'")
                if role_conditions:
                    conditions.append(f"({' OR '.join(role_conditions)})")  
            elif isinstance(kwargs['role'], dict):
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
            return query
        except Exception as e:
            logger.error(f"Error building retrieval query: {e}")
            raise CustomException(f"Error building retrieval query: {e}")
    
    
    def retrieve(self, query, job_req_id=None, n_results=10):
        "Builds a Cypher query based on the provided information and runs it on the Neo4j database."
        try:
            logger.info(f"Running retrieval for query: {query} with job_req_id: {job_req_id} and n_results: {n_results}")
            result = self.get_top_candidate_matches(job_req_id, query_text=query, limit=n_results)
            return result
        except Exception as e:
            logger.error(f"Error retrieving data: {e}")
            raise CustomException(f"Error retrieving data: {e}")