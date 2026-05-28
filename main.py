"""from agents.Resume_Intelligence_agent.services.retrival_services.retrieval.chromadb_retrieval import chromaDB_retrieval

result = chromaDB_retrieval("Data Scientist", 'resumes_data_scientist', n_results=5)

print(result) # -> {'ids': [['john_12_0']], 'distances': [[1.9675028]], 'embeddings': None, 'metadatas': [[None]], 'documents': [["John Doe is a data scientist with 5 years of experience in machine learning and data analysis . He has worked on various projects involving natural language processing and computer vision . John holds a Master 's degree in Computer Science from XYZ University and has published several research papers in top-tier conferences . He is proficient in Python , R , and SQL , and has experience with cloud platforms such as AWS and Azure ."]], 'uris': None, 'data': None, 'included': ['metadatas', 'documents', 'distances']}
"""
"""
from agents.Resume_Intelligence_agent.services.ingestion_services.StateGraph.IngestionGraph import IngestionGraph
from agents.Resume_Intelligence_agent.pipelines.ingestion_pipeline import Ingestion
ingestion_pipeline = Ingestion()

data = IngestionGraph(
    text = {
        "raj_124" : { "text" : "Raj Kumar is a Data Scientist with 8 years of experience in full-stack development and cloud computing. He has expertise in Java, JavaScript, and Python, and has worked on various projects involving microservices architecture and containerization. Raj holds a Bachelor's degree in Computer Science from ABC University and has contributed to several open-source projects. He is proficient in AWS, Azure, and Google Cloud Platform, and has experience with DevOps practices and CI/CD pipelines."},
        "john_12" :  { "text" : "John Doe is a data scientist with 5 years of experience in machine learning and data analysis. He has worked on various projects involving natural language processing and computer vision. John holds a Master's degree in Computer Science from XYZ University and has published several research papers in top-tier conferences. He is proficient in Python, R, and SQL, and has experience with cloud platforms such as AWS and Azure."}},
    index_name = "resumes_data_scientist",
)

ingestion_pipeline.ingest_to_vector_db(data)
"""

from agents.Resume_Intelligence_agent.database.clients import neo4j_client

_client = neo4j_client

def run_query(query: str):
    "Runs query on Neo4j database using the provided driver."
    return _client.execute_query(query, database="neo4j")
    
    

query = f"MATCH (c:Candidate) WHERE c.name = 'Muhammad Ghulam Jillani' RETURN c.name AS name, c.contact_info AS contactinfo"
result = run_query(query)
print(result) 
