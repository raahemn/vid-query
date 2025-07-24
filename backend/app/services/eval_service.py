from langchain.evaluation import load_evaluator
from app.services.rag_chain import llm  # reuse your existing LLM
from datetime import datetime
import json
import os
import re
from uuid import uuid4
from langsmith import evaluate, traceable
from langsmith.schemas import Example

# Import message types
try:
    from langchain_core.messages import HumanMessage
except ImportError:
    try:
        from langchain.schema import HumanMessage
    except ImportError:
        # Fallback for older versions
        class HumanMessage:
            def __init__(self, content):
                self.content = content


# Evaluate the response using Langchain evaluators
def langchain_evaluate_query(question: str, answer: str, retrieved_docs: str):
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
    file_path = f'./evaluations/langchain_eval_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.json'
    with open(file_path, "w") as f:
        json.dump(evaluation_result, f, indent=2)

    print(f"[Evaluation saved] {file_path}")


# Evaluate the response using LangSmith evaluators
@traceable(name="context_relevance")
def eval_context_relevance(inputs: dict, outputs: dict) -> dict:
    try:
        # Get answer from either outputs or inputs
        answer = outputs.get("answer") or inputs.get("answer", "")
        context = outputs.get("context") or inputs.get("context", "")
        question = inputs.get("question", "")
        
        prompt = (
            f"Question: {question}\n"
            f"Answer: {answer}\n"
            f"Context: {context}\n\n"
            "On a scale from 1–5, how well does the context help answer the question?\n"
            "You MUST respond with valid JSON in this exact format:\n"
            '{"score": <number between 1-5>, "explanation": "<your explanation>"}\n'
            "Example: {\"score\": 4, \"explanation\": \"The context provides most of the needed information\"}"
        )
        
        # Use the proper LangChain interface
        messages = [HumanMessage(content=prompt)]
        resp = llm._generate(messages)
        
        content = resp.generations[0].message.content
        print(f"LLM response for context relevance: {content}")
        
        # Try to parse JSON from the response
        json_match = re.search(r'\{[^}]*\}', content)
        if json_match:
            parsed = json.loads(json_match.group())
        else:
            # Fallback parsing if no JSON found
            parsed = {"score": 3, "explanation": content}
            
        return {"score": int(parsed["score"]), "comment": parsed.get("explanation", "")}
    except Exception as e:
        print(f"Error in context relevance evaluation: {e}")
        import traceback
        traceback.print_exc()
        return {"score": 1, "comment": f"Evaluation failed: {str(e)}"}

@traceable(name="faithfulness")
def eval_faithfulness(inputs: dict, outputs: dict) -> dict:
    try:
        answer = outputs.get("answer") or inputs.get("answer", "")
        context = inputs.get("context", "") or outputs.get("context", "")
        
        prompt = (
            f"Question: {inputs['question']}\n"
            f"Answer: {answer}\n"
            f"Context: {context}\n\n"
            "On a scale from 1–5, how faithfully does the answer rely *only* on that context (no hallucinations)?\n"
            "You MUST respond with valid JSON in this exact format:\n"
            '{"score": <number between 1-5>, "explanation": "<your explanation>"}\n'
            "Example: {\"score\": 3, \"explanation\": \"The answer mostly uses the context but adds some interpretation\"}"
        )
        
        # FIX: Use HumanMessage just like in the other evaluator
        messages = [HumanMessage(content=prompt)]
        resp = llm._generate(messages)
        
        content = resp.generations[0].message.content
        
        # FIX: Add robust JSON parsing
        json_match = re.search(r'\{[^}]*\}', content)
        if json_match:
            parsed = json.loads(json_match.group())
        else:
            parsed = {"score": 1, "explanation": "Failed to parse LLM response for faithfulness."}
            
        return {"score": int(parsed["score"]), "comment": parsed.get("explanation", "")}
    except Exception as e:
        print(f"Error in faithfulness evaluation: {e}")
        return {"score": 1, "comment": f"Evaluation failed: {str(e)}"}

