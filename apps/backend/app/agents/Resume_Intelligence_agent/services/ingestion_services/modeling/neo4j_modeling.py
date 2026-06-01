
from apps.backend.app.agents.Resume_Intelligence_agent.services.ingestion_services.StateGraph import IngestionGraph
from apps.backend.app.agents.Resume_Intelligence_agent.database.schemas import *
from CustomException import CustomException
import logging
import uuid
logger = logging.getLogger(__name__)

class Neo4jModeling:
    def model(self, StateGraph: IngestionGraph):
        """
        Model the extracted resume data into a Neo4j graph database.
        Args:
            StateGraph (IngestionGraph): The state graph containing the extracted information from resumes.
        """
        
        candidates_data = []
        logger.info("Modeling data for Neo4j...")
        try:
            # Handle both dict and object access
            llm_response = StateGraph.get("llm_response", {}) if isinstance(StateGraph, dict) else getattr(StateGraph, 'llm_response', {})
            
            for candidate in llm_response.values():
                # Extract candidate data, handling both dict and object access
                if isinstance(candidate, dict):
                    logger.info(f"Processing candidate Dict: {candidate.get('name', 'Unknown')}")
                    name = candidate.get('name', '')
                    email = candidate.get('email', '')
                    phones = candidate.get('phones', [])
                    status = candidate.get('status', True)
                    location = candidate.get('location', '')
                    skills = candidate.get('skills', [])
                    experience = candidate.get('experience', [])
                    education = candidate.get('education', [])
                else:
                    logger.info(f"Processing candidate Object: {getattr(candidate, 'name', 'Unknown')}")
                    name = getattr(candidate, 'name', '')
                    email = getattr(candidate, 'email', '')
                    phones = getattr(candidate, 'phones', [])
                    status = getattr(candidate, 'status', True)
                    location = getattr(candidate, 'location', '')
                    skills = getattr(candidate, 'skills', [])
                    experience = getattr(candidate, 'experience', [])
                    education = getattr(candidate, 'education', [])
                candidate_data = Candidate_data(
                    id=str(uuid.uuid4()),
                    name=name,
                    contact_info=[email, *phones],
                    status=status,
                    location=location,
                    skills=[Skill_node(name=skill.get('name', ''), category=skill.get('category', ''), proficiency=skill.get('proficiency', 'good')) for skill in skills],
                    roles=[Role_node(title=role.get('title', ''), seniority=role.get('seniority', 'mid-level'), domain=role.get('domain', '')) for role in experience],
                    companies=[exp.get('company', {}) for exp in experience if 'company' in exp],
                    education=[Education_node(degree=edu.get('degree', ''), institution=edu.get('institution', ''), year=edu.get('year', ''), gpa=edu.get('gpa', '')) for edu in education],
                )
                candidates_data.append(candidate_data)
            
            # Update StateGraph with candidates_data
            if isinstance(StateGraph, dict):
                logger.info("Updating StateGraph as dict with candidates_data in Dict format")
                StateGraph['candidates_data'] = candidates_data
            else:
                logger.info("Updating StateGraph as object with candidates_data in List format")
                setattr(StateGraph, 'candidates_data', candidates_data)
            
            logger.info(f"Finished modeling data for Neo4j. Processed {len(candidates_data)} candidates.")
        except Exception as e:
            logger.error(f"Error modeling data for Neo4j: {str(e)}")
            raise CustomException(f"Error modeling data for Neo4j: {str(e)}")
        return StateGraph
    