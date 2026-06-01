import chromadb

def chromaDB_client():
    return chromadb.HttpClient(host='localhost', port=8000)