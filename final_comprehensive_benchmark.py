import subprocess
import os
import time
import json
import requests
from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, HallucinationMetric
from deepeval.test_case import LLMTestCase
from deepeval.models.llms.ollama_model import OllamaModel
from golden_dataset import GOLDEN_DATASET
from dotenv import load_dotenv

load_dotenv()

# Select the model you want to run (Edit this for individual runs)
TARGET_MODEL = "gemma2:2b" 
MODELS = [
    "llama3.2:3b",
    "nemotron-mini:4b",
    "gemma2:2b",
    "meditron:7b",
    "biomistral:7b"
]

API_URL = "http://localhost:3000/query"
REPORT_DIR = "./benchmark_reports"
SERVER_CMD = ["/usr/local/bin/npm", "run", "dev"]
OLLAMA_PATH = "/usr/local/bin/ollama"

os.makedirs(REPORT_DIR, exist_ok=True)

def ensure_model_pulled(model):
    print(f"\n[SYSTEM] Ensuring model is ready: {model}...")
    subprocess.run([OLLAMA_PATH, "pull", model])

def calculate_lexical_change(text1, text2):
    """Measures how much the refined answer deviated from the original."""
    import difflib
    return difflib.SequenceMatcher(None, text1, text2).ratio()

def run_individual_bench(model_name):
    print(f"\n{'='*60}")
    print(f"SCIENTIFIC BENCHMARK: {model_name}")
    print(f"{'='*60}")
    
    ensure_model_pulled(model_name)
    
    # Start Server (Shared for all 5 queries of this model)
    env = os.environ.copy()
    env["CHAT_MODEL"] = model_name
    env["TSX_WATCH"] = "false"
    env["PATH"] = "/usr/local/bin:" + env.get("PATH", "")
    
    server_proc = subprocess.Popen(
        SERVER_CMD,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=os.getcwd()
    )

    # Wait for readiness
    is_ready = False
    start_wait = time.time()
    while time.time() - start_wait < 90:
        line = server_proc.stdout.readline()
        if "Healthcare RAG Backend running" in line:
            print(f"Server ready for {model_name}")
            is_ready = True
            break
    
    if not is_ready:
        print(f"Failed to start server for {model_name}")
        server_proc.terminate()
        return

    evaluator_model = OllamaModel(model=model_name)
    query_reports = []

    try:
        for i, entry in enumerate(GOLDEN_DATASET):
            print(f"\n[QUERY {i+1}] Processing: {entry['input'][:60]}...")
            
            # --- STEP 1: STANDARD RAG ---
            print(f"  -> Step 1/4: Executing Standard RAG...")
            start_std = time.time()
            resp_std = requests.post(API_URL, json={
                "question": entry['input'], "patientId": entry['patientId'], "skipPubMed": True
            }, timeout=300).json()
            lat_std = time.time() - start_std
            ans_std = resp_std.get("answer", "")
            
            tc_std = LLMTestCase(input=entry['input'], actual_output=ans_std, expected_output=entry['expected_output'], retrieval_context=entry['retrieval_context'], context=entry['retrieval_context'])
            mf_std = FaithfulnessMetric(threshold=0.7, model=evaluator_model)
            mf_std.measure(tc_std)
            mh_std = HallucinationMetric(threshold=0.7, model=evaluator_model)
            mh_std.measure(tc_std)
            
            print(f"     Standard Results: Latency: {lat_std:.2f}s | Faith: {mf_std.score:.2f} | Hallu: {mh_std.score:.2f}")

            # --- STEP 2: VERIFIED RAG (PUBMED) ---
            print(f"  -> Step 2/4: Executing Verified RAG...")
            start_ver = time.time()
            resp_ver = requests.post(API_URL, json={
                "question": entry['input'], "patientId": entry['patientId'], "skipPubMed": False
            }, timeout=300).json()
            lat_ver = time.time() - start_ver
            ans_ver = resp_ver.get("answer", "")
            ver_text = resp_ver.get("verification", "")
            sources = len(resp_ver.get("pubmedArticles", []))
            
            tc_ver = LLMTestCase(input=entry['input'], actual_output=ans_ver, expected_output=entry['expected_output'], retrieval_context=entry['retrieval_context'], context=entry['retrieval_context'])
            mf_ver = FaithfulnessMetric(threshold=0.7, model=evaluator_model)
            mf_ver.measure(tc_ver)
            mh_ver = HallucinationMetric(threshold=0.7, model=evaluator_model)
            mh_ver.measure(tc_ver)
            
            print(f"     Verified Results: Latency: {lat_ver:.2f}s | Faith: {mf_ver.score:.2f} | Hallu: {mh_ver.score:.2f} | Sources: {sources}")

            # --- STEP 3: ANALYZE DEVIATION ---
            lex_similarity = calculate_lexical_change(ans_std, ans_ver)
            change_impact = "Significant" if lex_similarity < 0.7 else "Moderate" if lex_similarity < 0.9 else "Minor"
            
            # Formulate Per-Query Report
            query_reports.append({
                "id": i+1,
                "input": entry['input'],
                "latency_std": lat_std, "latency_ver": lat_ver,
                "faith_std": mf_std.score, "faith_ver": mf_ver.score,
                "hallu_std": mh_std.score, "hallu_ver": mh_ver.score,
                "sources": sources,
                "change_impact": change_impact,
                "lex_similarity": lex_similarity,
                "ans_std": ans_std,
                "ans_ver": ans_ver,
                "ver_text": ver_text
            })

    finally:
        server_proc.terminate()
    
    generate_model_md_report(model_name, query_reports)
    return query_reports

