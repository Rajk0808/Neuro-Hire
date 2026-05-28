from agents.Resume_Intelligence_agent.database.clients.opensearch_client import _get_client
from agents.Resume_Intelligence_agent.database.clients.chromaDB_client import chromaDB_client   
from agents.Resume_Intelligence_agent.database.clients.Neo4j_client import _get_neo4j_client

chromadb_client = chromaDB_client()
neo4j_client = _get_neo4j_client()
opensearch_client = _get_client()

