"""
Ingestion Pipeline for Resume Intelligence Agent
it includes the following ingestion steps:
1. For Elastic Search: Ingesting resumes and job descriptions into an Elasticsearch index for efficient searching and retrieval.
2. For Vector Database: Ingesting resumes and job descriptions into a vector database (like Pinecone or Weaviate) for semantic search and similarity matching.
3. For Knowledge Graph: Ingesting structured data extracted from resumes and job descriptions into a knowledge graph (like Neo4j) for relationship mapping and advanced querying.
4. For Experience memory: Ingesting for Experience memory — exemplar matching (semantic experience memory + Conceptual exemplar learning)
"""
from langgraph.graph import StateGraph, START, END
from nltk.tokenize import word_tokenize
from apps.backend.app.agents.Resume_Intelligence_agent.services.ingestion_services.extractor.orchestrator import ResumeOrchestrator, ExtractionMode
from apps.backend.app.custom_llm.EmbeddingHuggingFace import QwenMultimodalEmbeddingFunction
from apps.backend.app.agents.Resume_Intelligence_agent.services.ingestion_services.extractor.run import text_extraction 
from apps.backend.app.agents.Resume_Intelligence_agent.database.clients.opensearch_client import _get_client
from apps.backend.app.agents.Resume_Intelligence_agent.database.clients.chromaDB_client import chromaDB_client 
from apps.backend.app.agents.Resume_Intelligence_agent.services.ingestion_services.StateGraph.IngestionGraph import IngestionGraph
from apps.backend.app.agents.Resume_Intelligence_agent.services.ingestion_services.modeling.neo4j_modeling import Neo4jModeling
from apps.backend.app.agents.Resume_Intelligence_agent.database.ops.Neo4j_insertion import insert_to_neo4j
import logging
import nltk

nltk.download('punkt')
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


