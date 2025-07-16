from fastapi import APIRouter
from pydantic import BaseModel
from app.models.schemas import ChatRequest, ChatResponse
from app.services.transcript_fetcher import fetch_youtube_transcript


router = APIRouter(
    prefix="/analyze",
    tags=["analyze"]
)

@router.post("/", response_model=ChatResponse)
async def analyze_endpoint(payload: ChatRequest):
    print("Payload received:", payload)
    transcript = fetch_youtube_transcript(payload.message)
    if not transcript:
        return {"reply": "Could not fetch transcript."}

    # Process the transcript with your RAG chain or any other logic
    reply = "Processed transcript: " + transcript
    return {"reply": reply}
