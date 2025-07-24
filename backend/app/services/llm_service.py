from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.outputs import ChatResult, ChatGeneration
from huggingface_hub import InferenceClient
from pydantic import PrivateAttr
from langchain_core.output_parsers import PydanticOutputParser

class HFChatModel(BaseChatModel):
    model: str
    provider: str
    token: str

    # Declare non-pydantic internal attributes
    _client: InferenceClient = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._client = InferenceClient(provider=self.provider, api_key=self.token)

    def _generate(self, messages, stop=None, **kwargs) -> ChatResult:
        hf_messages = []
        for m in messages:
            if isinstance(m, HumanMessage):
                hf_messages.append({"role": "user", "content": m.content})
            elif isinstance(m, AIMessage):
                hf_messages.append({"role": "assistant", "content": m.content})

        result = self._client.chat.completions.create(
            model=self.model,
            messages=hf_messages
        )

        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(content=result.choices[0].message.content)
                )
            ]
        )

    @property
    def _llm_type(self) -> str:
        return "custom_hf_chat"
