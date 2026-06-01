from pydantic import BaseModel, Field
from typing import Annotated, Optional

def merge_dicts(left: dict, right: dict) -> dict:
    for key in set(left.keys()).union(right.keys()):
        if key in left and key in right:
            if isinstance(left[key], dict) and isinstance(right[key], dict):
                left[key] = merge_dicts(left[key], right[key])
            elif isinstance(left[key], list) and isinstance(right[key], list):
                left[key] = left[key] + right[key]
            else:
                left[key] = right[key]
        elif key in right:
            left[key] = right[key]
    return left

def merge_lists(left: list, right: list) -> list:
    """Concatenate lists for parallel node updates"""
    if left is None:
        left = []
    if right is None:
        right = []
    return left + (right if isinstance(right, list) else [right])

def add(left, right):   
    return right

class RetrievalGraph(BaseModel):
    query: Annotated[Optional[str], add] = None
    preprocessed_query: Annotated[Optional[str], add] = None
    top_k: Annotated[int, add] = 5
    job_req_id: Annotated[str, add] = 'resumes'
    retrieved_chunks_BM25: Annotated[list, merge_lists] = Field(default_factory=list)
    retrieved_chunks_Embedding: Annotated[list, merge_lists] = Field(default_factory=list)
    retrieved_data_graph: Annotated[list, merge_lists] = Field(default_factory=list)
    ranking_score: Annotated[dict, merge_dicts] = Field(default_factory=dict)
    final_results: Annotated[list, merge_lists] = Field(default_factory=list)