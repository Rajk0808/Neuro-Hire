"""
Neo4j_client.py

This module provides a client for connecting to a Neo4j graph database. It uses the official Neo4j Python driver to establish a connection and verify connectivity. The client is designed to be used as a singleton, ensuring that only one instance of the connection is created throughout the application.
"""

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable
from dotenv import load_dotenv
import logging
import os

logger = logging.getLogger(__name__)
load_dotenv()  

def _get_neo4j_client():
    """Create and return a Neo4j driver instance."""
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        driver.verify_connectivity()
        logger.info("Successfully connected to Neo4j database.")
        return driver
    except ServiceUnavailable:
        logger.error("Failed to connect to Neo4j database.")
        return None
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        return None