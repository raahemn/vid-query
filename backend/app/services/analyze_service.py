from langchain.vectorstores import FAISS
from app.services.transcript_fetcher import fetch_youtube_transcript
from app.services.embedding_service import HFInferenceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

embedder = HFInferenceEmbeddings(
    model="sentence-transformers/all-MiniLM-L6-v2",
    token=HF_TOKEN
)

splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Will store this globally or in a cache/db later
video_vectorstores: dict[str, FAISS] = {}

async def analyze_youtube_video(video_id: str) -> str:
    # transcript = fetch_youtube_transcript(video_id)
    transcript = (
        "Max Taylor: Real quick, Max Taylor of Sports Direct here talking to Jamal Hadid. Let’s discuss your strong finish this afternoon, man. Congratulations, Jamal.\n"
        "Jamal Hadid: Thank you very much. [coughs]\n"
        "Max: What brought you back to this track? I understand you stayed away for a while.\n"
        "Jamal: [laughs] If you love racing and it’s in your bones, you can’t really stay away. It’s true that I haven’t been back for a few years. I was on a roll trying to discover new places. But now I’m back. It’s been incredible. The fans are-- Well, nothing beats the fans, right?\n"
        "Max: And now that you’re back again, is the track how you remember it?\n"
        "Jamal: Yeah, I think so. I think there were some spots where I was-- [laughs] But it was-\n"
        "Max: Awesome.\n"
        "Jamal: -crazy. Unbelievable, the people who would attempt this track, don’t you think?\n"
        "Max: Absolutely, and--\n"
        "Jamal: But I’m glad I came back, all the same. The weather is awesome, the people are great. Well, I have to say, though, the riders are fast this time of year. What are they putting into their bodies?\n"
        "[laughter]\n"
        "Max: Jamal, I think that’s opening a whole new can of worms there. We’ll need to book you for three hours if we’re going to talk about that.\n"
        "Jamal: [laughs]\n"
        "Max: Alright. Well, I think that’s it. Thanks a lot for talking to me, man. So glad to see you here again at West Oaks.\n"
    )  # For testing, replace with actual fetch
    
    if not transcript:
        return "❌ Could not fetch transcript."

    chunks = splitter.create_documents([transcript])
    if not chunks:
        return "❌ Transcript is empty or could not be processed."

    vectorstore = FAISS.from_documents(chunks, embedder)

    # Store in global dict (or replace with Redis / local file later)
    video_vectorstores['video_id'] = vectorstore

    return f"✅ Video {video_id} processed and vector store initialized."
