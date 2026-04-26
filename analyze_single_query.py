import time
import requests
import json
import os
import sys
from deepeval.metrics import FaithfulnessMetric, HallucinationMetric, ContextualRelevancyMetric
from deepeval.test_case import LLMTestCase
from deepeval.models.llms.ollama_model import OllamaModel
from golden_dataset import GOLDEN_DATASET
from dotenv import load_dotenv

load_dotenv()

# Configuration
API_URL = "http://localhost:3000/query"
OLLAMA_MODEL = os.getenv("CHAT_MODEL", "llama3.2:3b")
custom_model = OllamaModel(model=OLLAMA_MODEL)

def analyze_query(query_index=0):
    if query_index >= len(GOLDEN_DATASET):
        print(f"Error: Query index {query_index} out of range.")
        return

    entry = GOLDEN_DATASET[query_index]
    question = entry['input']
    patient_id = entry['patientId']
    expected = entry['expected_output']
    context = entry['retrieval_context']

    print(f"\n{'='*60}")
    print(f"RESEARCH DEMO: STEP-BY-STEP CLINICAL VERIFICATION")
    print(f"{'='*60}")
    print(f"QUESTION: {question}")
    print(f"PATIENT:  {patient_id}")
    print(f"{'-'*60}\n")

    # STEP 1: Baseline Generation (RAG Only)
    print("STEP 1: Generating Baseline Answer (Vector RAG Only)...")
    resp_std = requests.post(API_URL, json={
        "question": question,
        "patientId": patient_id,
        "skipPubMed": True
    }, timeout=300).json()
    
    baseline_output = resp_std.get("answer", "")
    print(f"\n[BASELINE ANSWER]:\n{baseline_output}\n")

    # Evaluate Baseline
    print("Measuring Baseline Metrics...")
    test_case_std = LLMTestCase(
        input=question,
        actual_output=baseline_output,
        expected_output=expected,
        retrieval_context=context,
        context=context
    )
    faith_std = FaithfulnessMetric(threshold=0.5, model=custom_model)
    hallu_std = HallucinationMetric(threshold=0.5, model=custom_model)
    rel_std = ContextualRelevancyMetric(threshold=0.5, model=custom_model)
    
    faith_std.measure(test_case_std)
    hallu_std.measure(test_case_std)
    rel_std.measure(test_case_std)
    
    score_f_std = faith_std.score
    score_h_std = hallu_std.score
    score_r_std = rel_std.score
    print(f"  > Baseline Faithfulness: {score_f_std:.2f}")
    print(f"  > Baseline Hallucination Score: {score_h_std:.2f} (Higher=Better)")
    print(f"  > Baseline Contextual Relevancy: {score_r_std:.2f}")

    print(f"\n{'-'*60}\n")

    # STEP 2: Refined Generation (PubMed Grounded)
    print("STEP 2: Generating Refined Answer (PubMed Verified)...")
    resp_ver = requests.post(API_URL, json={
        "question": question,
        "patientId": patient_id,
        "skipPubMed": False
    }, timeout=300).json()
    
    final_output = resp_ver.get("answer", "")
    verification = resp_ver.get("verification", "")
    articles = resp_ver.get("pubmedArticles", [])

    print(f"\n[PUBMED ARTICLES DISCOVERED]:")
    if articles:
        for i, art in enumerate(articles):
            print(f"  {i+1}. {art.get('title', 'No Title')[:80]}...")
    else:
        print("  No relevant external literature found.")
    
    print(f"\n[FINAL CLINICAL CONSULTATION REPORT]:\n")
    print(final_output)

    # Evaluate Final
    print("\nMeasuring Refined Metrics...")
    test_case_ver = LLMTestCase(
        input=question,
        actual_output=final_output,
        expected_output=expected,
        retrieval_context=context,
        context=context
    )
    faith_ver = FaithfulnessMetric(threshold=0.5, model=custom_model)
    hallu_ver = HallucinationMetric(threshold=0.5, model=custom_model)
    rel_ver = ContextualRelevancyMetric(threshold=0.5, model=custom_model)
    
    faith_ver.measure(test_case_ver)
    hallu_ver.measure(test_case_ver)
    rel_ver.measure(test_case_ver)
    
    score_f_ver = faith_ver.score
    score_h_ver = hallu_ver.score
    score_r_ver = rel_ver.score
    print(f"  > Refined Faithfulness: {score_f_ver:.2f}")
    print(f"  > Refined Hallucination Score: {score_h_ver:.2f}")
    print(f"  > Refined Contextual Relevancy: {score_r_ver:.2f}")

    print(f"\n{'='*60}")
    print(f"CLINICAL IMPROVEMENT SUMMARY")
    print(f"{'='*60}")
    print(f"Hallucination Delta:   {(score_h_ver - score_h_std):+.2f}")
    print(f"Faithfulness Delta:    {(score_f_ver - score_f_std):+.2f}")
    print(f"Relevancy Delta:       {(score_r_ver - score_r_std):+.2f}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    analyze_query(idx)
