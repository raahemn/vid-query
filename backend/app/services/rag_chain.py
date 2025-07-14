from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama

# ✅ Define your prompt
prompt = PromptTemplate.from_template("Respond to the user normally like a professional and helpful assistant: {question}")

# ✅ Choose your LLM (example: a local Ollama model)
llm = Ollama(model="tinyllama")  # This is free, local

# ✅ Build the chain
chain = LLMChain(llm=llm, prompt=prompt)

# ✅ Your service function
def get_rag_response(question: str) -> str:
    result = chain.invoke({"question": question})
    return result["text"]
