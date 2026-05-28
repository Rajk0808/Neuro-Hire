from pydantic import BaseModel, Field
from typing import Annotated
from agents.Resume_Intelligence_agent.database.schemas.neo4j_schema import *
def merge_dicts(left: dict, right: dict) -> dict:
    return {**left, **right}

def add(left, right):
    return right

class IngestionGraph(BaseModel):
    file_path : Annotated[str,add] = 'resumes/'
    mode : Annotated[str,add] = 'hybrid'
    workers : Annotated[int,add] = 4
    text : Annotated[dict, merge_dicts] = {}
    llm_response : Annotated[dict, merge_dicts] = {}
    chunk_size : Annotated[int,add] = 512
    chunk_overlap : Annotated[int,add] = 25
    index_name : Annotated[str,add] = 'resumes'    
    candidates_data : Annotated[list[Candidate_data], add] = [Candidate_data()]
    jobreq_data : Annotated[JobReq_node, add] = JobReq_node()
