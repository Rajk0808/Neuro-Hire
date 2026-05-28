"""
ChromaDB Retrieval Service
"""
from agents.Resume_Intelligence_agent.database.clients import chromaDB_client
from chromadb.errors import InvalidDimensionException
from CustomException import CustomException
import logging
logger = logging.getLogger(__name__)


def chromaDB_retrieval(query : str , collection_name : str, n_results : int = 5)-> dict:
    """
    ChromaDB Retrieval Service

    args:
        query (str): The query string to search for.
        collection_name (str): The name of the collection to search in.
        n_results (int): The number of results to return. Default is 5. 
    returns:
        dict: A dictionary containing the search results.

    """
    try:
        client = chromaDB_client()
        collection = client.get_or_create_collection(name=collection_name)
        results = collection.query(query_texts=[query], n_results=n_results)
        logger.info(f"Retrieved results for query: {query}")
        return results
    except Exception as e:
        logger.error(f"Error occurred while retrieving data from ChromaDB: {str(e)}")
        if isinstance(e, InvalidDimensionException):
            raise CustomException("The dimension of the query does not match the dimension of the collection.")
        raise CustomException(f"Error occurred while retrieving data from ChromaDB: {str(e)}")