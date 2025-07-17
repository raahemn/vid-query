from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from app.services.llm_service import HFChatModel
from dotenv import load_dotenv
import os 

# Load environment variables from .env file
load_dotenv()

llm = HFChatModel(
    model="mistralai/Mistral-7B-Instruct-v0.3",
    provider="together",
    token=os.environ["HF_TOKEN"]
)


# Define your RAG prompt
rag_prompt = PromptTemplate.from_template("""
You are a helpful assistant. Use the context below to answer the user's question.

Context:
{context}

Question:
{question}

Answer in a professional tone.
""")

# Chain that combines prompt + LLM
qa_chain = LLMChain(llm=llm, prompt=rag_prompt)

def get_rag_response(question: str, vectorstore: FAISS, k: int = 3) -> str:
    
    if not vectorstore:
        # result = qa_chain.invoke({"context": "There's no video content available but answer any generic questions.", "question": question})   # Can later allow general chats with LLM
        return "No video content available. Please analyze a video first."
    
    # Retrieve top k relevant chunks
    docs = vectorstore.similarity_search(question, k=k)
    context = "\n\n".join(doc.page_content for doc in docs)
    
    print("Context retrieved:", context)
    print("Question asked:", question)

    # Ask LLM with context
    result = qa_chain.invoke({"context": context, "question": question})
    return result["text"]
