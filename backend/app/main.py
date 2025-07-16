from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat
from app.routes import analyze

app = FastAPI(
    title="Vid Query Backend",
    description="A minimal FastAPI service for RAG workflows",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify your extension's origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(analyze.router)

@app.get("/")
async def read_root():
    return {"message": "Hello, world!"}