class Ingestion:
    def __init__(self, mode: ExtractionMode = ExtractionMode.HYBRID):
        self.orchestrator = ResumeOrchestrator(mode=mode)
        self.__mode = mode
    
    def extract_text(self, StateGraph: IngestionGraph)-> IngestionGraph:
        """
        Invoke the ingestion pipeline for the given file path.
        Args:
            StateGraph: The state graph containing file paths and other configuration.
        Returns:
            IngestionGraph: The updated state graph with extracted text.
        """
        text = text_extraction(mode=self.__mode.value, workers=4, file_path=StateGraph.file_path)
        if isinstance(StateGraph, dict):
            StateGraph["text"] = text
        else:
            setattr(StateGraph, "text", text)
        return StateGraph
        
    def process_with_llm(self, StateGraph: IngestionGraph) -> IngestionGraph:
        """
        Process the extracted text using a language model to extract structured information.
        Args:
            StateGraph (IngestionGraph): The state graph containing the extracted text and other relevant information.
        Returns:
            IngestionGraph: The updated state graph with LLM response.
        """
        # Initialize llm_response if not present
        if isinstance(StateGraph, dict):
            StateGraph["llm_response"] = StateGraph.get("llm_response", {})
        else:
            StateGraph.llm_response = getattr(StateGraph, "llm_response", {})
            
        StateGraph = self.orchestrator.batch_process(StateGraph)
        return StateGraph
    
    def ingest_to_opensearch(self, StateGraph: IngestionGraph):
        """
        Ingest the extracted resume data into an OpenSearch index.
        Args:
            StateGraph (IngestionGraph): The state graph containing the extracted information from resumes.
        """
        try:
            _client = _get_client()
            
            # Handle both dict and object access
            index_name = StateGraph.get("job_req_id", "resumes") if isinstance(StateGraph, dict) else StateGraph.job_req_id
            llm_response = StateGraph.get("llm_response", {}) if isinstance(StateGraph, dict) else StateGraph.llm_response
           
            # Delete and recreate index to ensure correct schema
            if _client.indices.exists(index=index_name):
                _client.indices.delete(index=index_name)
                logging.info(f"Deleted existing index: {index_name}")
            
            _client.indices.create(index=index_name, body={
                "settings": {"index": {"number_of_shards": 1, "number_of_replicas": 0}},
                "mappings": {
                    "properties": {
                        "name": {"type": "text"},
                        "email": {"type": "keyword"},
                        "phones": {"type": "keyword"},
                        "skills": {"type": "nested", "properties": {"name": {"type": "text"},"category": {"type": "keyword"}, "proficiency": {"type": "keyword"}}},
                        "experience": {"type": "object"},
                        "education": {"type": "object"},
                        "summary": {"type": "text"}
                    }
                }
            })
            logging.info(f"Created index: {index_name}")
            
            count = 0
            for resume in llm_response.values():
                doc = resume.to_dict() if hasattr(resume, 'to_dict') else resume
                
                # Normalize skills field: convert single object to array for nested type
                if "skills" in doc and doc["skills"] is not None:
                    if isinstance(doc["skills"], dict):
                        # Single skill object - convert to list
                        doc["skills"] = [doc["skills"]]
                    elif isinstance(doc["skills"], list) and len(doc["skills"]) > 0 and isinstance(doc["skills"][0], dict):
                        # Already a list of objects - keep as is
                        pass
                    else:
                        # If it's not in expected format, set to empty list
                        doc["skills"] = []
                
                res = _client.index(index=index_name, body=doc, id=count, refresh=True)
                logging.info(f"Ingested document with ID: {res['_id']}")
                count += 1
        except Exception as e:
            logging.warning(f"OpenSearch ingestion failed: {e}")
        return StateGraph

    def ingest_to_vector_db(self, StateGraph: IngestionGraph):
        """
        Ingest the extracted resume data into a vector database for semantic search.
        Args:
            StateGraph (IngestionGraph): The state graph containing the extracted information from resumes.
        """
        try:
            client = chromaDB_client()
            # Handle both dict and object access
            text = StateGraph.get("text", {}) if isinstance(StateGraph, dict) else StateGraph.text
            chunk_size = StateGraph.get("chunk_size", 512) if isinstance(StateGraph, dict) else StateGraph.chunk_size
            chunk_overlap = StateGraph.get("chunk_overlap", 25) if isinstance(StateGraph, dict) else StateGraph.chunk_overlap
            index_name = StateGraph.get("job_req_id", "resumes") if isinstance(StateGraph, dict) else StateGraph.job_req_id
            
            chunks = []
            for key, text_content in text.items():
                # Handle both string and dict text entries
                if isinstance(text_content, dict):
                    text_str = text_content.get("text", "")
                else:
                    text_str = str(text_content)
                    
                tokens = word_tokenize(text_str)
                for i in range(0, len(tokens), chunk_size - chunk_overlap):
                    chunk = " ".join(tokens[i:i + chunk_size])
                    chunks.append({"text": chunk, "metadata": {"source": key}})
            
            # Get or create collection once
            embedding_func = QwenMultimodalEmbeddingFunction()
            try:
                collection = client.get_collection(index_name)
                logging.info(f"Collection {index_name} already exists in vector database.")
            except Exception:
                collection = client.create_collection(index_name, embedding_function=embedding_func)
                logging.info(f"Created collection {index_name}")
            
            # Ingest all chunks into vector database
            if chunks:
                documents = [chunk["text"] for chunk in chunks]
                ids = [f"{chunk['metadata']['source']}_{i}" for i, chunk in enumerate(chunks)]
                collection.add(documents=documents, ids=ids)
                logging.info(f"Ingested {len(chunks)} chunks into vector database")
        except Exception as e:
            logging.warning(f"Vector DB ingestion failed: {e}")
        return StateGraph

    def model_data(self, StateGraph: IngestionGraph) -> IngestionGraph:
        """
        Model the extracted data for better structuring and understanding.
        Args:
            StateGraph (IngestionGraph): The state graph containing the extracted information from resumes.
        Returns:
            IngestionGraph: The updated state graph with modeled data.
        """
        try:
            modeling = Neo4jModeling()
            StateGraph = modeling.model(StateGraph)
            logging.info("Modeled data (placeholder)")
        except Exception as e:
            logging.warning(f"Model data failed: {e}")
        return StateGraph
    

    def ingest_to_knowledge_graph(self, StateGraph: IngestionGraph):
        """
        Ingest the extracted resume data into a knowledge graph for relationship mapping.
        Args:
            StateGraph (IngestionGraph): The state graph containing the extracted information from resumes.
        """
        try:
            # Placeholder for knowledge graph ingestion logic (e.g., using Neo4j)
            logging.info("Ingested document into knowledge graph (placeholder)")
            inserter = insert_to_neo4j()
            StateGraph = inserter._invoke(StateGraph)
        except Exception as e:
            logging.warning(f"Knowledge graph ingestion failed: {e}")
        return StateGraph
    
    def merge_data(self, StateGraph: IngestionGraph):
        """
        Merge the extracted and modeled data into a unified format for downstream applications.
        Args:
            StateGraph (IngestionGraph): The state graph containing the extracted and modeled information from resumes.
        Returns:
            IngestionGraph: The updated state graph with merged data.
        """
        # Placeholder for data merging logic
        logging.info("Merged data (placeholder)")
        return StateGraph
    

def main():
    ingestion = Ingestion()
    graph = StateGraph(state_schema=IngestionGraph)
    graph.add_node("extract_node", ingestion.extract_text)
    graph.add_node("process_node", ingestion.process_with_llm)
    graph.add_node("ingest_opensearch_node", ingestion.ingest_to_opensearch)
    graph.add_node("ingest_vector_db_node", ingestion.ingest_to_vector_db)
    graph.add_node("model_node", ingestion.model_data)
    graph.add_node("ingest_knowledge_graph_node", ingestion.ingest_to_knowledge_graph)
    graph.add_node("merge_node", ingestion.merge_data)
    
    graph.add_edge(START, "extract_node")
    graph.add_edge("extract_node", "process_node")
    graph.add_edge("process_node", "ingest_opensearch_node")
    graph.add_edge("process_node", "ingest_vector_db_node")
    graph.add_edge("process_node", "model_node")
    graph.add_edge("model_node", "ingest_knowledge_graph_node")
    graph.add_edge("ingest_opensearch_node", "merge_node")
    graph.add_edge("ingest_vector_db_node", "merge_node")
    graph.add_edge("ingest_knowledge_graph_node", "merge_node")
    graph.add_edge("merge_node", END)
    
    return graph.compile()