def generate_model_md_report(model_name, reports):
    timestamp = int(time.time())
    report_path = f"{REPORT_DIR}/RESEARCH_REPORT_{model_name.replace(':', '_')}_{timestamp}.md"
    
    with open(report_path, "w") as f:
        f.write(f"# Scientific Research Report: {model_name}\n\n")
        f.write(f"**Objective**: Analyze model deviation and grounding quality shift through clinical RAG verification.\n\n")
        
        f.write("## Executive Metrics Summary\n")
        avg_lat_std = sum(r['latency_std'] for r in reports) / len(reports)
        avg_lat_ver = sum(r['latency_ver'] for r in reports) / len(reports)
        avg_faith_std = sum(r['faith_std'] for r in reports) / len(reports)
        avg_faith_ver = sum(r['faith_ver'] for r in reports) / len(reports)
        
        f.write(f"| Metric | Standard RAG | Verified RAG | Shift |\n")
        f.write(f"| :--- | :---: | :---: | :---: |\n")
        f.write(f"| **Avg Latency** | {avg_lat_std:.2f}s | {avg_lat_ver:.2f}s | {((avg_lat_ver-avg_lat_std)/avg_lat_std)*100:+.1f}% |\n")
        f.write(f"| **Avg Faithfulness** | {avg_faith_std:.2f} | {avg_faith_ver:.2f} | {(avg_faith_ver-avg_faith_std):+.2f} |\n")
        f.write(f"| **Total PubMed Citations** | 0 | {sum(r['sources'] for r in reports)} | - |\n\n")

        for r in reports:
            f.write(f"### Query {r['id']}: {r['input']}\n")
            f.write(f"**Verification Impact**: {r['change_impact']} (Lexical Similarity: {r['lex_similarity']:.2f})\n\n")
            
            f.write("| Feature | Standard | Verified | Delta |\n")
            f.write("| :--- | :--- | :--- | :--- |\n")
            f.write(f"| **Latency** | {r['latency_std']:.2f}s | {r['latency_ver']:.2f}s | {r['latency_ver']-r['latency_std']:+.2f}s |\n")
            f.write(f"| **Faithfulness** | {r['faith_std']:.2f} | {r['faith_ver']:.2f} | {r['faith_ver']-r['faith_std']:+.2f} |\n")
            f.write(f"| **Hallucination** | {r['hallu_std']:.2f} | {r['hallu_ver']:.2f} | {r['hallu_ver']-r['hallu_std']:+.2f} |\n\n")
            
            f.write("#### Clinical Deviation Analysis\n")
            if r['faith_ver'] > r['faith_std']:
                f.write("- **Positive Correction**: PubMed verification successfully improved the grounding of the clinical response.\n")
            elif r['faith_ver'] < r['faith_std']:
                f.write("- **Context Contamination**: External verification introduced conflicting or generalized info that reduced patient-specific faithfulness.\n")
            else:
                f.write("- **Stability**: Verification supported existing records without significant factual shift.\n")
            
            f.write("\n---\n")

    print(f"\n[COMPLETED] Research report generated at: {report_path}")

def generate_global_comparison_report(all_model_results):
    timestamp = int(time.time())
    global_report_path = f"{REPORT_DIR}/GLOBAL_COMPARISON_REPORT_{timestamp}.md"
    
    with open(global_report_path, "w") as f:
        f.write("# Global Clinical RAG Benchmark: Model Comparison\n\n")
        f.write("| Model | Avg Latency (Std) | Avg Latency (Ver) | Avg Faith (Std) | Avg Faith (Ver) | Hallu (Std) | Hallu (Ver) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        
        for data in all_model_results:
            model = data["model"]
            reports = data["reports"]
            
            avg_lat_std = sum(r['latency_std'] for r in reports) / len(reports)
            avg_lat_ver = sum(r['latency_ver'] for r in reports) / len(reports)
            avg_faith_std = sum(r['faith_std'] for r in reports) / len(reports)
            avg_faith_ver = sum(r['faith_ver'] for r in reports) / len(reports)
            avg_hallu_std = sum(r['hallu_std'] for r in reports) / len(reports)
            avg_hallu_ver = sum(r['hallu_ver'] for r in reports) / len(reports)
            
            f.write(f"| **{model}** | {avg_lat_std:.2f}s | {avg_lat_ver:.2f}s | {avg_faith_std:.2f} | {avg_faith_ver:.2f} | {avg_hallu_std:.2f} | {avg_hallu_ver:.2f} |\n")
            
        f.write("\n\n## Summary of Findings\n")
        f.write("This report compares the performance of five different LLMs across Standard and Verified RAG workflows. Verified RAG typically increases latency due to external PubMed searches but often improves clinical faithfulness and reduces hallucinations.\n")

    print(f"\n[GLOBAL REPORT] Comparison summary generated at: {global_report_path}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1].lower() == "all":
        print(f"Starting comprehensive benchmark for all models: {MODELS}")
        all_results = []
        for model in MODELS:
            try:
                reports = run_individual_bench(model)
                if reports:
                    all_results.append({"model": model, "reports": reports})
            except Exception as e:
                print(f"Error benchmarking model {model}: {e}")
        
        if all_results:
            generate_global_comparison_report(all_results)
    else:
        model = TARGET_MODEL
        if len(sys.argv) > 1:
            model = sys.argv[1]
        run_individual_bench(model)
