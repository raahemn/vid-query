from fastapi import APIRouter
from pydantic import BaseModel
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analyze_service import analyze_youtube_video

router = APIRouter(
    prefix="/analyze",
    tags=["analyze"]
)


@router.post("/", response_model=AnalyzeResponse)
async def analyze_endpoint(payload: AnalyzeRequest):
    print(f"Received payload in analyze endpoint: {payload}")
    reply = await analyze_youtube_video(payload.video_id)
    return {"reply": reply}
