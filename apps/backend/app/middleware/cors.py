from fastapi.middleware.cors import CORSMiddleware

def setup_cors(app, frontend_origins):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=frontend_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )