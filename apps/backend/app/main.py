from fastapi import FastAPI
from api import v1_app 

app = FastAPI(title="NeuroHire API", version="1.0.0")

app.mount("/v1", v1_app)

@app.get("/")
def read_root():
    return {"message": "Welcome to the NeuroHire API!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
    