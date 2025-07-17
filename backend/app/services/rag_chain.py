from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from langchain.vectorstores import FAISS

# Set up the LLM
llm = Ollama(model="tinyllama")

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
    # Retrieve top k relevant chunks
    docs = vectorstore.similarity_search(question, k=k)
    context = "\n\n".join(doc.page_content for doc in docs)
    
    print("Context retrieved:", context)
    print("Question asked:", question)

    # Ask LLM with context
    result = qa_chain.invoke({"context": context, "question": question})
    return result["text"]
