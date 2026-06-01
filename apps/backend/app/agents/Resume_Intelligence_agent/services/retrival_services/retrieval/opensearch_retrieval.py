from agents.Resume_Intelligence_agent.database.clients import opensearch_client
from opensearchpy.exceptions import NotFoundError
from CustomException import CustomException
import logging
logger = logging.getLogger(__name__)

def opensearch_retrieval(query: str, index_name: str, n_results: int = 5) -> list:

    client = opensearch_client()
    index_name = index_name
    
    # Construct a query that searches both nested and non-nested fields
    search_query = {
        "query": {
            "bool": {
                "should": [
                    # Search in nested skills field
                    {
                        "nested": {
                            "path": "skills",
                            "query": {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["skills.name", "skills.category"]
                                }
                            }
                        }
                    },
                    # Search in non-nested fields
                    {
                        "multi_match": {
                            "query": query,
                            "fields": ["summary", "job_title", "name"]
                        }
                    }
                ],
                "maximum_should_match": n_results
            }
        }
    }
    try:
        response = client.search(index=index_name, body=search_query, size=n_results)
        logger.info(f"Retrieved results for query: {query}")
    except Exception as e:
        logger.error(f"Error occurred while retrieving data from OpenSearch: {str(e)}")
        if isinstance(e, NotFoundError):
            raise CustomException(f"Index '{index_name}' not found in OpenSearch.")
        else:
            raise CustomException(f"Error during OpenSearch retrieval: {str(e)}")
    return response
