from langchain.evaluation import load_evaluator
from app.services.rag_chain import llm  # reuse your existing LLM
from datetime import datetime
import json
import os

def evaluate_query(question: str, answer: str, retrieved_docs: str):
    """Run LangChain evaluators synchronously and save results to file."""
    context_eval = load_evaluator(
        "criteria",
        criteria={"relevance": "Does the retrieved context help answer the question?"},
        llm=llm
    )
    faithfulness_eval = load_evaluator(
        "criteria",
        criteria={"faithfulness": "Does the answer faithfully use only the retrieved context without hallucinating?"},
        llm=llm
    )

    context_score = context_eval.evaluate_strings(
        prediction=answer,
        input=question,
        reference=retrieved_docs,
    )
    faithfulness_score = faithfulness_eval.evaluate_strings(
        prediction=answer,
        input=question,
        reference=retrieved_docs,
    )

    evaluation_result = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer,
        "context_relevance": context_score,
        "faithfulness": faithfulness_score
    }

    os.makedirs("./evaluations", exist_ok=True)
    file_path = f'./evaluations/eval_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
    with open(file_path, "w") as f:
        json.dump(evaluation_result, f, indent=2)

    print(f"[Evaluation saved] {file_path}")
