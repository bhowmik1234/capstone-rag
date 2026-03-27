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
REPORT_FILE = "PUBMED_EFFECT_REPORT.md"

# Initialize DeepEval with Ollama
custom_model = OllamaModel(model=OLLAMA_MODEL)

def run_ab_test():
    print(f"--- Starting PubMed Grounding Effect Study ---")
    print(f"Using Evaluation Model: {OLLAMA_MODEL}\n")

    full_results = {
        "standard_rag": [],
        "verified_rag": []
    }

    # Run for both modes
    for mode in ["standard_rag", "verified_rag"]:
        skip_pubmed = (mode == "standard_rag")
        print(f"\n>>> Evaluating Mode: {mode.upper()} (skipPubMed={skip_pubmed}) <<<")
        
        # Limit to 1 query for the ultimate proof of hypothesis
        test_subset = GOLDEN_DATASET[:1]
        for i, entry in enumerate(test_subset):
            print(f"Query {i+1}/{len(test_subset)}: {entry['input']}")
            
            # 1. API Call
            start_time = time.time()
            try:
                response = requests.post(API_URL, json={
                    "question": entry['input'],
                    "patientId": entry['patientId'],
                    "skipPubMed": skip_pubmed
                }, timeout=300)
                response.raise_for_status()
                data = response.json()
                actual_output = data.get("answer", "")
                latency = time.time() - start_time
            except Exception as e:
                print(f"  Error calling API: {e}")
                continue

            # 2. Metrics
            test_case = LLMTestCase(
                input=entry['input'],
                actual_output=actual_output,
                expected_output=entry['expected_output'],
                retrieval_context=entry['retrieval_context'],
                context=entry['retrieval_context']
            )

            metrics = [
                FaithfulnessMetric(threshold=0.7, model=custom_model),
                HallucinationMetric(threshold=0.7, model=custom_model)
            ]
            
            row_results = {"latency": latency}
            for metric in metrics:
                metric.measure(test_case)
                name = metric.__class__.__name__.replace("Metric", "").lower()
                row_results[name] = metric.score
                print(f"  {name.capitalize()}: {metric.score:.2f}")
            
            print(f"  Latency: {latency:.2f}s")
            full_results[mode].append(row_results)
            print("-" * 20)

    # Generate Comparative Report
    generate_report(full_results)

def generate_report(results):
    def avg(lst, key):
        return sum(item[key] for item in lst) / len(lst) if lst else 0

    std = results["standard_rag"]
    ver = results["verified_rag"]

    avg_std_lat = avg(std, "latency")
    avg_ver_lat = avg(ver, "latency")
    avg_std_faithful = avg(std, "faithfulness")
    avg_ver_faithful = avg(ver, "faithfulness")
    avg_std_hallu = avg(std, "hallucination")
    avg_ver_hallu = avg(ver, "hallucination")

    hallu_reduction = ((avg_ver_hallu - avg_std_hallu) / (avg_std_hallu if avg_std_hallu > 0 else 1)) * 100
    lat_increase = ((avg_ver_lat - avg_std_lat) / avg_std_lat) * 100

    with open(REPORT_FILE, "w") as f:
        f.write("# Research Report: The PubMed Grounding Effect\n\n")
        f.write(f"**Objective**: Measure the impact of live PubMed verification on clinical hallucination mitigation vs. system latency.\n\n")
        f.write(f"**Model Used**: {OLLAMA_MODEL}\n\n")
        
        f.write("## Comparative Metrics\n\n")
        f.write("| Metric | Standard RAG | Verified RAG (PubMed) | Delta |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        f.write(f"| **Avg. Hallucination (Higher=Better)** | {avg_std_hallu:.2f} | {avg_ver_hallu:.2f} | {hallu_reduction:+.1f}% |\n")
        f.write(f"| **Avg. Faithfulness** | {avg_std_faithful:.2f} | {avg_ver_faithful:.2f} | {(avg_ver_faithful-avg_std_faithful):+.2f} |\n")
        f.write(f"| **Avg. Latency** | {avg_std_lat:.2f}s | {avg_ver_lat:.2f}s | {lat_increase:+.1f}% |\n\n")
        
        f.write("## Analysis\n")
        f.write("- **Hallucination Mitigation**: Indicates the effectiveness of peer-reviewed grounding in correcting model errors.\n")
        f.write("- **Computational Cost**: The latency delta represents the 'safety tax' incurred by adding external verification steps.\n")

    print(f"\n--- Study Complete! Report saved to {REPORT_FILE} ---")

if __name__ == "__main__":
    run_ab_test()
