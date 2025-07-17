from fastapi import APIRouter
from pydantic import BaseModel
from app.models.schemas import AnalyzeRequest, AnalyzeResponse
from app.services.analyze_service import analyze_youtube_video
from app.services.analyze_service import video_vectorstores

router = APIRouter(
    prefix="/analyze",
    tags=["analyze"]
)

@router.get("/status/{video_id}", response_model=dict[str, bool])
async def get_analysis_status(video_id: str):
    if video_id in video_vectorstores:
        return {"analyzed": True}
    return {"analyzed": False}

@router.post("/", response_model=AnalyzeResponse)
async def analyze_endpoint(payload: AnalyzeRequest):
    print(f"Received payload in analyze endpoint: {payload}")
    reply = await analyze_youtube_video(payload.video_id)
    return {"reply": reply}
