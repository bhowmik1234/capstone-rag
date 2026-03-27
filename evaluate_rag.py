import time
import requests
import json
import os
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, HallucinationMetric, ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase
from deepeval.models.llms.ollama_model import OllamaModel
from golden_dataset import GOLDEN_DATASET
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = "http://localhost:3000/query"
OLLAMA_MODEL = os.getenv("CHAT_MODEL", "llama3.2:1b")

# Initialize DeepEval with Ollama
custom_model = OllamaModel(model=OLLAMA_MODEL)

def run_evaluation():
    print(f"--- Starting Healthcare RAG Evaluation (Expanded Metrics) ---")
    print(f"Using Evaluation Model: {OLLAMA_MODEL}")
    print(f"Target API: {API_URL}\n")

    results = []

    for i, entry in enumerate(GOLDEN_DATASET):
        print(f"Query {i+1}/{len(GOLDEN_DATASET)}: {entry['input']}")
        
        # 1. Measure Response Time
        start_time = time.time()
        try:
            response = requests.post(API_URL, json={
                "question": entry['input'],
                "patientId": entry['patientId']
            }, timeout=120)
            response.raise_for_status()
            data = response.json()
            actual_output = data.get("answer", "No answer field found")
            latency = time.time() - start_time
        except Exception as e:
            print(f"  Error calling API: {e}")
            continue

        print(f"  Latency: {latency:.2f}s")

        # 2. Run DeepEval Metrics
        test_case = LLMTestCase(
            input=entry['input'],
            actual_output=actual_output,
            expected_output=entry['expected_output'],
            retrieval_context=entry['retrieval_context'],
            context=entry['retrieval_context']
        )

        # Initialize metrics
        metrics = [
            FaithfulnessMetric(threshold=0.7, model=custom_model),
            AnswerRelevancyMetric(threshold=0.7, model=custom_model),
            HallucinationMetric(threshold=0.7, model=custom_model),
            ContextualRelevancyMetric(threshold=0.7, model=custom_model)
        ]
        
        row_results = {"latency": latency}
        for metric in metrics:
            metric.measure(test_case)
            metric_name = metric.__class__.__name__.replace("Metric", "").lower()
            row_results[metric_name] = metric.score
            print(f"  {metric.__class__.__name__.replace('Metric', '')}: {metric.score:.2f}")
        
        row_results["success"] = all(m.is_successful() for m in metrics)
        results.append(row_results)
        print("-" * 40)

    # Summary report
    if not results:
        print("No results to report.")
        return

    print("\n--- Evaluation Summary ---")
    metrics_to_avg = ["latency", "faithfulness", "answerrelevancy", "hallucination", "contextualrelevancy"]
    summary = {m: sum(r.get(m, 0) for r in results) / len(results) for m in metrics_to_avg}
    
    for m, val in summary.items():
        unit = "s" if m == "latency" else ""
        print(f"Average {m.capitalize()}: {val:.2f}{unit}")

    success_rate = (sum(1 for r in results if r['success']) / len(results)) * 100
    print(f"Overall Success Rate: {success_rate:.1f}%")

if __name__ == "__main__":
    run_evaluation()

if __name__ == "__main__":
    run_evaluation()