@traceable
def dummy_app(inputs: dict) -> dict:
    # our evaluate() wrapper will see this as the "run" and then pass
    # the same inputs and our outputs dict into each evaluator above.
    # The inputs should contain question, context and we return answer, context
    return {
        "answer": inputs.get("answer", ""),  # This should come from inputs now
        "context": inputs.get("context", "")
    }

def langsmith_evaluate_query(question: str, answer: str, retrieved_docs: str):
    try:
        # Generate a UUID for this standalone example
        example = Example(
            id=uuid4(),
            inputs={"question": question, "context": retrieved_docs, "answer": answer},
            outputs={"answer": answer, "context": retrieved_docs},
        )

        results = evaluate(
            dummy_app,
            data=[example],
            evaluators=[eval_context_relevance, eval_faithfulness],
            experiment_prefix="rag-eval",
            upload_results=False,
            max_concurrency=1,
        )

        print("Results:", results)
    except Exception as e:
        print(f"Error during evaluation: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        return  # Exit early if evaluation fails
    # normalize & dump
    eval_record = {
        "timestamp": datetime.utcnow().isoformat(),
        "question": question,
        "answer": answer,
        "evaluations": [],
    }
    
    try:
        for run in results:
            if "evaluation_results" in run and "results" in run["evaluation_results"]:
                eval_results = run["evaluation_results"]["results"]
                for eval_result in eval_results:
                    if eval_result is None:
                        continue
                        
                    # Check if evaluation was successful
                    has_error = eval_result.extra and eval_result.extra.get("error", False) if eval_result.extra else False
                    
                    if not has_error and eval_result.score is not None:
                        # Successful evaluation with a score
                        score = max(1, min(5, eval_result.score))
                        eval_record["evaluations"].append({
                            "name": eval_result.key,
                            "score": score,
                            "comment": eval_result.comment or "",
                        })
                    elif eval_result.comment:
                        # Evaluation returned a comment but no score - try to extract score from comment
                        print(f"Parsing evaluation comment for '{eval_result.key}': {eval_result.comment}")
                        
                        # Try to extract JSON score from the comment
                        import re
                        json_match = re.search(r'\{[^}]*"score"[^}]*\}', eval_result.comment)
                        if json_match:
                            try:
                                parsed = json.loads(json_match.group())
                                score = max(1, min(5, int(parsed.get("score", 3))))
                                explanation = parsed.get("explanation", eval_result.comment)
                                eval_record["evaluations"].append({
                                    "name": eval_result.key,
                                    "score": score,
                                    "comment": explanation,
                                })
                            except (json.JSONDecodeError, ValueError) as e:
                                print(f"Failed to parse JSON from comment: {e}")
                                # Fallback: assign a default score and use the full comment
                                eval_record["evaluations"].append({
                                    "name": eval_result.key,
                                    "score": 3,  # Default middle score
                                    "comment": eval_result.comment,
                                })
                        else:
                            # No JSON found, but we have a comment - assign default score
                            eval_record["evaluations"].append({
                                "name": eval_result.key,
                                "score": 3,  # Default middle score
                                "comment": eval_result.comment,
                            })
                    else:
                        print(f"Evaluation failed for '{eval_result.key}': No score or comment available")
            else:
                print(f"No recognizable evaluation structure found in run: {run.keys()}")
    except Exception as e:
        print(f"Error parsing evaluation results: {e}")
        import traceback
        traceback.print_exc()

    try:
        os.makedirs("./evaluations", exist_ok=True)
        fp = f'./evaluations/langsmith_eval_{datetime.utcnow():%Y%m%d_%H%M%S}.json'
        with open(fp, "w") as f:
            json.dump(eval_record, f, indent=2, ensure_ascii=False)
        print(f"[LangSmith Evaluation saved] {fp}")
    except Exception as e:
        print(f"Error saving evaluation results: {e}")
        import traceback
        traceback.print_exc()
