from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.vectorstores import FAISS
from app.services.llm_service import HFChatModel
from langsmith import trace
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
You are a YouTube video assistant. You will receive the user's query about the video as well as the context from the video's transcript and part of the chat history. 
Use the context to answer the user's question. 

Chat History:
{chat_history}

Context:
{context}

Question:
{question}

Answer in a professional and concise manner, ensuring that the response is directly relevant to the question asked.
If the question has an ambiguity not addressed by the context, refer to the chat history or ask for clarification.
""")

# Chain that combines prompt + LLM
qa_chain = LLMChain(llm=llm, prompt=rag_prompt)

def get_rag_response(question: str, vectorstore: FAISS, k: int = 3, chat_history: list[dict] = []) -> str:
    with trace("RAGPipeline", inputs={"question": question}) as span:

        if not vectorstore:
            # result = qa_chain.invoke({"context": "There's no video content available but answer any generic questions.", "question": question})   # Can later allow general chats with LLM
            return "No video content available. Please analyze a video first."
        
        # Retrieve top k relevant chunks
        docs = vectorstore.similarity_search(question, k=k)
        context = "\n\n".join(doc.page_content for doc in docs)

        # Log the retrieved documents for tracing
        span.add_outputs({"retrieved_docs": [doc.page_content for doc in docs]})
        
        formatted_history = ""
        for msg in chat_history[-6:]:  # Limit to last 3 user+bot pairs
            role = "Human" if msg["sender"] == "user" else "AI"
            formatted_history += f"{role}: {msg['text']}\n"
        
        print("Context retrieved:", context)
        print("Question asked:", question)

        # Ask LLM with context
        result = qa_chain.invoke({"context": context, "question": question, "chat_history": formatted_history})

        # Log the final answer for tracing
        span.add_outputs({"answer": result["text"]})

        return result["text"]
