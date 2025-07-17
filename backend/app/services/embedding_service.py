from langchain.embeddings.base import Embeddings
from huggingface_hub import InferenceClient

class HFInferenceEmbeddings(Embeddings):
    def __init__(self, model: str, token: str):
        self.client = InferenceClient(model=model, token=token)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.client.feature_extraction(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self.client.feature_extraction(text)
