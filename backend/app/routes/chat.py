from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.services.rag_chain import get_rag_response
from app.models.schemas import ChatRequest, ChatResponse
from app.services.analyze_service import video_vectorstores
import os
from app.services.eval_service import evaluate_query
from dotenv import load_dotenv
load_dotenv()

# Find out if we need to evaluate RAG responses via the .env toggle
EVALUATE_RAG = os.getenv("EVALUATE_RAG", "false").lower() == "true"
os.makedirs("../evaluations", exist_ok=True)


router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest, background_tasks: BackgroundTasks):
    print("Payload received in chat endpoint:", payload)

    question = payload.message
    vectorstore = video_vectorstores.get(payload.video_id)
    reply = get_rag_response(payload.message, vectorstore)
    
    print("Reply generated:", reply)

    if EVALUATE_RAG and vectorstore:
        docs = vectorstore.similarity_search(question, k=3)
        context = "\n\n".join(doc.page_content for doc in docs)
        background_tasks.add_task(evaluate_query, question, reply, context)


    return {"reply": reply}
