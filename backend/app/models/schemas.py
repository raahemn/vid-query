from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    video_id: str = None  

class ChatResponse(BaseModel):
    reply: str

class AnalyzeRequest(BaseModel):
    video_id: str
    message: str = None  # Optional message for analysis

class AnalyzeResponse(BaseModel):
    reply: str