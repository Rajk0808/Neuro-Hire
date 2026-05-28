from langgraph.graph import StateGraph, START, END
from agents.Resume_Intelligence_agent.services.retrival_services.StateGraph.RetrievaGraph import RetrievalGraph


class RetrievalNodes():
    def query_router_node(self, state: RetrievalGraph) -> dict:
        # Read from Pydantic state
        user_query = state.query 
        
        # Determine routing logic here...
        
        # Return updates as a dictionary
        return {"query": user_query}
    
    def preprocessing_node(self, state: RetrievalGraph) -> dict:
        # Process the query
        cleaned_query = state.query.strip().lower()
        
        # Return only the fields that change
        return {"preprocessed_query": 'raj'}
    
    def BM25_retrieval_node(self, state: RetrievalGraph) -> dict:
        # Implement BM25 retrieval
        chunks = ["chunk1", "chunk2"] 
        return {"retrieved_chunks_BM25": chunks}

    def embedding_retrieval_node(self, state: RetrievalGraph) -> dict:
        # Implement embedding retrieval
        chunks = ["chunk3", "chunk4"]
        return {"retrieved_chunks_Embedding": chunks}
    
    def graph_retrieval_node(self, state: RetrievalGraph) -> dict:
        # Implement graph-based retrieval (separate from experience)
        graph_data = [{"source": "graph", "data": "retrieval_result"}]
        return {"retrieved_data_graph": graph_data}
       
    def ranking_node(self, state: RetrievalGraph) -> dict:
        return {"ranking_score": {"score": [1,2,3]}}
    
    def experience_retrieval_node(self, state: RetrievalGraph) -> dict:
        # Retrieve from experience/exemplar memory
        experience_data = [{"source": "experience", "data": "exemplar_match"}]
        return {"retrieved_data_graph": experience_data}
    
    def rrf_node(self, state: RetrievalGraph) -> dict:
        return {"ranking_score": {"rrf_score": [1,2,3]}}
    
    def score_fusion_node(self, state: RetrievalGraph) -> dict:
        return {"final_results": [{"rank": 1}, {"rank": 2}, {"rank": 3}]}
    

def create_retrieval_graph():
    # Pass your Pydantic class here
    graph = StateGraph(RetrievalGraph)
    nodes = RetrievalNodes()
    
    # FIX: Add query_router as a standard named node, not START
    graph.add_node('query_router', nodes.query_router_node)
    graph.add_node('preprocessing', nodes.preprocessing_node)
    graph.add_node('BM25_retrieval', nodes.BM25_retrieval_node)
    graph.add_node('embedding_retrieval', nodes.embedding_retrieval_node)
    graph.add_node('graph_retrieval', nodes.graph_retrieval_node)
    graph.add_node('ranking', nodes.ranking_node)
    graph.add_node('experience_retrieval', nodes.experience_retrieval_node)
    graph.add_node('rrf', nodes.rrf_node)
    graph.add_node('score_fusion', nodes.score_fusion_node)

    # FIX: Connect START to your first actual processing node
    graph.add_edge(START, 'query_router')
    graph.add_edge('query_router', 'preprocessing')
    
    # Fan-out parallel execution
    graph.add_edge('preprocessing', 'BM25_retrieval')
    graph.add_edge('preprocessing', 'embedding_retrieval')
    graph.add_edge('preprocessing', 'graph_retrieval')
    graph.add_edge('preprocessing', 'experience_retrieval')
    
    # Fan-in / Merge synchronization
    graph.add_edge('BM25_retrieval', 'ranking')
    graph.add_edge('embedding_retrieval', 'ranking')
    graph.add_edge('graph_retrieval', 'rrf')
    graph.add_edge('experience_retrieval', 'rrf')
    
    graph.add_edge('ranking', 'score_fusion')
    graph.add_edge('rrf', 'score_fusion')
    graph.add_edge('score_fusion', END)
    
    return graph.compile()

