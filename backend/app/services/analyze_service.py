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

VECTORSTORE_DIR = "vectorstores"

async def analyze_youtube_video(video_id: str) -> str:
    if video_id in video_vectorstores:
        return f"Your video {video_id} has already been processed."

    vector_path = os.path.join(VECTORSTORE_DIR, video_id)
    
    if os.path.exists(vector_path):
        print(f"Loading existing vectorstore for video {video_id} from {vector_path}.")
        vectorstore = FAISS.load_local(vector_path, embedder, allow_dangerous_deserialization=True)
        video_vectorstores[video_id] = vectorstore
        return f"Your video {video_id} has been loaded from the existing vectorstore."
    
    transcript = fetch_youtube_transcript(video_id)
    
    if not transcript:
        return "Could not fetch transcript."

    chunks = splitter.create_documents([transcript])
    if not chunks:
        return "Transcript is empty or could not be processed."
    
    print(f"Processed {len(chunks)} chunks from transcript.")

    vectorstore = FAISS.from_documents(chunks, embedder)

    # Store in global dict (or replace with Redis / local file later)
    video_vectorstores[video_id] = vectorstore
    
    # Save to persistent storage
    os.makedirs(VECTORSTORE_DIR, exist_ok=True)
    vectorstore.save_local(vector_path)

    return f"Your video {video_id} has been processed and the vector store has been initialized!"
