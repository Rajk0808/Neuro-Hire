from opensearchpy import OpenSearch


def _get_client():
    client = OpenSearch(
        hosts=[{"host": "localhost", "port": 9200}],
        use_ssl=False,
        verify_certs=False
    )
    
    return client
