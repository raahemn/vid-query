from fastapi import APIRouter
from pydantic import BaseModel
from app.models.schemas import ChatRequest, ChatResponse
from app.services.analyze_service import analyze_youtube_video
router = APIRouter(
    prefix="/analyze",
    tags=["analyze"]
)


@router.post("/", response_model=ChatResponse)
async def analyze_endpoint(payload: ChatRequest):
    reply = await analyze_youtube_video(payload.message)
    return {"reply": reply}
