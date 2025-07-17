from fastapi import APIRouter
from pydantic import BaseModel
from app.models.schemas import ChatRequest, ChatResponse
from app.services.transcript_fetcher import fetch_youtube_transcript
from langchain.text_splitter import RecursiveCharacterTextSplitter



router = APIRouter(
    prefix="/analyze",
    tags=["analyze"]
)

splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Adjust chunk size as needed
        chunk_overlap=200  # Adjust overlap as needed
    )

@router.post("/", response_model=ChatResponse)
async def analyze_endpoint(payload: ChatRequest):
    print("Payload received:", payload)
    transcript = fetch_youtube_transcript(payload.message)
    if not transcript:
        return {"reply": "Could not fetch transcript."}

    # Split the transcript into chunks if necessary
    chunks = splitter.create_documents([transcript])
    if not chunks:
        return {"reply": "Transcript is empty or could not be processed."}
    
    print("Number of chunks created:", len(chunks))

    # Generate the embeddings for the chunks


    # Process the transcript with your RAG chain or any other logic
    reply = "Processed transcript: " + transcript
    return {"reply": reply}
