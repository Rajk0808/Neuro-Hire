from apps.backend.app.agents.Resume_Intelligence_agent.database.clients import neo4j_client
from apps.backend.app.agents.Resume_Intelligence_agent.services.embedding_service import get_embedding_service
import logging
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class VectorSimilarityQueries:
    """
    Service for performing vector similarity searches in Neo4j.
    Provides semantic search capabilities for all entity types.
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize the vector similarity queries service.
        
        Args:
            similarity_threshold (float): Default similarity score threshold (0.0-1.0)
        """
        self.driver = neo4j_client
        self.embedding_service = get_embedding_service()
        self.similarity_threshold = similarity_threshold
        logger.info(f"Initialized VectorSimilarityQueries with threshold: {similarity_threshold}")
    
    def _run_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a query and return results."""
        with self.driver.session() as session:
            result = session.run(query, params or {})
            return [record.data() for record in result]
    
    def find_similar_candidates(
        self, 
        query_text: str, 
        limit: int = 10,
        threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Find candidates similar to the query text based on embeddings.
        
        Args:
            query_text (str): Text to search for (e.g., "Senior Python Developer from SF")
            limit (int): Maximum number of results
            threshold (float): Similarity threshold override
            
        Returns:
            List of candidates with similarity scores, sorted by similarity
            
        Example:
            >>> queries = VectorSimilarityQueries()
            >>> results = queries.find_similar_candidates("Python developer", limit=5)
            >>> for result in results:
            >>>     print(f"{result['name']}: {result['similarity']:.2f}")
        """
        try:
            threshold = threshold or self.similarity_threshold
            try:
                query_embedding = self.embedding_service.embed_text(query_text)
            except ValueError as e:
                logger.error(f"Embedding generation failed: {e}")
                raise
            
            cypher_query = f"""
                // 1. Fast Retrieval: Leverage the index to grab the top candidates instantly
                MATCH (c:Candidate)
                SEARCH c IN (
                  VECTOR INDEX candidate_embeddings 
                  FOR $query_embedding 
                  LIMIT 100
                ) SCORE AS similarity
                WHERE similarity > {threshold}
                
                // 2. Return results and extract relationships ONLY for the top matches
                RETURN 
                    c.id AS candidate_id,
                    c.name AS name,
                    c.location AS location,
                    c.status AS status,
                    similarity,
                    [(c)-[:HAS_SKILL]->(s:Skill) | s.name] AS skills,
                    [(c)-[:HELD_ROLE]->(r:Role) | r.title] AS roles,
                    [(c)-[:WORKED_AT]->(co:Company) | co.name] AS companies
                ORDER BY similarity DESC
                LIMIT {limit}
                """
            
            logger.info(f"Searching for similar candidates to: '{query_text}' with threshold {threshold}")
            results = self._run_query(cypher_query, {"query_embedding": query_embedding})
            logger.info(f"Found {len(results)} similar candidates")
            return results
            
        except ValueError as e:
            logger.error(f"Error finding similar candidates: {e}")
            raise
        except Exception as e:
            logger.error(f"Error finding similar candidates: {e}")
            raise
    
    def find_similar_skills(
        self,
        query_text: str,
        limit: int = 10,
        threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Find skills similar to the query text.
        
        Args:
            query_text (str): Skill to search for
            limit (int): Maximum results
            threshold (float): Similarity threshold override
            
        Returns:
            List of skills with similarity scores
            
        Example:
            >>> results = queries.find_similar_skills("Python programming", limit=5)
        """
        try:
            threshold = threshold or self.similarity_threshold
            query_embedding = self.embedding_service.embed_text(query_text)
        
            cypher_query = f"""
            // 1. Fast Retrieval: Instantly grab closest skills using the vector index
            MATCH (s:Skill)
            SEARCH s IN (
              VECTOR INDEX skill_embeddings
              FOR $query_embedding 
              LIMIT 100
            ) SCORE AS similarity
            WHERE similarity > {threshold}
            
            // 2. Safely match candidates who have these specific top skills
            OPTIONAL MATCH (c:Candidate)-[:HAS_SKILL]->(s)
            
            // 3. Aggregate and count candidates per skill
            WITH s, similarity, COUNT(DISTINCT c) AS candidates_with_skill
            
            RETURN
                s.name AS skill_name,
                s.category AS category,
                s.proficiency AS proficiency,
                similarity,
                candidates_with_skill
            ORDER BY similarity DESC
            LIMIT {limit}
            """
            
            logger.info(f"Searching for similar skills to: '{query_text}'")
            results = self._run_query(cypher_query, {"query_embedding": query_embedding})
            logger.info(f"Found {len(results)} similar skills")
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar skills: {e}")
            raise
    
    def find_similar_roles(
        self,
        query_text: str,
        limit: int = 10,
        threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Find roles similar to the query text.
        
        Args:
            query_text (str): Role to search for
            limit (int): Maximum results
            threshold (float): Similarity threshold override
            
        Returns:
            List of roles with similarity scores
            
        Example:
            >>> results = queries.find_similar_roles("Machine Learning Engineer", limit=5)
        """
        try:
            threshold = threshold or self.similarity_threshold
            query_embedding = self.embedding_service.embed_text(query_text)
            
            cypher_query = f"""
            // 1. Fast Retrieval: Instantly grab the closest roles using the vector index
            MATCH (r:Role)
            SEARCH r IN (
              VECTOR INDEX role_embeddings 
              FOR $query_embedding 
              LIMIT 100
            ) SCORE AS similarity
            WHERE similarity > {threshold}
            
            // 2. Safely match candidates who have held these specific top roles
            OPTIONAL MATCH (c:Candidate)-[:HELD_ROLE]->(r)
            
            // 3. Aggregate and count candidates per role
            WITH r, similarity, COUNT(DISTINCT c) AS candidates_with_role
            
            RETURN
                r.title AS role_title,
                r.domain AS domain,
                r.seniority AS seniority,
                similarity,
                candidates_with_role
            ORDER BY similarity DESC
            LIMIT {limit}
           """
            
            logger.info(f"Searching for similar roles to: '{query_text}'")
            results = self._run_query(cypher_query, {"query_embedding": query_embedding})
            logger.info(f"Found {len(results)} similar roles")
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar roles: {e}")
            raise
    
    def find_similar_companies(
        self,
        query_text: str,
        limit: int = 10,
        threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Find companies similar to the query text.
        
        Args:
            query_text (str): Company to search for
            limit (int): Maximum results
            threshold (float): Similarity threshold override
            
        Returns:
            List of companies with similarity scores
            
        Example:
            >>> results = queries.find_similar_companies("Tech startup in Silicon Valley", limit=5)
        """
        try:
            threshold = threshold or self.similarity_threshold
            query_embedding = self.embedding_service.embed_text(query_text)
            
            cypher_query = f"""
            // 1. Fast Retrieval: Leverage the vector index to grab the top companies instantly
            MATCH (co:Company)
            SEARCH co IN (
              VECTOR INDEX company_embeddings 
              FOR $query_embedding 
              LIMIT 100
            ) SCORE AS similarity
            WHERE similarity > {threshold}
            
            // 2. Safely match candidates who have worked at these specific top companies
            OPTIONAL MATCH (c:Candidate)-[:WORKED_AT]->(co)
            
            // 3. Aggregate and count candidates per company
            WITH co, similarity, COUNT(DISTINCT c) AS candidates_worked_here
            
            RETURN
                co.name AS company_name,
                co.sector AS sector,
                co.stage AS stage,
                co.size AS size,
                similarity,
                candidates_worked_here
            ORDER BY similarity DESC
            LIMIT {limit}
            """    
            
            logger.info(f"Searching for similar companies to: '{query_text}'")
            results = self._run_query(cypher_query, {"query_embedding": query_embedding})
            logger.info(f"Found {len(results)} similar companies")
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar companies: {e}")
            raise
    
    def hybrid_search_candidates(
        self,
        query_text: str,
        location: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 10,
        threshold: Optional[float] = None,
        location_weight: float = 0.2
    ) -> List[Dict]:
        """
        Hybrid search combining vector similarity with metadata filters.
        Useful for finding candidates with specific attributes.
        
        Args:
            query_text (str): Semantic query (e.g., "Senior backend engineer")
            location (str): Filter by location
            status (str): Filter by status (e.g., "active", "inactive")
            limit (int): Maximum results
            threshold (float): Similarity threshold override
            location_weight (float): How much to boost exact location matches (0.0-1.0)
            
        Returns:
            List of candidates matching both vector and metadata filters
            
        Example:
            >>> results = queries.hybrid_search_candidates(
            >>>     "Python developer",
            >>>     location="San Francisco",
            >>>     status="active",
            >>>     limit=5
            >>> )
        """
        try:
            threshold = threshold or self.similarity_threshold
            query_embedding = self.embedding_service.embed_text(query_text)
            
            # Build filter conditions
            filters = "WHERE c.embedding_vector IS NOT NULL"
            if location:
                filters += " AND c.location = $location"
            if status:
                filters += " AND c.status = $status"
            
            # Build location boost clause only if location is provided
            if location:
                location_boost_clause = f"CASE WHEN c.location = $location THEN {location_weight} ELSE 0 END"
            else:
                location_boost_clause = "0"
            
            cypher_query = f"""
            MATCH (c:Candidate)
            {filters}
            WITH c, gds.similarity.cosine($query_embedding, c.embedding_vector) AS similarity
            WHERE similarity > {threshold}
            WITH c, similarity, {location_boost_clause} AS location_boost
            WITH c, similarity + location_boost AS final_score
            RETURN
                c.id AS candidate_id,
                c.name AS name,
                c.location AS location,
                c.status AS status,
                final_score AS score,
                [(c)-[:HAS_SKILL]->(s:Skill) | s.name] AS skills,
                [(c)-[:HELD_ROLE]->(r:Role) | r.title] AS roles
            ORDER BY final_score DESC
            LIMIT {limit}
            """
            
            params = {"query_embedding": query_embedding}
            if location:
                params["location"] = location
            if status:
                params["status"] = status.lower()
            
            logger.info(f"Hybrid search for candidates: query='{query_text}', location={location}, status={status}")
            results = self._run_query(cypher_query, params)
            logger.info(f"Found {len(results)} candidates matching hybrid criteria")
            return results
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            return []
    
    def semantic_job_match(
        self,
        jobreq_id: str,
        limit: int = 20,
        threshold: Optional[float] = None
    ) -> List[Dict]:
        """
        Find candidates that semantically match a job requirement.
        
        Args:
            jobreq_id (str): Job requirement ID
            limit (int): Maximum candidates to return
            threshold (float): Similarity threshold override
            
        Returns:
            List of candidates ranked by match score
            
        Example:
            >>> results = queries.semantic_job_match("job_123", limit=10)
            >>> for result in results:
            >>>     print(f"{result['name']}: match_score={result['match_score']:.2f}")
        """
        try:
            threshold = threshold or self.similarity_threshold
            
            # First, fetch the job requirement to get its embedding
            fetch_job_query = "MATCH (j:JobReq {id: $jobreq_id}) RETURN j.embedding_vector AS embedding"
            job_result = self._run_query(fetch_job_query, {"jobreq_id": jobreq_id})
            
            if not job_result or not job_result[0].get('embedding'):
                logger.warning(f"Job requirement {jobreq_id} not found or has no embedding")
                raise ValueError(f"Job requirement {jobreq_id} has no valid embedding")
            
            job_embedding = job_result[0]['embedding']
            
            # Validate job embedding
            if isinstance(job_embedding, list) and all(v == 0.0 for v in job_embedding):
                logger.error(f"Job requirement {jobreq_id} has invalid zero vector embedding")
                raise ValueError(f"Job requirement {jobreq_id} has invalid embedding (zero vector)")
            
            cypher_query = f"""
            MATCH (j:JobReq {{id: $jobreq_id}})
            WHERE j.embedding_vector IS NOT NULL
            
            // 1. Fast Retrieval: Quickly grab closest candidates using the vector index
            MATCH (c:Candidate)
            SEARCH c IN (
              VECTOR INDEX candidate_embeddings
              FOR j.embedding_vector 
              LIMIT 100
            ) SCORE AS similarity
            WHERE similarity > {threshold}
            
            // 2. Calculate additional match score based on shared skills/roles
            OPTIONAL MATCH (j)<-[:REQUIRED_FOR]-(req_skill:Skill)
            OPTIONAL MATCH (c)-[:HAS_SKILL]->(cand_skill:Skill)
            WITH j, c, similarity,
                 COUNT(DISTINCT req_skill) AS required_skills_count,
                 COUNT(DISTINCT CASE WHEN req_skill.name = cand_skill.name THEN cand_skill END) AS matched_skills
            
            // 3. Calculate final match score
            WITH j, c, similarity, required_skills_count, matched_skills,
                 CASE WHEN required_skills_count > 0 
                      THEN TOFLOAT(matched_skills) / required_skills_count 
                      ELSE 0.0 
                 END AS skill_match_ratio
            
            WITH c, (similarity * 0.7 + skill_match_ratio * 0.3) AS match_score
            RETURN
                c.id AS candidate_id,
                c.name AS name,
                c.location AS location,
                match_score,
                [(c)-[:HAS_SKILL]->(s:Skill) | s.name] AS skills,
                [(c)-[:WORKED_AT]->(co:Company) | co.name] AS companies
            ORDER BY match_score DESC
            LIMIT {limit}
            """
            
            logger.info(f"Finding semantic matches for job requirement: {jobreq_id}")
            results = self._run_query(cypher_query, {"jobreq_id": jobreq_id})
            logger.info(f"Found {len(results)} candidate matches")
            return results
            
        except ValueError as e:
            logger.error(f"Error in semantic job match: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in semantic job match: {e}")
            raise
    
    def find_candidates_by_skills(
        self,
        skill_names: List[str],
        match_percentage: float = 0.8,
        limit: int = 10
    ) -> List[Dict]:
        """
        Find candidates that have a certain percentage of required skills.
        
        Args:
            skill_names (List[str]): List of required skills
            match_percentage (float): Required match percentage (0.0-1.0)
            limit (int): Maximum results
            
        Returns:
            List of candidates with skill match information
            
        Example:
            >>> results = queries.find_candidates_by_skills(
            >>>     ["Python", "JavaScript", "React"],
            >>>     match_percentage=0.8,
            >>>     limit=5
            >>> )
        """
        try:
            required_count = len(skill_names)
            min_match_count = int(required_count * match_percentage)
            
            cypher_query = f"""
            // 1. Start from the specific target skills (uses index lookup)
            MATCH (s:Skill)
            WHERE s.name IN $skill_names
            
            // 2. Traversal travels backward to only relevant candidates
            MATCH (c:Candidate)-[:HAS_SKILL]->(s)
            
            // 3. Aggregate and filter early
            WITH c, COUNT(DISTINCT s) AS matched_skills_count
            WHERE matched_skills_count >= {min_match_count}
            
            // 4. Return results and extract full skill lists only for the top matches
            RETURN
                c.id AS candidate_id,
                c.name AS name,
                c.location AS location,
                matched_skills_count AS matched_skills,
                {required_count} AS required_skills,
                ROUND(100.0 * matched_skills_count / {required_count}) AS match_percentage,
                [(c)-[:HAS_SKILL]->(all_s:Skill) | all_s.name] AS all_skills
            ORDER BY matched_skills_count DESC
            LIMIT {limit}
            """
            
            logger.info(f"Finding candidates with {match_percentage*100:.0f}% of skills: {skill_names}")
            results = self._run_query(cypher_query, {"skill_names": skill_names})
            logger.info(f"Found {len(results)} candidates with matching skills")
            return results
            
        except Exception as e:
            logger.error(f"Error finding candidates by skills: {e}")
            raise
    
    def batch_similarity_search(
        self,
        query_texts: List[str],
        entity_type: str = "Candidate",
        limit: int = 5,
        threshold: Optional[float] = None
    ) -> Dict[str, List[Dict]]:
        """
        Perform multiple similarity searches in batch.
        
        Args:
            query_texts (List[str]): List of queries
            entity_type (str): Type of entity to search ("Candidate", "Skill", "Role", "Company")
            limit (int): Maximum results per query
            threshold (float): Similarity threshold override
            
        Returns:
            Dictionary mapping query to results
            
        Example:
            >>> queries_list = ["Python developer", "JavaScript developer"]
            >>> results = queries.batch_similarity_search(queries_list, "Candidate")
            >>> for query, matches in results.items():
            >>>     print(f"Query: {query}, Found: {len(matches)} matches")
        """
        try:
            results = {}
            
            if entity_type == "Candidate":
                for query_text in query_texts:
                    results[query_text] = self.find_similar_candidates(query_text, limit, threshold)
            elif entity_type == "Skill":
                for query_text in query_texts:
                    results[query_text] = self.find_similar_skills(query_text, limit, threshold)
            elif entity_type == "Role":
                for query_text in query_texts:
                    results[query_text] = self.find_similar_roles(query_text, limit, threshold)
            elif entity_type == "Company":
                for query_text in query_texts:
                    results[query_text] = self.find_similar_companies(query_text, limit, threshold)
            else:
                logger.error(f"Unknown entity type: {entity_type}")
                raise ValueError(f"Unknown entity type: {entity_type}")
            
            logger.info(f"Completed batch search for {len(query_texts)} queries")
            return results
            
        except Exception as e:
            logger.error(f"Error in batch similarity search: {e}")
            raise


# Singleton pattern for easy access
_vector_queries_instance = None

def get_vector_queries(similarity_threshold: float = 0.7) -> VectorSimilarityQueries:
    """
    Get or create a singleton instance of VectorSimilarityQueries.
    
    Args:
        similarity_threshold (float): Default similarity threshold
        
    Returns:
        VectorSimilarityQueries instance
        
    Example:
        >>> queries = get_vector_queries()
        >>> results = queries.find_similar_candidates("Senior developer")
    """
    global _vector_queries_instance
    if _vector_queries_instance is None:
        _vector_queries_instance = VectorSimilarityQueries(similarity_threshold)
    return _vector_queries_instance