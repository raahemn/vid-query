from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_chain import get_rag_response
from app.models.schemas import ChatRequest, ChatResponse
from app.services.analyze_service import video_vectorstores


router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    print("Payload received:", payload)
    video_id = "video_id"  # Assuming video_id is part of the payload
    reply = get_rag_response(payload.message, video_vectorstores.get(video_id))
    print("Reply generated:", reply)
    return {"reply": reply}
