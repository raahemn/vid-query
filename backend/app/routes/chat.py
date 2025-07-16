from fastapi import APIRouter
from pydantic import BaseModel
from app.services.rag_chain import get_rag_response
from app.models.schemas import ChatRequest, ChatResponse


router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    print("Payload received:", payload)
    reply = get_rag_response(payload.message)
    return {"reply": reply}
