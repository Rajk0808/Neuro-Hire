from apps.backend.app.agents.Resume_Intelligence_agent.database.clients import neo4j_client
from apps.backend.app.agents.Resume_Intelligence_agent.database.schemas import *
from apps.backend.app.agents.Resume_Intelligence_agent.services.ingestion_services.StateGraph.IngestionGraph import IngestionGraph
from apps.backend.app.agents.Resume_Intelligence_agent.services.embedding_service import get_embedding_service
import logging
from CustomException import CustomException as CustomException
logger = logging.getLogger(__name__)

def run_query(query : str, driver):
    "Runs query on Neo4j database using the provided driver."
    with driver.session() as session:
        result = session.run(query)
        return result
    
    
class insert_to_neo4j:
    def __init__(self):
        self.driver = neo4j_client
        self.embedding_service = get_embedding_service()
        logger.info("Initialized Neo4j insertion service with driver and embedding service.")
    
    def create_constraints(self):
        logger.info("Creating constraints in Neo4j...")
       
        JOBREQ_CONSTRAINT = "CREATE CONSTRAINT FOR (n:JobReq) REQUIRE n.id IS UNIQUE;"
        CANDIDATE_CONSTRAINT = "CREATE CONSTRAINT FOR (n:Candidate) REQUIRE n.id IS UNIQUE;"
        SKILL_CONSTRAINT = "CREATE CONSTRAINT FOR (n:Skill) REQUIRE n.name IS UNIQUE;"
        ROLE_CONSTRAINT = "CREATE CONSTRAINT FOR (n:Role) REQUIRE n.title IS UNIQUE;"
        EXPERIENCE_CONSTRAINT = "CREATE CONSTRAINT FOR (n:Experience) REQUIRE n.id IS UNIQUE;"
        INDUSTRY_CONSTRAINT = "CREATE CONSTRAINT FOR (n:Industry) REQUIRE n.name IS UNIQUE;"
        constraints = [
            JOBREQ_CONSTRAINT,
            CANDIDATE_CONSTRAINT,
            SKILL_CONSTRAINT,
            ROLE_CONSTRAINT,
            EXPERIENCE_CONSTRAINT,
            INDUSTRY_CONSTRAINT
        ]
        for constraint in constraints:
                try:
                    run_query(constraint, self.driver)
                    print(f"Created constraint: {constraint}")
                except Exception as e:
                    # Check if it's a constraint existence error
                    if "AlreadyExists" in str(e) or "EquivalentConstraint" in str(e):
                        print("Constraint already exists, skipping...")
                    else:
                        raise CustomException(f"Failed to create constraint: {constraint}. Error: {str(e)}")
        
        # Create vector indexes for semantic search
        logger.info("Creating vector indexes...")
        
        vector_indexes = [
            """
            CREATE VECTOR INDEX candidate_embeddings IF NOT EXISTS
            FOR (c:Candidate) ON c.embedding_vector
            OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """,
            """
            CREATE VECTOR INDEX skill_embeddings IF NOT EXISTS
            FOR (s:Skill) ON s.embedding_vector
            OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """,
            """
            CREATE VECTOR INDEX role_embeddings IF NOT EXISTS
            FOR (r:Role) ON r.embedding_vector
            OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """,
            """
            CREATE VECTOR INDEX company_embeddings IF NOT EXISTS
            FOR (co:Company) ON co.embedding_vector
            OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """,
            """
            CREATE VECTOR INDEX industry_embeddings IF NOT EXISTS
            FOR (i:Industry) ON i.embedding_vector
            OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """,
            """
            CREATE VECTOR INDEX jobreq_embeddings IF NOT EXISTS
            FOR (j:JobReq) ON j.embedding_vector
            OPTIONS {indexConfig: {`vector.dimensions`: 384, `vector.similarity_function`: 'cosine'}}
            """
        ]
        
        for idx_query in vector_indexes:
            try:
                run_query(idx_query, self.driver)
                logger.info("Created vector index")
            except Exception as e:
                if "AlreadyExists" in str(e) or "EquivalentConstraint" in str(e):
                    logger.info("Vector index already exists, skipping...")
                else:
                    logger.warning(f"Failed to create vector index: {e}")


    def insert_jobreq(self, jobreq_data: JobReq_node):
        try:    
            jobreq_id = jobreq_data['id'] if isinstance(jobreq_data, dict) else jobreq_data.id
            status = str(jobreq_data['status'] if isinstance(jobreq_data, dict) else jobreq_data.status).lower()
            posted_date = jobreq_data['posted_date'] if isinstance(jobreq_data, dict) else jobreq_data.posted_date
            title = jobreq_data['title'] if isinstance(jobreq_data, dict) else jobreq_data.title
            description = jobreq_data['description'] if isinstance(jobreq_data, dict) else jobreq_data.description
            
            embedding_vector = self.embedding_service.embed_text(f"{title} {description}")
            
            logger.info(f"Inserting job requirement with ID: {jobreq_id} into Neo4j...")
            query = f"""
            MERGE (j:JobReq {{id: '{jobreq_id}'}})
            SET j.status = {status},
                j.posted_date = '{posted_date}',
                j.title = '{title}',
                j.description = '{description}',
                j.embedding_vector = {embedding_vector}
            """           
            run_query(query, self.driver)
        except Exception as e:
            logger.error(f"Failed to insert job requirement with ID: {jobreq_data['id'] if isinstance(jobreq_data, dict) else jobreq_data.id}. Error: {str(e)}")
            raise CustomException(f"Failed to insert job requirement with ID: {jobreq_data['id'] if isinstance(jobreq_data, dict) else jobreq_data.id}. Error: {str(e)}")

    def insert_candidate(self, candidate_data: Candidate_node, jobreq_id: str):
        try:
            logger.info(f"Inserting candidate with ID: {candidate_data['id'] if isinstance(candidate_data, dict) else candidate_data.id} into Neo4j...")
            if candidate_data.contact_info is None:
                contact_info_str = ''
            elif candidate_data.contact_info and isinstance(candidate_data.contact_info, list):
                contact_info_str = ""
                for info in candidate_data.contact_info:
                    if isinstance(info, str):
                        contact_info_str += info + ", "
                    else:
                        contact_info_str += ""
            else:
                contact_info_str = ''
            text_for_embedding = f"{candidate_data['name'] if isinstance(candidate_data, dict) else candidate_data.name} {candidate_data['location'] if isinstance(candidate_data, dict) else candidate_data.location}"
            embedding_vector = self.embedding_service.embed_text(text_for_embedding)
            query = f"""
                MERGE (c:Candidate {{id: '{candidate_data['id'] if isinstance(candidate_data, dict) else candidate_data.id}'}})
                SET c.name = '{candidate_data['name'] if isinstance(candidate_data, dict) else candidate_data.name}',
                    c.contact_info = '{contact_info_str}',
                    c.status = {str(candidate_data['status'] if isinstance(candidate_data, dict) else candidate_data.status).lower()},
                    c.location = '{candidate_data['location'] if isinstance(candidate_data, dict) else candidate_data.location}',
                    c.embedding_vector = {embedding_vector}
                MATCH (j:JobReq {{id: '{jobreq_id}'}})
                MERGE (c)-[:APPLIED_TO]->(j)
                """
            run_query(query, self.driver)
        except Exception as e:
            logger.error(f"Failed to insert candidate with ID: {candidate_data['id'] if isinstance(candidate_data, dict) else candidate_data.id}. Error: {str(e)}")
            raise CustomException(f"Failed to insert candidate with ID: {candidate_data['id'] if isinstance(candidate_data, dict) else candidate_data.id}. Error: {str(e)}")

    def insert_skill(self, skill_data: Skill_node, candidate_id: str):
        try:
            logger.info(f"Inserting skill with name: {skill_data['name'] if isinstance(skill_data, dict) else skill_data.name} into Neo4j...")
            text_for_embedding = f"{skill_data['name'] if isinstance(skill_data, dict) else skill_data.name}"
            embedding_vector = self.embedding_service.embed_text(text_for_embedding)
            query = f"""
            MERGE (s:Skill {{name: '{skill_data['name'] if isinstance(skill_data, dict) else skill_data.name}'}})
            SET s.category = '{skill_data['category'] if isinstance(skill_data, dict) else skill_data.category}',
            s.proficiency = '{skill_data['proficiency'] if isinstance(skill_data, dict) else skill_data.proficiency}',
            s.embedding_vector = {embedding_vector}
            MATCH (c:Candidate {{id: '{candidate_id}'}})
            MERGE (c)-[:HAS_SKILL]->(s)
            """
            run_query(query, self.driver)
        except Exception as e:
            logger.error(f"Failed to insert skill with name: {skill_data['name'] if isinstance(skill_data, dict) else skill_data.name} for candidate ID: {candidate_id}. Error: {str(e)}")
            raise CustomException(f"Failed to insert skill with name: {skill_data['name'] if isinstance(skill_data, dict) else skill_data.name} for candidate ID: {candidate_id}. Error: {str(e)}")

    def insert_role(self, role_data: Role_node, candidate_id: str, skill_names: str):
        try:
            logger.info(f"Inserting role with title: {role_data['title'] if isinstance(role_data, dict) else role_data.title} into Neo4j...")
            role_title = role_data['title'] if isinstance(role_data, dict) else role_data.title
            domain = role_data['domain'] if isinstance(role_data, dict) else role_data.domain
            embedding_vector = self.embedding_service.embed_text(f"{role_title} {domain}")
            query = f"""
            MERGE (r:Role {{title: '{role_data['title'] if isinstance(role_data, dict) else role_data.title}'}})
            SET r.seniority = '{role_data['seniority'] if isinstance(role_data, dict) else role_data.seniority}',
            r.domain = '{role_data['domain'] if isinstance(role_data, dict) else role_data.domain}',
            r.embedding_vector = {embedding_vector}
            MATCH (c:Candidate {{id: '{candidate_id}'}})
            MERGE (c)-[:HELD_ROLE]->(r)
            MATCH (s:Skill {{name: '{skill_names}'}})
            MERGE (s)-[:REQUIRED_FOR]->(r)
            """
            run_query(query, self.driver)
        except Exception as e:
            logger.error(f"Failed to insert role with title: {role_data['title'] if isinstance(role_data, dict) else role_data.title} for candidate ID: {candidate_id}. Error: {str(e)}")
            raise CustomException(f"Failed to insert role with title: {role_data['title'] if isinstance(role_data, dict) else role_data.title} for candidate ID: {candidate_id}. Error: {str(e)}")

    def insert_company(self, company_data: Company_node, candidate_id: str):
        try:
            logger.info(f"Inserting company with name: {company_data['name'] if isinstance(company_data, dict) else company_data.name} into Neo4j...")
            embedding_vector = self.embedding_service.embed_text(f"{company_data['name'] if isinstance(company_data, dict) else company_data.name}")
            query = f"""
            MERGE (co:Company {{name: '{company_data['name'] if isinstance(company_data, dict) else company_data.name}'}})
            SET co.sector = '{company_data['sector'] if isinstance(company_data, dict) else company_data.sector}',
                co.stage = '{company_data['stage'] if isinstance(company_data, dict) else company_data.stage}',
                co.size = '{company_data['size'] if isinstance(company_data, dict) else company_data.size}',
                co.embedding_vector = {embedding_vector}
            MATCH (c:Candidate {{id: '{candidate_id}'}})
            MERGE (c)-[:WORKED_AT]->(co)
            """
            run_query(query, self.driver)
        except Exception as e:
            logger.error(f"Failed to insert company with name: {company_data['name'] if isinstance(company_data, dict) else company_data.name} for candidate ID: {candidate_id}. Error: {str(e)}")
            raise CustomException(f"Failed to insert company with name: {company_data['name'] if isinstance(company_data, dict) else company_data.name} for candidate ID: {candidate_id}. Error: {str(e)}")

    
    def insert_industry(self, industry_data: Industry_node, company_name: str):
        try:
            logger.info(f"Inserting industry with name: {industry_data['name'] if isinstance(industry_data, dict) else industry_data.name} into Neo4j...")
            embedding_vector = self.embedding_service.embed_text(f"{industry_data['name'] if isinstance(industry_data, dict) else industry_data.name}")
            query = f"""
            MERGE (i:Industry {{name: '{industry_data['name'] if isinstance(industry_data, dict) else industry_data.name}'}})
            SET i.subsector = '{industry_data['subsector'] if isinstance(industry_data, dict) else industry_data.subsector}',
                i.regulation = '{industry_data['regulation'] if isinstance(industry_data, dict) else industry_data.regulation}',
                i.embedding_vector = {embedding_vector}
            MATCH (co:Company {{name: '{company_name}'}})
            MERGE (co)-[:IN_INDUSTRY]->(i)
            """
            run_query(query, self.driver)
        except Exception as e:
            logger.error(f"Failed to insert industry with name: {industry_data['name'] if isinstance(industry_data, dict) else industry_data.name} for company name: {company_name}. Error: {str(e)}")
            raise CustomException(f"Failed to insert industry with name: {industry_data['name'] if isinstance(industry_data, dict) else industry_data.name} for company name: {company_name}. Error: {str(e)}")
    def insert_education(self, education_data: Education_node, candidate_id : str):
        try:
            logger.info(f"Inserting education with degree: {education_data['degree'] if isinstance(education_data, dict) else education_data.degree} into Neo4j...")
            embedding_vector = self.embedding_service.embed_text(f"{education_data['degree'] if isinstance(education_data, dict) else education_data.degree}")
            query = f"""
            MERGE (e:Education {{degree: '{education_data['degree'] if isinstance(education_data, dict) else education_data.degree}'}})
            SET e.institution = '{education_data['institution'] if isinstance(education_data, dict) else education_data.institution}',
                e.year = '{education_data['year'] if isinstance(education_data, dict) else education_data.year}',
                e.gpa = '{education_data['gpa'] if isinstance(education_data, dict) else education_data.gpa}',
                e.embedding_vector = {embedding_vector}
            MATCH (c:Candidate {{id : '{candidate_id}'}})
            MERGE (c)-[:STUDIED_AT]->(e)
            """
            run_query(query, self.driver)

        except Exception as e:
            logger.error(f"Failed to insert education with degree: {education_data['degree'] if isinstance(education_data, dict) else education_data.degree}. Error: {str(e)}")
            raise CustomException(f"Failed to insert education with degree: {education_data['degree'] if isinstance(education_data, dict) else education_data.degree}. Error: {str(e)}")
    
    def _invoke(self, data : IngestionGraph):
        try:
            self.create_constraints()
            logger.info(f"Inserting job requirement with ID: {data.jobreq_data.id} into Neo4j...")
            self.insert_jobreq(data.jobreq_data)
            for candidate in data.candidates_data:
                logger.info(f"Inserting candidate with ID: {candidate.id} into Neo4j...")
                self.insert_candidate(candidate, data.jobreq_data.id)
                for skill in candidate.skills:
                    logger.info(f"Inserting skill with name: {skill['name'] if isinstance(skill, dict) else skill.name} into Neo4j...")
                    self.insert_skill(skill, candidate.id if isinstance(candidate, dict) else candidate.id)
                for role in candidate.roles:
                    logger.info(f"Inserting role with title: {role['title'] if isinstance(role, dict) else role.title} into Neo4j...")
                    skill_names = []
                    for skill in candidate.skills:
                        skill_names.append(skill['name'] if isinstance(skill, dict) else skill.name)
                        self.insert_role(role, candidate['id'] if isinstance(candidate, dict) else candidate.id, skill.name)
                for company in candidate.companies:
                    logger.info(f"Inserting company with name: {company['name'] if isinstance(company, dict) else company.name} into Neo4j...")
                    self.insert_company(company, candidate['id'] if isinstance(candidate, dict) else candidate.id)
                    logger.info(f"Inserting industry with name: {company['industry'] if isinstance(company, dict) else company.industry} into Neo4j...")
                    self.insert_industry(Industry_node(name=company['industry'] if isinstance(company, dict) else company.industry, subsector=company['sector'] if isinstance(company, dict) else company.sector, regulation=company['regulation'] if isinstance(company, dict) else company.regulation ), company['name'] if isinstance(company, dict) else company.name)
                for education in candidate.education:
                    logger.info(f"Inserting education with degree: {education['degree'] if isinstance(education, dict) else education.degree} into Neo4j...")
                    self.insert_education(Education_node(degree=education['degree'] if isinstance(education, dict) else education.degree, institution=education['institution'] if isinstance(education, dict) else education.institution, year=education['year'] if isinstance(education, dict) else education.year, gpa=education['gpa'] if isinstance(education, dict) else education.gpa), candidate.id)
            self.driver.close()
            logger.info("Finished inserting data into Neo4j.")
        except Exception as e:  
            logger.error(f"Failed to insert data into Neo4j. Error: {str(e)}")
            raise CustomException(f"Failed to insert data into Neo4j. Error: {str(e)}")
